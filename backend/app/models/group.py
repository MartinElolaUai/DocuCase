from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.id_generator import generate_cuid


class Group(Base):
    __tablename__ = "groups"

    id = Column(String, primary_key=True, default=generate_cuid)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    applications = relationship("Application", back_populates="group", cascade="all, delete-orphan")
    subscriptions = relationship("GroupSubscription", back_populates="group", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Group {self.name}>"


class GroupSubscription(Base):
    __tablename__ = "group_subscriptions"

    id = Column(String, primary_key=True, default=generate_cuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(String, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    group = relationship("Group", back_populates="subscriptions")

    __table_args__ = (
        UniqueConstraint("user_id", "group_id", name="uq_user_group"),
    )

    def __repr__(self):
        return f"<GroupSubscription user={self.user_id} group={self.group_id}>"

