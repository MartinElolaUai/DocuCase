import enum
from datetime import datetime
from sqlalchemy import Column, String, Enum, DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.id_generator import generate_cuid


class TestCaseType(str, enum.Enum):
    MANUAL = "MANUAL"
    AUTOMATED = "AUTOMATED"


class TestCasePriority(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TestCaseStatus(str, enum.Enum):
    PLANNED = "PLANNED"
    IN_DEVELOPMENT = "IN_DEVELOPMENT"
    PRODUCTIVE = "PRODUCTIVE"
    OBSOLETE = "OBSOLETE"


class GherkinStepType(str, enum.Enum):
    GIVEN = "GIVEN"
    WHEN = "WHEN"
    THEN = "THEN"
    AND = "AND"
    BUT = "BUT"


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(String, primary_key=True, default=generate_cuid)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    type = Column(Enum(TestCaseType), default=TestCaseType.AUTOMATED, nullable=False)
    priority = Column(Enum(TestCasePriority), default=TestCasePriority.MEDIUM, nullable=False)
    status = Column(Enum(TestCaseStatus), default=TestCaseStatus.PLANNED, nullable=False)
    feature_id = Column(String, ForeignKey("features.id", ondelete="CASCADE"), nullable=False)

    # Azure DevOps
    azure_user_story_id = Column(String, nullable=True)
    azure_user_story_url = Column(String, nullable=True)
    azure_test_case_id = Column(String, nullable=True)
    azure_test_case_url = Column(String, nullable=True)

    # Metadata
    # En PostgreSQL se usaba ARRAY(String); para mejor compatibilidad entre motores usamos JSON
    tags = Column(JSON, default=list, nullable=False)
    scenario_name = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    feature = relationship("Feature", back_populates="test_cases")
    steps = relationship("GherkinStep", back_populates="test_case", cascade="all, delete-orphan", order_by="GherkinStep.order")
    pipeline_results = relationship("TestCasePipelineResult", back_populates="test_case", cascade="all, delete-orphan")
    test_requests = relationship("TestRequest", back_populates="generated_test_case")

    def __repr__(self):
        return f"<TestCase {self.name}>"


class GherkinStep(Base):
    __tablename__ = "gherkin_steps"

    id = Column(String, primary_key=True, default=generate_cuid)
    type = Column(Enum(GherkinStepType), nullable=False)
    text = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    test_case_id = Column(String, ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    test_case = relationship("TestCase", back_populates="steps")
    sub_steps = relationship("GherkinSubStep", back_populates="step", cascade="all, delete-orphan", order_by="GherkinSubStep.order")

    def __repr__(self):
        return f"<GherkinStep {self.type} {self.text[:30]}>"


class GherkinSubStep(Base):
    __tablename__ = "gherkin_sub_steps"

    id = Column(String, primary_key=True, default=generate_cuid)
    text = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    step_id = Column(String, ForeignKey("gherkin_steps.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    step = relationship("GherkinStep", back_populates="sub_steps")

    def __repr__(self):
        return f"<GherkinSubStep {self.text[:30]}>"

