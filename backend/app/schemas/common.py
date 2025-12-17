from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')


class PaginationResponse(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    success: bool
    message: str


class BaseResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T


class ListResponse(BaseModel, Generic[T]):
    success: bool = True
    data: List[T]
    pagination: Optional[PaginationResponse] = None

