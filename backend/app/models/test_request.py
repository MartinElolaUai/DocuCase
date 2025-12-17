import enum
from datetime import datetime
from sqlalchemy import Column, String, Enum, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.id_generator import generate_cuid


class TestRequestStatus(str, enum.Enum):
    NEW = "NEW"
    IN_ANALYSIS = "IN_ANALYSIS"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    IMPLEMENTED = "IMPLEMENTED"



class TestRequestType(str, enum.Enum):
    FRONT = "FRONT"
    API = "API"


class TestRequest(Base):
    __tablename__ = "test_requests"

    id = Column(String, primary_key=True, default=generate_cuid)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    status = Column(Enum(TestRequestStatus), default=TestRequestStatus.NEW, nullable=False)
    type = Column(Enum(TestRequestType), default=TestRequestType.FRONT, nullable=False)
    environment = Column(String, nullable=True)
    has_auth = Column(Boolean, default=False, nullable=False)
    auth_type = Column(String, nullable=True)
    auth_users = Column(JSON, nullable=True)  # list of test users
    front_plan = Column(JSON, nullable=True)  # structured plan for frontend tests
    api_plan = Column(JSON, nullable=True)  # structured plan for API/microservice tests
    application_id = Column(String, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    requester_id = Column(String, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(String, ForeignKey("users.id"), nullable=True)

    # Azure references
    azure_work_item_id = Column(String, nullable=True)
    azure_work_item_url = Column(String, nullable=True)
    additional_notes = Column(Text, nullable=True)

    # Generated test case
    generated_test_case_id = Column(String, ForeignKey("test_cases.id"), unique=True, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    application = relationship("Application", back_populates="test_requests")
    requester = relationship("User", foreign_keys=[requester_id], back_populates="test_requests")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_requests")
    generated_test_case = relationship("TestCase", back_populates="test_requests")

    def __repr__(self):
        return f"<TestRequest {self.title}>"

