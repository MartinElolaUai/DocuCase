from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.test_case import TestCaseType, TestCasePriority, TestCaseStatus, GherkinStepType


class GherkinSubStepCreate(BaseModel):
    text: str
    order: Optional[int] = None


class GherkinSubStepResponse(BaseModel):
    id: str
    text: str
    order: int

    class Config:
        from_attributes = True


class GherkinStepCreate(BaseModel):
    type: GherkinStepType
    text: str
    order: Optional[int] = None
    sub_steps: Optional[List[GherkinSubStepCreate]] = Field(None, alias="subSteps")

    class Config:
        populate_by_name = True


class GherkinStepResponse(BaseModel):
    id: str
    type: GherkinStepType
    text: str
    order: int
    sub_steps: Optional[List[GherkinSubStepResponse]] = Field(None, serialization_alias="subSteps")

    class Config:
        from_attributes = True
        populate_by_name = True


class TestCaseBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: Optional[TestCaseType] = TestCaseType.AUTOMATED
    priority: Optional[TestCasePriority] = TestCasePriority.MEDIUM
    azure_user_story_id: Optional[str] = Field(None, alias="azureUserStoryId")
    azure_user_story_url: Optional[str] = Field(None, alias="azureUserStoryUrl")
    azure_test_case_id: Optional[str] = Field(None, alias="azureTestCaseId")
    azure_test_case_url: Optional[str] = Field(None, alias="azureTestCaseUrl")
    tags: Optional[List[str]] = []
    scenario_name: Optional[str] = Field(None, alias="scenarioName")

    class Config:
        populate_by_name = True


class TestCaseCreate(TestCaseBase):
    feature_id: str = Field(..., alias="featureId")
    status: Optional[TestCaseStatus] = TestCaseStatus.PLANNED
    steps: Optional[List[GherkinStepCreate]] = None


class TestCaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[TestCaseType] = None
    priority: Optional[TestCasePriority] = None
    status: Optional[TestCaseStatus] = None
    feature_id: Optional[str] = Field(None, alias="featureId")
    azure_user_story_id: Optional[str] = Field(None, alias="azureUserStoryId")
    azure_user_story_url: Optional[str] = Field(None, alias="azureUserStoryUrl")
    azure_test_case_id: Optional[str] = Field(None, alias="azureTestCaseId")
    azure_test_case_url: Optional[str] = Field(None, alias="azureTestCaseUrl")
    tags: Optional[List[str]] = None
    scenario_name: Optional[str] = Field(None, alias="scenarioName")

    class Config:
        populate_by_name = True


class UpdateStepsRequest(BaseModel):
    steps: List[GherkinStepCreate]


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


class FeatureSimple(BaseModel):
    id: str
    name: str
    application: Optional[ApplicationSimple] = None

    class Config:
        from_attributes = True


class TestCaseCounts(BaseModel):
    steps: int
    pipeline_results: int = Field(..., alias="pipelineResults")

    class Config:
        populate_by_name = True


class PipelineSimple(BaseModel):
    id: str
    gitlab_pipeline_id: str = Field(..., serialization_alias="gitlabPipelineId")
    branch: str
    status: str

    class Config:
        from_attributes = True
        populate_by_name = True


class PipelineResultSimple(BaseModel):
    id: str
    status: str
    created_at: datetime = Field(..., serialization_alias="createdAt")
    pipeline: Optional[PipelineSimple] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class TestCaseResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    type: TestCaseType
    priority: TestCasePriority
    status: TestCaseStatus
    feature_id: str = Field(..., serialization_alias="featureId")
    azure_user_story_id: Optional[str] = Field(None, serialization_alias="azureUserStoryId")
    azure_user_story_url: Optional[str] = Field(None, serialization_alias="azureUserStoryUrl")
    azure_test_case_id: Optional[str] = Field(None, serialization_alias="azureTestCaseId")
    azure_test_case_url: Optional[str] = Field(None, serialization_alias="azureTestCaseUrl")
    tags: List[str] = []
    scenario_name: Optional[str] = Field(None, serialization_alias="scenarioName")
    created_at: datetime = Field(..., serialization_alias="createdAt")
    updated_at: datetime = Field(..., serialization_alias="updatedAt")
    feature: Optional[FeatureSimple] = None
    steps: Optional[List[GherkinStepResponse]] = None
    _count: Optional[TestCaseCounts] = None
    pipeline_results: Optional[List[PipelineResultSimple]] = Field(None, serialization_alias="pipelineResults")

    class Config:
        from_attributes = True
        populate_by_name = True


class TestCaseListResponse(BaseModel):
    success: bool = True
    data: List[TestCaseResponse]
    pagination: dict

