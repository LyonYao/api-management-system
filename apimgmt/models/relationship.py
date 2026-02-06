from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
import uuid

from apimgmt.db.database import Base


class Relationship(Base):
    __tablename__ = "relationships"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    caller_type = Column(String(50), nullable=False)
    caller_id = Column(String(36), nullable=False)
    callee_type = Column(String(50), nullable=False)
    callee_id = Column(String(36), nullable=False)
    endpoint_id = Column(String(36), ForeignKey("endpoints.id"), nullable=True)
    auth_type = Column(String(50), nullable=True)
    auth_config = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
