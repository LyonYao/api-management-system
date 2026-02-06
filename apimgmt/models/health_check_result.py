from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.sql import func
import uuid

from apimgmt.db.database import Base


class HealthCheckResult(Base):
    __tablename__ = "health_check_results"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id = Column(String(36), ForeignKey("endpoints.id"), nullable=False)
    status = Column(String(50), nullable=False)
    response_code = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
