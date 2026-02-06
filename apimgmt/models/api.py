from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
import uuid

from apimgmt.db.database import Base


class Api(Base):
    __tablename__ = "apis"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    system_id = Column(String(36), ForeignKey("systems.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    auth_type = Column(String(50), nullable=True)
    spec_link = Column(String(500), nullable=True)
    department = Column(String(255), nullable=True)
    contact_name = Column(String(255), nullable=True)
    contact_emails = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
