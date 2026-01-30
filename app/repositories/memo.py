"""
Memo Repository Implementation.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, or_
import sqlalchemy

from .base import BaseRepository
from ..models.memo import memos
from ..schemas.memo import MemoCreate, MemoUpdate


def escape_like(query: str) -> str:
    """Escape special LIKE pattern characters (%, _, \\) to prevent unexpected matching."""
    return query.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


class MemoRepository(BaseRepository[dict, int]):
    """
    SQLAlchemy implementation of the Memo repository.
    Works with SQLAlchemy Table objects, returning dictionary mappings.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> Optional[dict]:
        query = select(memos).where(memos.c.id == id)
        result = await self.session.execute(query)
        row = result.mappings().first()
        return dict(row) if row else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        query = select(memos).order_by(memos.c.id.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return [dict(row) for row in result.mappings().all()]

    async def create(self, obj_in: MemoCreate) -> dict:
        stmt = insert(memos).values(
            title=obj_in.title,
            content=obj_in.content,
            tags=obj_in.tags or [],
            priority=obj_in.priority,
            category=obj_in.category,
            is_archived=obj_in.is_archived,
            is_favorite=obj_in.is_favorite,
            author=obj_in.author
        ).returning(memos.c.id)
        
        result = await self.session.execute(stmt)
        created_id = result.scalar_one()
        await self.session.commit()
        
        # Helper to fetch the created object
        return await self.get(created_id)

    async def update(self, id: int, obj_in: MemoUpdate) -> Optional[dict]:
        # Check existence first
        curr = await self.get(id)
        if not curr:
            return None

        update_data = obj_in.model_dump(exclude_unset=True)
        if not update_data:
            return curr

        stmt = update(memos).where(memos.c.id == id).values(**update_data)
        await self.session.execute(stmt)
        await self.session.commit()
        
        return await self.get(id)

    async def delete(self, id: int) -> bool:
        # Check existence first
        curr = await self.get(id)
        if not curr:
            return False

        stmt = delete(memos).where(memos.c.id == id)
        await self.session.execute(stmt)
        await self.session.commit()
        return True
    
    async def search(self, query_str: str) -> List[dict]:
        search_query = f"%{escape_like(query_str)}%"
        stmt = select(memos).where(
            or_(
                memos.c.title.like(search_query, escape='\\'),
                memos.c.content.like(search_query, escape='\\')
            )
        ).order_by(memos.c.id.desc())
        
        result = await self.session.execute(stmt)
        return [dict(row) for row in result.mappings().all()]
