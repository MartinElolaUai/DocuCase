import enum
from datetime import datetime
from sqlalchemy import Column, String, Enum, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.id_generator import generate_cuid


class ApplicationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    DISCONTINUED = "DISCONTINUED"


class Application(Base):
    __tablename__ = "applications"

    id = Column(String, primary_key=True, default=generate_cuid)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.ACTIVE, nullable=False)
    group_id = Column(String, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # GitLab Config
    gitlab_project_id = Column(String, nullable=True)
    gitlab_project_url = Column(String, nullable=True)
    
    # External IDs for mapping
    asset_id = Column(String, nullable=True, index=True)  # ID from external system
    bapp_id = Column(String, nullable=True, index=True)  # ID from disponibilidad system
    availability_url = Column(String, nullable=True)  # URL to disponibilidad dashboard

    # Relationships
    group = relationship("Group", back_populates="applications")
    features = relationship("Feature", back_populates="application", cascade="all, delete-orphan")
    test_requests = relationship("TestRequest", back_populates="application", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("name", "group_id", name="uq_app_name_group"),
    )

    def __repr__(self):
        return f"<Application {self.name}>"

