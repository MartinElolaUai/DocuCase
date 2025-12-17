import enum
from datetime import datetime
from sqlalchemy import Column, String, Enum, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.id_generator import generate_cuid


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_cuid)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    subscriptions = relationship("GroupSubscription", back_populates="user", cascade="all, delete-orphan")
    test_requests = relationship("TestRequest", foreign_keys="TestRequest.requester_id", back_populates="requester")
    assigned_requests = relationship("TestRequest", foreign_keys="TestRequest.assignee_id", back_populates="assignee")

    def __repr__(self):
        return f"<User {self.email}>"

