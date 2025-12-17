from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON
from app.database import Base
from app.utils.id_generator import generate_cuid


class IntegrationConfig(Base):
    __tablename__ = "integration_configs"

    id = Column(String, primary_key=True, default=generate_cuid)
    type = Column(String, unique=True, nullable=False)  # 'azure_devops', 'gitlab', 'smtp'
    config = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<IntegrationConfig {self.type}>"


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(String, primary_key=True, default=generate_cuid)
    type = Column(String, nullable=False)  # 'request_new', 'request_status_change', 'pipeline_failed', etc.
    # En PostgreSQL se usaba ARRAY(String); para mejor compatibilidad usamos JSON
    recipients = Column(JSON, nullable=False)  # emails
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String, nullable=False)  # 'sent', 'failed', 'pending', 'skipped'
    error = Column(Text, nullable=True)
    extra_metadata = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<NotificationLog {self.type} {self.status}>"

