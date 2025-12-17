from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.test_request import TestRequestStatus, TestRequestType


class TestRequestBase(BaseModel):
    title: str
    description: str
    azure_work_item_id: Optional[str] = Field(None, alias="azureWorkItemId")
    azure_work_item_url: Optional[str] = Field(None, alias="azureWorkItemUrl")
    additional_notes: Optional[str] = Field(None, alias="additionalNotes")
    type: TestRequestType = Field(TestRequestType.FRONT, alias="type")
    environment: Optional[str] = None
    has_auth: Optional[bool] = Field(False, alias="hasAuth")
    auth_type: Optional[str] = Field(None, alias="authType")
    auth_users: Optional[List[str]] = Field(None, alias="authUsers")
    front_plan: Optional[Dict[str, Any]] = Field(None, alias="frontPlan")
    api_plan: Optional[Dict[str, Any]] = Field(None, alias="apiPlan")

    class Config:
        populate_by_name = True


class TestRequestCreate(TestRequestBase):
    application_id: str = Field(..., alias="applicationId")


class TestRequestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TestRequestStatus] = None
    assignee_id: Optional[str] = Field(None, alias="assigneeId")
    azure_work_item_id: Optional[str] = Field(None, alias="azureWorkItemId")
    azure_work_item_url: Optional[str] = Field(None, alias="azureWorkItemUrl")
    additional_notes: Optional[str] = Field(None, alias="additionalNotes")
    generated_test_case_id: Optional[str] = Field(None, alias="generatedTestCaseId")
    type: Optional[TestRequestType] = Field(None, alias="type")
    environment: Optional[str] = None
    has_auth: Optional[bool] = Field(None, alias="hasAuth")
    auth_type: Optional[str] = Field(None, alias="authType")
    auth_users: Optional[List[str]] = Field(None, alias="authUsers")
    front_plan: Optional[Dict[str, Any]] = Field(None, alias="frontPlan")
    api_plan: Optional[Dict[str, Any]] = Field(None, alias="apiPlan")

    class Config:
        populate_by_name = True


class TestRequestStatusUpdate(BaseModel):
    status: TestRequestStatus
    assignee_id: Optional[str] = Field(None, alias="assigneeId")
    generated_test_case_id: Optional[str] = Field(None, alias="generatedTestCaseId")
    notes: Optional[str] = None

    class Config:
        populate_by_name = True


class GroupSimple(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


class ApplicationSimple(BaseModel):
    id: str
    name: str
    group: Optional[GroupSimple] = None

    class Config:
        from_attributes = True


class UserSimple(BaseModel):
    id: str
    first_name: str = Field(..., serialization_alias="firstName")
    last_name: str = Field(..., serialization_alias="lastName")
    email: str

    class Config:
        from_attributes = True
        populate_by_name = True


class TestCaseSimple(BaseModel):
    id: str
    name: str
    status: str

    class Config:
        from_attributes = True


class TestRequestResponse(BaseModel):
    id: str
    title: str
    description: str
    status: TestRequestStatus
    application_id: str = Field(..., serialization_alias="applicationId")
    requester_id: str = Field(..., serialization_alias="requesterId")
    assignee_id: Optional[str] = Field(None, serialization_alias="assigneeId")
    azure_work_item_id: Optional[str] = Field(None, serialization_alias="azureWorkItemId")
    azure_work_item_url: Optional[str] = Field(None, serialization_alias="azureWorkItemUrl")
    additional_notes: Optional[str] = Field(None, serialization_alias="additionalNotes")
    generated_test_case_id: Optional[str] = Field(None, serialization_alias="generatedTestCaseId")
    type: TestRequestType = Field(..., serialization_alias="type")
    environment: Optional[str] = Field(None, serialization_alias="environment")
    has_auth: bool = Field(..., serialization_alias="hasAuth")
    auth_type: Optional[str] = Field(None, serialization_alias="authType")
    auth_users: Optional[List[str]] = Field(None, serialization_alias="authUsers")
    front_plan: Optional[Dict[str, Any]] = Field(None, serialization_alias="frontPlan")
    api_plan: Optional[Dict[str, Any]] = Field(None, serialization_alias="apiPlan")
    created_at: datetime = Field(..., serialization_alias="createdAt")
    updated_at: datetime = Field(..., serialization_alias="updatedAt")
    application: Optional[ApplicationSimple] = None
    requester: Optional[UserSimple] = None
    assignee: Optional[UserSimple] = None
    generated_test_case: Optional[TestCaseSimple] = Field(None, serialization_alias="generatedTestCase")

    class Config:
        from_attributes = True
        populate_by_name = True


class TestRequestListResponse(BaseModel):
    success: bool = True
    data: List[TestRequestResponse]
    pagination: dict

