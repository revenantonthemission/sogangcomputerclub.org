import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import FastAPI, HTTPException, Depends, status, Request, Query
from pydantic import BaseModel, Field
from typing import List, AsyncGenerator, Optional
from datetime import datetime, date, timezone
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import redis.asyncio as redis
import json
import os
import asyncio
from aiokafka import AIOKafkaProducer

# --- 기본 설정 ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 서비스 설정 ---
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+aiomysql://memo_user:phoenix@localhost:3306/memo_app"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# Global services
redis_client = None
kafka_producer = None

metadata = sqlalchemy.MetaData()
memos = sqlalchemy.Table(
    "memos",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column("title", sqlalchemy.String(100), nullable=False),
    sqlalchemy.Column("content", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("tags", sqlalchemy.JSON, nullable=True, default=[]),
    sqlalchemy.Column("priority", sqlalchemy.Integer, nullable=False, default=2, server_default="2"),
    sqlalchemy.Column("category", sqlalchemy.String(50), nullable=True),
    sqlalchemy.Column("is_archived", sqlalchemy.Boolean, nullable=False, default=False, server_default="0"),
    sqlalchemy.Column("is_favorite", sqlalchemy.Boolean, nullable=False, default=False, server_default="0"),
    sqlalchemy.Column("author", sqlalchemy.String(100), nullable=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now()),
)

# --- 애플리케이션 생명주기 및 리소스 초기화 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Lifespan: 애플리케이션 시작...")

    # Database setup
    if "sqlite" in DATABASE_URL:
        engine = create_async_engine(DATABASE_URL, echo=True)
    else:
        engine = create_async_engine(
            DATABASE_URL,
            echo=True,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True
        )
    async_session_factory = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
    app.state.db_engine = engine
    app.state.db_session_factory = async_session_factory
    logger.info("Lifespan: 데이터베이스 리소스가 app.state에 저장되었습니다.")

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    logger.info("Lifespan: 데이터베이스 테이블이 성공적으로 준비되었습니다.")

    # Redis and Kafka setup
    global redis_client, kafka_producer
    try:
        redis_client = redis.from_url(REDIS_URL)
        await redis_client.ping()
        logger.info("Redis connected successfully")

        kafka_producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8')
        )
        await kafka_producer.start()
        logger.info("Kafka producer started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")

    yield

    logger.info("Lifespan: 애플리케이션 종료...")
    await app.state.db_engine.dispose()
    if redis_client:
        await redis_client.close()
    if kafka_producer:
        await kafka_producer.stop()
    logger.info("Lifespan: 모든 서비스가 정상적으로 종료되었습니다.")


# --- FastAPI 앱 인스턴스 생성 및 lifespan 연결 ---
app = FastAPI(
    title="Memo API",
    description="FastAPI, SQLAlchemy 2.0, Asyncio를 사용한 비동기 메모 애플리케이션",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic 스키마 정의 ---
class MemoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="메모 제목")
    content: str = Field(..., min_length=1, description="메모 내용")
    tags: Optional[List[str]] = Field(default=[], description="태그 목록")
    priority: int = Field(default=2, ge=1, le=4, description="우선순위 (1:낮음, 2:보통, 3:높음, 4:긴급)")
    category: Optional[str] = Field(None, max_length=50, description="카테고리")
    is_archived: bool = Field(default=False, description="아카이브 여부")
    is_favorite: bool = Field(default=False, description="즐겨찾기 여부")
    author: Optional[str] = Field(None, max_length=100, description="작성자")

class MemoCreate(MemoBase):
    pass

class MemoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="메모 제목 (선택 사항)")
    content: Optional[str] = Field(None, min_length=1, description="메모 내용 (선택 사항)")
    tags: Optional[List[str]] = Field(None, description="태그 목록 (선택 사항)")
    priority: Optional[int] = Field(None, ge=1, le=4, description="우선순위 (선택 사항)")
    category: Optional[str] = Field(None, max_length=50, description="카테고리 (선택 사항)")
    is_archived: Optional[bool] = Field(None, description="아카이브 여부 (선택 사항)")
    is_favorite: Optional[bool] = Field(None, description="즐겨찾기 여부 (선택 사항)")
    author: Optional[str] = Field(None, max_length=100, description="작성자 (선택 사항)")

class MemoInDB(MemoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# --- 데이터베이스 의존성 주입 ---
async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    session_factory = request.app.state.db_session_factory
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# --- API 엔드포인트 ---

@app.post("/memos/", response_model=MemoInDB, status_code=status.HTTP_201_CREATED, summary="새 메모 생성")
async def create_memo(memo: MemoCreate, db: AsyncSession = Depends(get_db)):
    try:
        query = memos.insert().values(
            title=memo.title,
            content=memo.content,
            tags=memo.tags or [],
            priority=memo.priority,
            category=memo.category,
            is_archived=memo.is_archived,
            is_favorite=memo.is_favorite,
            author=memo.author
        )
        result = await db.execute(query)
        await db.commit()

        created_id = result.lastrowid
        created_memo_query = memos.select().where(memos.c.id == created_id)
        created_memo = await db.execute(created_memo_query)
        memo_data = created_memo.mappings().one()

        # Kafka 이벤트 발행
        if kafka_producer:
            try:
                event_data = {
                    "event_type": "memo_created",
                    "memo_id": created_id,
                    "title": memo.title,
                    "author": memo.author,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                await asyncio.wait_for(
                    kafka_producer.send_and_wait("memo_events", event_data),
                    timeout=5.0
                )
                logger.info(f"Memo creation event sent for ID: {created_id}")
            except Exception as e:
                logger.warning(f"Failed to send Kafka event: {e}")

        return memo_data
    except Exception as e:
        await db.rollback()
        logger.error(f"메모 생성 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 생성에 실패했습니다.")


@app.get("/memos/", response_model=List[MemoInDB], summary="모든 메모 조회")
async def read_memos(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        query = memos.select().order_by(memos.c.id.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.mappings().all()
    except Exception as e:
        logger.error(f"메모 목록 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모를 불러오는 데 실패했습니다.")


@app.get("/memos/{memo_id}", response_model=MemoInDB, summary="특정 메모 조회")
async def read_memo(memo_id: int, db: AsyncSession = Depends(get_db)):
    try:
        # Redis 캐시에서 먼저 확인
        cache_key = f"memo:{memo_id}"
        if redis_client:
            try:
                cached_data = await redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                logger.warning(f"Redis get error for memo {memo_id}: {e}")

        query = memos.select().where(memos.c.id == memo_id)
        result = await db.execute(query)
        memo = result.mappings().first()
        if memo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")

        memo_dict = dict(memo)

        # Redis에 캐시 저장 (5분)
        if redis_client:
            try:
                await redis_client.setex(cache_key, 300, json.dumps(memo_dict, default=str))
            except Exception as e:
                logger.warning(f"Redis set error for memo {memo_id}: {e}")

        return memo_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"메모(ID:{memo_id}) 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 조회 중 오류가 발생했습니다.")


@app.put("/memos/{memo_id}", response_model=MemoInDB, summary="특정 메모 수정")
async def update_memo(memo_id: int, memo: MemoUpdate, db: AsyncSession = Depends(get_db)):
    try:
        existing_memo_query = memos.select().where(memos.c.id == memo_id)
        existing_memo = (await db.execute(existing_memo_query)).mappings().first()
        if existing_memo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")

        update_data = memo.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="수정할 내용이 없습니다.")

        query = memos.update().where(memos.c.id == memo_id).values(**update_data)
        await db.execute(query)
        await db.commit()

        updated_memo_query = memos.select().where(memos.c.id == memo_id)
        updated_memo = (await db.execute(updated_memo_query)).mappings().one()
        return updated_memo
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"메모(ID:{memo_id}) 수정 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 수정 중 오류가 발생했습니다.")


@app.delete("/memos/{memo_id}", status_code=status.HTTP_204_NO_CONTENT, summary="특정 메모 삭제")
async def delete_memo(memo_id: int, db: AsyncSession = Depends(get_db)):
    try:
        existing_memo_query = memos.select().where(memos.c.id == memo_id)
        existing_memo = (await db.execute(existing_memo_query)).mappings().first()
        if existing_memo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")

        delete_query = memos.delete().where(memos.c.id == memo_id)
        await db.execute(delete_query)
        await db.commit()

        # Redis 캐시 무효화
        if redis_client:
            try:
                await redis_client.delete(f"memo:{memo_id}")
            except Exception as e:
                logger.warning(f"Redis delete error for memo {memo_id}: {e}")

        # Kafka 이벤트 발행
        if kafka_producer:
            try:
                event_data = {
                    "event_type": "memo_deleted",
                    "memo_id": memo_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                await asyncio.wait_for(
                    kafka_producer.send_and_wait("memo_events", event_data),
                    timeout=5.0
                )
                logger.info(f"Memo deletion event sent for ID: {memo_id}")
            except Exception as e:
                logger.warning(f"Failed to send Kafka event: {e}")

        return None
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"메모(ID:{memo_id}) 삭제 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 삭제 중 오류가 발생했습니다.")


@app.get("/memos/search/", response_model=List[MemoInDB], summary="메모 검색")
async def search_memos(q: str = Query(..., min_length=1, description="검색어"), db: AsyncSession = Depends(get_db)):
    try:
        search_query = f"%{q}%"
        query = memos.select().where(
            sqlalchemy.or_(
                memos.c.title.like(search_query),
                memos.c.content.like(search_query)
            )
        ).order_by(memos.c.id.desc())
        
        result = await db.execute(query)
        return result.mappings().all()
    except Exception as e:
        logger.error(f"메모 검색 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 검색 중 오류가 발생했습니다.")


@app.get("/health", summary="헬스 체크")
async def health_check():
    """서비스 상태 확인"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {}
    }

    # Database 상태 확인
    try:
        engine = app.state.db_engine
        async with engine.begin() as conn:
            await conn.execute(sqlalchemy.text("SELECT 1"))
        health_status["services"]["database"] = "healthy"
    except Exception:
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "degraded"

    # Redis 상태 확인
    if redis_client:
        try:
            await redis_client.ping()
            health_status["services"]["redis"] = "healthy"
        except Exception:
            health_status["services"]["redis"] = "unhealthy"
            health_status["status"] = "degraded"
    else:
        health_status["services"]["redis"] = "not_configured"

    # Kafka 상태 확인
    if kafka_producer:
        try:
            await kafka_producer.client.metadata()
            health_status["services"]["kafka"] = "healthy"
        except Exception:
            health_status["services"]["kafka"] = "unhealthy"
            health_status["status"] = "degraded"
    else:
        health_status["services"]["kafka"] = "not_configured"

    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)