from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ApplicationSimple(BaseModel):
    id: str
    name: str
    status: Optional[str] = None

    class Config:
        from_attributes = True


class GroupCounts(BaseModel):
    applications: int
    subscriptions: int


class GroupResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(..., serialization_alias="createdAt")
    updated_at: datetime = Field(..., serialization_alias="updatedAt")
    applications: Optional[List[ApplicationSimple]] = None
    _count: Optional[GroupCounts] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class GroupListResponse(BaseModel):
    success: bool = True
    data: List[GroupResponse]
    pagination: dict


class UserSimple(BaseModel):
    id: str
    first_name: str = Field(..., serialization_alias="firstName")
    last_name: str = Field(..., serialization_alias="lastName")
    email: str

    class Config:
        from_attributes = True
        populate_by_name = True


class GroupSubscriptionResponse(BaseModel):
    id: str
    user: Optional[UserSimple] = None
    group: Optional[GroupResponse] = None
    created_at: datetime = Field(..., serialization_alias="createdAt")

    class Config:
        from_attributes = True
        populate_by_name = True

