"""
데이터베이스 연결 및 세션 관리.
"""
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .config import get_settings

# 모든 테이블을 위한 메타데이터
metadata = sqlalchemy.MetaData()

settings = get_settings()

# 커넥션 풀링을 포함한 비동기 엔진 생성
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True
)

# 데이터베이스 세션 생성을 위한 세션 팩토리
async_session_factory = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)
