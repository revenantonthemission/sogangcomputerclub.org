"""
Memo CRUD API endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request, Query
from typing import List
import logging

from ..schemas.memo import MemoCreate, MemoUpdate, MemoInDB
from ..dependencies import get_memo_repository
from ..repositories.memo import MemoRepository
from ..metrics import MEMO_COUNT

router = APIRouter(prefix="/memos", tags=["Memos"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=MemoInDB, status_code=status.HTTP_201_CREATED)
async def create_memo(
    memo: MemoCreate, 
    request: Request, 
    repo: MemoRepository = Depends(get_memo_repository)
):
    """Create a new memo."""
    try:
        new_memo = await repo.create(memo)
        MEMO_COUNT.inc()

        # Publish to Kafka (failure doesn't affect memo creation)
        if request.app.state.kafka:
            try:
                await request.app.state.kafka.publish(
                    "memo-created",
                    {"id": new_memo["id"], "title": memo.title, "action": "created"}
                )
            except Exception as e:
                logger.warning(f"Kafka 발행 실패: {e}")

        return new_memo
    except Exception as e:
        logger.error(f"메모 생성 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 생성에 실패했습니다.")


@router.get("/", response_model=List[MemoInDB])
async def read_memos(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=100, description="Maximum number of records to return"),
    repo: MemoRepository = Depends(get_memo_repository)
):
    """Get all memos."""
    try:
        return await repo.get_all(skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"메모 목록 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모를 불러오는 데 실패했습니다.")


@router.get("/search/", response_model=List[MemoInDB])
async def search_memos(
    q: str = Query(..., min_length=1, description="검색어"),
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=100, description="Maximum number of records to return"),
    repo: MemoRepository = Depends(get_memo_repository)
):
    """Search memos by keyword."""
    try:
        return await repo.search(q, skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"메모 검색 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 검색 중 오류가 발생했습니다.")


@router.get("/{memo_id}", response_model=MemoInDB)
async def read_memo(
    memo_id: int, 
    repo: MemoRepository = Depends(get_memo_repository)
):
    """Get a specific memo by ID."""
    try:
        memo = await repo.get(memo_id)
        if memo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")
        return memo
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"메모(ID:{memo_id}) 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 조회 중 오류가 발생했습니다.")


@router.put("/{memo_id}", response_model=MemoInDB)
async def update_memo(
    memo_id: int, 
    memo: MemoUpdate, 
    request: Request, 
    repo: MemoRepository = Depends(get_memo_repository)
):
    """Update a memo."""
    try:
        # Check if there's any data to update
        if not memo.model_dump(exclude_unset=True):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="수정할 내용이 없습니다.")

        updated_memo = await repo.update(memo_id, memo)
        if updated_memo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")

        # Publish to Kafka (failure doesn't affect memo update)
        if request.app.state.kafka:
            try:
                await request.app.state.kafka.publish(
                    "memo-updated",
                    {"id": memo_id, "action": "updated"}
                )
            except Exception as e:
                logger.warning(f"Kafka 발행 실패: {e}")

        return updated_memo
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"메모(ID:{memo_id}) 수정 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 수정 중 오류가 발생했습니다.")


@router.delete("/{memo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memo(
    memo_id: int, 
    request: Request, 
    repo: MemoRepository = Depends(get_memo_repository)
):
    """Delete a memo."""
    try:
        deleted = await repo.delete(memo_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")

        MEMO_COUNT.dec()

        # Publish to Kafka (failure doesn't affect memo deletion)
        if request.app.state.kafka:
            try:
                await request.app.state.kafka.publish(
                    "memo-deleted",
                    {"id": memo_id, "action": "deleted"}
                )
            except Exception as e:
                logger.warning(f"Kafka 발행 실패: {e}")

        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"메모(ID:{memo_id}) 삭제 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 삭제 중 오류가 발생했습니다.")
