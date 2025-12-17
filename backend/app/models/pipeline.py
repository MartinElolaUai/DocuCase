import enum
from datetime import datetime
from sqlalchemy import Column, String, Enum, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.id_generator import generate_cuid


class PipelineStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
    SKIPPED = "SKIPPED"


class TestCaseResultStatus(str, enum.Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    NOT_EXECUTED = "NOT_EXECUTED"


class GitlabPipeline(Base):
    __tablename__ = "gitlab_pipelines"

    id = Column(String, primary_key=True, default=generate_cuid)
    gitlab_project_id = Column(String, nullable=False, index=True)
    gitlab_pipeline_id = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    status = Column(Enum(PipelineStatus), default=PipelineStatus.PENDING, nullable=False)
    web_url = Column(String, nullable=True)
    executed_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    test_case_results = relationship("TestCasePipelineResult", back_populates="pipeline", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("gitlab_project_id", "gitlab_pipeline_id", name="uq_gitlab_pipeline"),
    )

    def __repr__(self):
        return f"<GitlabPipeline {self.gitlab_pipeline_id}>"


class TestCasePipelineResult(Base):
    __tablename__ = "test_case_pipeline_results"

    id = Column(String, primary_key=True, default=generate_cuid)
    test_case_id = Column(String, ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False)
    pipeline_id = Column(String, ForeignKey("gitlab_pipelines.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(TestCaseResultStatus), default=TestCaseResultStatus.NOT_EXECUTED, nullable=False)
    details = Column(Text, nullable=True)
    log_url = Column(String, nullable=True)
    duration = Column(Integer, nullable=True)  # in seconds
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    test_case = relationship("TestCase", back_populates="pipeline_results")
    pipeline = relationship("GitlabPipeline", back_populates="test_case_results")

    __table_args__ = (
        UniqueConstraint("test_case_id", "pipeline_id", name="uq_test_case_pipeline"),
    )

    def __repr__(self):
        return f"<TestCasePipelineResult test_case={self.test_case_id} pipeline={self.pipeline_id}>"

