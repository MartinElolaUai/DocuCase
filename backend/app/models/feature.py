import enum
from datetime import datetime
from sqlalchemy import Column, String, Enum, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.id_generator import generate_cuid


class FeatureStatus(str, enum.Enum):
    PLANNED = "PLANNED"
    IN_DEVELOPMENT = "IN_DEVELOPMENT"
    PRODUCTIVE = "PRODUCTIVE"


class Feature(Base):
    __tablename__ = "features"

    id = Column(String, primary_key=True, default=generate_cuid)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    feature_file_path = Column(String, nullable=True)
    status = Column(Enum(FeatureStatus), default=FeatureStatus.PLANNED, nullable=False)
    application_id = Column(String, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    application = relationship("Application", back_populates="features")
    test_cases = relationship("TestCase", back_populates="feature", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("name", "application_id", name="uq_feature_name_app"),
    )

    def __repr__(self):
        return f"<Feature {self.name}>"

