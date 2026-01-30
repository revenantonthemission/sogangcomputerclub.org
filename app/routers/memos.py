"""
메모 CRUD API 엔드포인트.
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


async def publish_kafka_event(request: Request, topic: str, message: dict) -> None:
    """Kafka 이벤트 발행 (실패해도 메인 로직에 영향 없음)"""
    if request.app.state.kafka:
        try:
            await request.app.state.kafka.publish(topic, message)
        except Exception as e:
            logger.warning(f"Kafka 발행 실패: {e}")


@router.post("/", response_model=MemoInDB, status_code=status.HTTP_201_CREATED)
async def create_memo(
    memo: MemoCreate, 
    request: Request, 
    repo: MemoRepository = Depends(get_memo_repository)
):
    """새 메모를 생성합니다."""
    try:
        new_memo = await repo.create(memo)
        MEMO_COUNT.inc()

        # Kafka 발행
        await publish_kafka_event(request, "memo-created", {
            "id": new_memo["id"], "title": memo.title, "action": "created"
        })

        return new_memo
    except Exception as e:
        logger.error(f"메모 생성 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 생성에 실패했습니다.")


@router.get("/", response_model=List[MemoInDB])
async def read_memos(
    skip: int = Query(default=0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(default=100, ge=1, le=100, description="반환할 최대 레코드 수"),
    repo: MemoRepository = Depends(get_memo_repository)
):
    """모든 메모를 조회합니다."""
    try:
        return await repo.get_all(skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"메모 목록 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모를 불러오는 데 실패했습니다.")


@router.get("/search/", response_model=List[MemoInDB])
async def search_memos(
    q: str = Query(..., min_length=1, description="검색어"),
    skip: int = Query(default=0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(default=100, ge=1, le=100, description="반환할 최대 레코드 수"),
    repo: MemoRepository = Depends(get_memo_repository)
):
    """키워드로 메모를 검색합니다."""
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
    """ID로 특정 메모를 조회합니다."""
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
    """메모를 수정합니다."""
    try:
        # 수정할 데이터가 있는지 확인
        if not memo.model_dump(exclude_unset=True):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="수정할 내용이 없습니다.")

        updated_memo = await repo.update(memo_id, memo)
        if updated_memo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")

        # Kafka 발행
        await publish_kafka_event(request, "memo-updated", {
            "id": memo_id, "action": "updated"
        })

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
    """메모를 삭제합니다."""
    try:
        deleted = await repo.delete(memo_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")

        MEMO_COUNT.dec()

        # Kafka 발행
        await publish_kafka_event(request, "memo-deleted", {
            "id": memo_id, "action": "deleted"
        })

        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"메모(ID:{memo_id}) 삭제 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 삭제 중 오류가 발생했습니다.")
