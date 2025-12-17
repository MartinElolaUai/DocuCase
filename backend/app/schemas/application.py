from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.application import ApplicationStatus


class ApplicationBase(BaseModel):
    name: str
    description: Optional[str] = None
    gitlab_project_id: Optional[str] = Field(None, alias="gitlabProjectId")
    gitlab_project_url: Optional[str] = Field(None, alias="gitlabProjectUrl")
    availability_url: Optional[str] = Field(None, alias="availabilityUrl")

    class Config:
        populate_by_name = True


class ApplicationCreate(ApplicationBase):
    group_id: str = Field(..., alias="groupId")


class ApplicationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    group_id: Optional[str] = Field(None, alias="groupId")
    gitlab_project_id: Optional[str] = Field(None, alias="gitlabProjectId")
    gitlab_project_url: Optional[str] = Field(None, alias="gitlabProjectUrl")
    availability_url: Optional[str] = Field(None, alias="availabilityUrl")

    class Config:
        populate_by_name = True


class GroupSimple(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


class ApplicationCounts(BaseModel):
    features: int
    test_requests: Optional[int] = Field(None, alias="testRequests")

    class Config:
        populate_by_name = True


class ApplicationResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    status: ApplicationStatus
    group_id: str = Field(..., serialization_alias="groupId")
    gitlab_project_id: Optional[str] = Field(None, serialization_alias="gitlabProjectId")
    gitlab_project_url: Optional[str] = Field(None, serialization_alias="gitlabProjectUrl")
    availability_url: Optional[str] = Field(None, serialization_alias="availabilityUrl")
    created_at: datetime = Field(..., serialization_alias="createdAt")
    updated_at: datetime = Field(..., serialization_alias="updatedAt")
    group: Optional[GroupSimple] = None
    _count: Optional[ApplicationCounts] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class ApplicationListResponse(BaseModel):
    success: bool = True
    data: List[ApplicationResponse]
    pagination: dict

