from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.pipeline import PipelineStatus, TestCaseResultStatus


class TestResultInput(BaseModel):
    test_case_id: Optional[str] = Field(None, alias="testCaseId")
    scenario_name: Optional[str] = Field(None, alias="scenarioName")
    status: Optional[TestCaseResultStatus] = TestCaseResultStatus.NOT_EXECUTED
    details: Optional[str] = None
    log_url: Optional[str] = Field(None, alias="logUrl")
    duration: Optional[int] = None

    class Config:
        populate_by_name = True


class RegisterPipelineResult(BaseModel):
    gitlab_project_id: str = Field(..., alias="gitlabProjectId")
    gitlab_pipeline_id: str = Field(..., alias="gitlabPipelineId")
    branch: Optional[str] = "main"
    pipeline_status: Optional[PipelineStatus] = Field(None, alias="pipelineStatus")
    web_url: Optional[str] = Field(None, alias="webUrl")
    executed_at: Optional[datetime] = Field(None, alias="executedAt")
    test_results: Optional[List[TestResultInput]] = Field(None, alias="testResults")

    class Config:
        populate_by_name = True


class PipelineCounts(BaseModel):
    test_case_results: int = Field(..., alias="testCaseResults")

    class Config:
        populate_by_name = True


class PipelineResponse(BaseModel):
    id: str
    gitlab_project_id: str = Field(..., serialization_alias="gitlabProjectId")
    gitlab_pipeline_id: str = Field(..., serialization_alias="gitlabPipelineId")
    branch: str
    status: PipelineStatus
    web_url: Optional[str] = Field(None, serialization_alias="webUrl")
    executed_at: datetime = Field(..., serialization_alias="executedAt")
    created_at: datetime = Field(..., serialization_alias="createdAt")
    _count: Optional[PipelineCounts] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class PipelineListResponse(BaseModel):
    success: bool = True
    data: List[PipelineResponse]
    pagination: dict


class FeatureSimple(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


class TestCaseSimple(BaseModel):
    id: str
    name: str
    scenario_name: Optional[str] = Field(None, serialization_alias="scenarioName")
    feature: Optional[FeatureSimple] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class PipelineResultResponse(BaseModel):
    id: str
    test_case_id: str = Field(..., serialization_alias="testCaseId")
    pipeline_id: str = Field(..., serialization_alias="pipelineId")
    status: TestCaseResultStatus
    details: Optional[str] = None
    log_url: Optional[str] = Field(None, serialization_alias="logUrl")
    duration: Optional[int] = None
    created_at: datetime = Field(..., serialization_alias="createdAt")
    test_case: Optional[TestCaseSimple] = Field(None, serialization_alias="testCase")
    pipeline: Optional[PipelineResponse] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class PipelineResultSummary(BaseModel):
    total: int
    passed: int
    failed: int
    skipped: int
    not_executed: int = Field(..., alias="notExecuted")

    class Config:
        populate_by_name = True

