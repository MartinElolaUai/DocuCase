from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole, UserStatus


class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")

    class Config:
        populate_by_name = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: Optional[UserRole] = UserRole.USER
    status: Optional[UserStatus] = UserStatus.ACTIVE


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    password: Optional[str] = None

    class Config:
        populate_by_name = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ChangePassword(BaseModel):
    current_password: str = Field(..., alias="currentPassword")
    new_password: str = Field(..., min_length=6, alias="newPassword")

    class Config:
        populate_by_name = True


class GroupInfo(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


class SubscriptionInfo(BaseModel):
    id: str
    group: GroupInfo

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str = Field(..., serialization_alias="firstName")
    last_name: str = Field(..., serialization_alias="lastName")
    role: UserRole
    status: Optional[UserStatus] = None
    created_at: Optional[datetime] = Field(None, serialization_alias="createdAt")
    updated_at: Optional[datetime] = Field(None, serialization_alias="updatedAt")
    subscriptions: Optional[List[SubscriptionInfo]] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class UserResponseSimple(BaseModel):
    id: str
    email: str
    first_name: str = Field(..., serialization_alias="firstName")
    last_name: str = Field(..., serialization_alias="lastName")

    class Config:
        from_attributes = True
        populate_by_name = True


class UserListResponse(BaseModel):
    success: bool = True
    data: List[UserResponse]
    pagination: dict


class LoginResponse(BaseModel):
    success: bool = True
    data: dict

