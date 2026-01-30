import asyncio
import pytest
import os
from unittest.mock import MagicMock, AsyncMock, patch
import sys

# 1. 환경 변수 오버라이드 (앱 가져오기 전에 수행)
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "testvalidsecretkeythatislongenough"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["KAFKA_BOOTSTRAP_SERVERS"] = "localhost:9092"

# 2. app.database 가져오기 전에 create_async_engine 패치
# Postgres 전용 인자(pool_size 등)와 SQLite 간의 호환성 문제를 해결합니다.
from sqlalchemy.ext.asyncio import create_async_engine as real_create_async_engine
import sqlalchemy.ext.asyncio

def shim_create_async_engine(url, **kwargs):
    if "sqlite" in str(url):
        # SQLite에 유효하지 않은 인자 제거
        kwargs.pop("pool_size", None)
        kwargs.pop("max_overflow", None)
        kwargs.pop("pool_timeout", None)
        kwargs.pop("pool_recycle", None)
        kwargs.pop("pool_pre_ping", None)
    return real_create_async_engine(url, **kwargs)

sqlalchemy.ext.asyncio.create_async_engine = shim_create_async_engine

# 3. 앱 모듈 가져오기 & 서비스 모킹
from app.database import metadata

# sys.modules에서 Redis/Kafka 모킹
mock_kafka_module = MagicMock()
mock_kafka_service = AsyncMock()
mock_kafka_service.start = AsyncMock()
mock_kafka_service.stop = AsyncMock()
mock_kafka_service.publish = AsyncMock()
mock_kafka_service.is_connected = True
mock_kafka_module.kafka_service = mock_kafka_service
sys.modules["app.services.kafka"] = mock_kafka_module

from app.main import app

# 4. 표준 Fixture 정의
from httpx import AsyncClient, ASGITransport
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

@pytest.fixture(scope="session")
async def test_db_engine():
    # 앱의 전역 엔진 사용 (shim이 적용된 상태)
    from app.database import engine
    
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def client(test_db_engine):
    # Redis 모킹
    mock_redis = AsyncMock()
    
    # main의 redis 연결 패치
    with patch("app.main.redis.from_url", return_value=mock_redis):
        # app.state를 채우기 위해 lifespan 명시적 실행
        from app.main import app
        # lifespan 컨텍스트 트리거
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                yield ac
