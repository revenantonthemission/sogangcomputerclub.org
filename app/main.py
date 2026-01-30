"""
FastAPI Memo Application - Main Entry Point

This is the main application module that wires together all components:
- Database connections
- Redis cache
- Kafka messaging
- API routers
- Prometheus metrics

The original monolithic code has been refactored into modular components.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio
import redis.asyncio as redis
import sqlalchemy

from .config import get_settings
from .database import engine, async_session_factory, metadata
from .routers import health_router, memos_router
from .middleware import PrometheusMiddleware
from .rate_limit import RateLimitMiddleware
from .services.kafka import kafka_service
from .metrics import MEMO_COUNT, ACTIVE_CONNECTIONS

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


# --- Background Tasks ---
async def monitor_database_connections(app: FastAPI):
    """Background task to monitor database connection pool."""
    while True:
        try:
            if hasattr(app.state, 'db_engine'):
                pool = app.state.db_engine.sync_engine.pool
                ACTIVE_CONNECTIONS.set(pool.checkedout())
        except Exception as e:
            logger.error(f"Error monitoring DB connections: {e}")
        await asyncio.sleep(5)


# --- 애플리케이션 수명 주기 관리 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작 및 종료 수명 주기 관리."""
    logger.info("Lifespan: 애플리케이션 시작...")

    # 데이터베이스 리소스를 앱 상태(state)에 저장
    app.state.db_engine = engine
    app.state.db_session_factory = async_session_factory
    logger.info("Lifespan: 데이터베이스 리소스가 app.state에 저장되었습니다.")

    # 테이블 생성
    try:
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
        logger.info("Lifespan: 데이터베이스 테이블이 성공적으로 준비되었습니다.")
    except Exception as e:
        logger.error(f"Lifespan: 데이터베이스 테이블 생성 실패 - {e}")

    # Redis 초기화
    try:
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        await redis_client.ping()
        app.state.redis = redis_client
        logger.info("Lifespan: Redis 연결 성공")
    except Exception as e:
        logger.warning(f"Lifespan: Redis 연결 실패 - {e}")
        app.state.redis = None

    # Kafka Producer 초기화
    try:
        await kafka_service.start()
        app.state.kafka = kafka_service
        logger.info("Lifespan: Kafka Producer 연결 성공")
    except Exception as e:
        logger.warning(f"Lifespan: Kafka 연결 실패 - {e}")
        app.state.kafka = None

    logger.info("Lifespan: 모든 서비스가 성공적으로 시작되었습니다.")

    # MEMO_COUNT 메트릭 초기화
    try:
        async with engine.connect() as conn:
            result = await conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM memos"))
            count = result.scalar()
            MEMO_COUNT.set(count)
            logger.info(f"Lifespan: MEMO_COUNT initialized to {count}")
    except Exception as e:
        logger.warning(f"Lifespan: Failed to initialize MEMO_COUNT - {e}")

    # 백그라운드 작업 시작
    monitoring_task = asyncio.create_task(monitor_database_connections(app))

    yield

    # 종료
    logger.info("Lifespan: 애플리케이션 종료 중...")

    if app.state.kafka:
        await kafka_service.stop()
        logger.info("Lifespan: Kafka Producer 종료 완료")

    if app.state.redis:
        await app.state.redis.aclose()
        logger.info("Lifespan: Redis 연결 종료 완료")

    monitoring_task.cancel()
    try:
        await monitoring_task
    except asyncio.CancelledError:
        pass

    await app.state.db_engine.dispose()
    logger.info("Lifespan: 데이터베이스 연결 종료 완료")
    logger.info("Lifespan: 모든 서비스가 정상적으로 종료되었습니다.")


# --- FastAPI Application ---
app = FastAPI(
    title="Memo API",
    description="FastAPI, SQLAlchemy 2.0, Redis, Kafka를 사용한 비동기 메모 애플리케이션",
    version="1.0.0",
    lifespan=lifespan
)

# --- 미들웨어 ---
# 참고: 미들웨어는 역순으로 처리됩니다 (마지막에 추가된 것이 가장 먼저 실행됨)
app.add_middleware(PrometheusMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60, burst_size=10)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# --- Routers ---
app.include_router(health_router)
app.include_router(memos_router)


# --- 개발 서버 ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
