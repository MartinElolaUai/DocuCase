from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.feature import FeatureStatus


class FeatureBase(BaseModel):
    name: str
    description: Optional[str] = None
    feature_file_path: Optional[str] = Field(None, alias="featureFilePath")

    class Config:
        populate_by_name = True


class FeatureCreate(FeatureBase):
    application_id: str = Field(..., alias="applicationId")
    status: Optional[FeatureStatus] = FeatureStatus.PLANNED


class FeatureUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    feature_file_path: Optional[str] = Field(None, alias="featureFilePath")
    status: Optional[FeatureStatus] = None
    application_id: Optional[str] = Field(None, alias="applicationId")

    class Config:
        populate_by_name = True


class GroupSimple(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


class ApplicationWithGroup(BaseModel):
    id: str
    name: str
    group: Optional[GroupSimple] = None

    class Config:
        from_attributes = True


class FeatureCounts(BaseModel):
    test_cases: int = Field(..., alias="testCases")

    class Config:
        populate_by_name = True


class FeatureResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    feature_file_path: Optional[str] = Field(None, serialization_alias="featureFilePath")
    status: FeatureStatus
    application_id: str = Field(..., serialization_alias="applicationId")
    created_at: datetime = Field(..., serialization_alias="createdAt")
    updated_at: datetime = Field(..., serialization_alias="updatedAt")
    application: Optional[ApplicationWithGroup] = None
    _count: Optional[FeatureCounts] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class FeatureListResponse(BaseModel):
    success: bool = True
    data: List[FeatureResponse]
    pagination: dict

