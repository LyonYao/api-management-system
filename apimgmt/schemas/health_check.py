from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid


class HealthCheckResultDTO(BaseModel):
    """健康检查结果DTO"""
    id: str
    batch_id: Optional[str] = None  # 批次ID
    api_id: Optional[str] = None
    system_id: Optional[str] = None
    status: str
    response_code: Optional[int]
    response_time_ms: Optional[int]
    error_message: Optional[str]
    environment: Optional[str] = None  # 健康检查的环境
    response_body: Optional[str] = None  # HTTP响应体
    response_headers: Optional[str] = None  # HTTP响应头
    request_url: Optional[str] = None  # 请求的URL
    request_details: Optional[str] = None  # 完整的HTTP请求记录
    checked_at: datetime
    
    class Config:
        from_attributes = True


class BatchHealthCheckRequest(BaseModel):
    """批量健康检查请求"""
    endpoint_ids: List[str] = Field(..., description="端点ID列表")


class SystemHealthCheckRequest(BaseModel):
    """系统健康检查请求"""
    system_id: str = Field(..., description="系统ID")


class EnvironmentHealthCheckRequest(BaseModel):
    """带环境参数的健康检查请求"""
    system_id: str = Field(..., description="系统ID")
    environment: str = Field(..., description="环境类型：dev、uat、prod")


class BatchHealthCheckResponse(BaseModel):
    """批量健康检查响应"""
    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="批次ID")
    results: List[HealthCheckResultDTO] = Field(default_factory=list, description="健康检查结果列表")
    total_count: int = Field(default=0, description="总检查数量")
    success_count: int = Field(default=0, description="成功数量")
    failure_count: int = Field(default=0, description="失败数量")


class HealthCheckBatchDTO(BaseModel):
    """健康检查批次DTO"""
    batch_id: str
    system_id: Optional[str]
    environment: Optional[str]
    total_count: int
    success_count: int
    failure_count: int
    checked_at: datetime


class HealthCheckBatchListResponse(BaseModel):
    """健康检查批次列表响应"""
    items: List[HealthCheckBatchDTO] = Field(..., description="健康检查批次列表")
    total: int = Field(..., description="总记录数")


class HealthCheckResultPageResponse(BaseModel):
    """健康检查结果分页响应"""
    items: List[HealthCheckResultDTO] = Field(..., description="健康检查结果列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    pages: int = Field(..., description="总页数")
