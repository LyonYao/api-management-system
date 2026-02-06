from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
import uuid

from apimgmt.db.database import Base


class Endpoint(Base):
    __tablename__ = "endpoints"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    api_id = Column(String(36), ForeignKey("apis.id"), nullable=False)
    path = Column(String(500), nullable=False)
    http_method = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
