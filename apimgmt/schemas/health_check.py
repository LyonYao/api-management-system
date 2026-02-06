from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import uuid


class HealthCheckResultDTO(BaseModel):
    """健康检查结果DTO"""
    id: uuid.UUID
    endpoint_id: uuid.UUID
    status: str
    response_code: Optional[int]
    response_time_ms: Optional[int]
    error_message: Optional[str]
    checked_at: datetime
    
    class Config:
        from_attributes = True


class BatchHealthCheckRequest(BaseModel):
    """批量健康检查请求"""
    endpoint_ids: List[uuid.UUID] = Field(..., description="端点ID列表")


class BatchHealthCheckResponse(BaseModel):
    """批量健康检查响应"""
    results: List[HealthCheckResultDTO] = Field(default_factory=list, description="健康检查结果列表")
