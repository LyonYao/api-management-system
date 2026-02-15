from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, Index
from sqlalchemy.sql import func
import uuid

from apimgmt.db.database import Base


class HealthCheckResult(Base):
    __tablename__ = "health_check_results"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String(36), nullable=True)  # 新增：批次ID
    api_id = Column(String(36), nullable=True)
    system_id = Column(String(36), nullable=True)
    status = Column(String(50), nullable=False)
    response_code = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    environment = Column(String(10), nullable=True)  # 健康检查的环境
    response_body = Column(Text, nullable=True)  # 新增：HTTP响应体
    response_headers = Column(Text, nullable=True)  # 新增：HTTP响应头
    request_url = Column(Text, nullable=True)  # 新增：请求的URL
    request_details = Column(Text, nullable=True)  # 新增：完整的HTTP请求记录
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 索引
    __table_args__ = (
        Index('idx_health_check_results_api_id', 'api_id'),
        Index('idx_health_check_results_system_id', 'system_id'),
        Index('idx_health_check_results_checked_at', 'checked_at'),
    )
