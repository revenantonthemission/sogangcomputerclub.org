"""
FastAPI dependency injection functions.
"""
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from .repositories.memo import MemoRepository


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    Handles rollback on exceptions and cleanup.
    """
    session_factory = request.app.state.db_session_factory
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_memo_repository(session: AsyncSession = Depends(get_db)) -> MemoRepository:
    """Dependency for MemoRepository."""
    return MemoRepository(session)
