"""
요청/응답 유효성 검사를 위한 Memo Pydantic 스키마.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class MemoBase(BaseModel):
    """공통 필드를 포함하는 기본 메모 스키마."""
    title: str = Field(..., min_length=1, max_length=100, description="메모 제목")
    content: str = Field(..., min_length=1, description="메모 내용")
    tags: Optional[List[str]] = Field(default=[], description="태그 목록")
    priority: int = Field(default=2, ge=1, le=4, description="우선순위 (1:낮음, 2:보통, 3:높음, 4:긴급)")
    category: Optional[str] = Field(None, max_length=50, description="카테고리")
    is_archived: bool = Field(default=False, description="아카이브 여부")
    is_favorite: bool = Field(default=False, description="즐겨찾기 여부")
    author: Optional[str] = Field(None, max_length=100, description="작성자")


class MemoCreate(MemoBase):
    """새 메모 생성을 위한 스키마."""
    pass


class MemoUpdate(BaseModel):
    """기존 메모 수정을 위한 스키마. 모든 필드는 선택 항목입니다."""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None
    priority: Optional[int] = Field(None, ge=1, le=4)
    category: Optional[str] = Field(None, max_length=50)
    is_archived: Optional[bool] = None
    is_favorite: Optional[bool] = None
    author: Optional[str] = Field(None, max_length=100)


class MemoInDB(MemoBase):
    """데이터베이스에 저장된 메모 스키마."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
