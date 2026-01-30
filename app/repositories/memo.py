"""
Memo 리포지토리 구현.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, or_
import sqlalchemy

from .base import BaseRepository
from ..models.memo import memos
from ..schemas.memo import MemoCreate, MemoUpdate


def escape_like(query: str) -> str:
    """LIKE 패턴 특수 문자(%, _, \\)를 이스케이프 처리하여 의도치 않은 매칭을 방지합니다."""
    return query.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


class MemoRepository(BaseRepository[dict, int]):
    """
    SQLAlchemy를 사용한 Memo 리포지토리 구현.
    SQLAlchemy Table 객체와 함께 작동하며, 딕셔너리 매핑을 반환합니다.
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
        
        # 생성된 객체를 조회하여 반환
        return await self.get(created_id)

    async def update(self, id: int, obj_in: MemoUpdate) -> Optional[dict]:
        # 존재 여부 확인
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
        # 존재 여부 확인
        curr = await self.get(id)
        if not curr:
            return False

        stmt = delete(memos).where(memos.c.id == id)
        await self.session.execute(stmt)
        await self.session.commit()
        return True
    
    async def search(self, query_str: str, skip: int = 0, limit: int = 100) -> List[dict]:
        """키워드로 메모를 검색하며 페이지네이션을 지원합니다."""
        search_query = f"%{escape_like(query_str)}%"
        stmt = select(memos).where(
            or_(
                memos.c.title.like(search_query, escape='\\'),
                memos.c.content.like(search_query, escape='\\')
            )
        ).order_by(memos.c.id.desc()).offset(skip).limit(limit)
        
        result = await self.session.execute(stmt)
        return [dict(row) for row in result.mappings().all()]
