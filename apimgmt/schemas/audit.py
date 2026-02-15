from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from apimgmt.models.audit import OperationType, ResourceType


class AuditLogBase(BaseModel):
    """审计日志基础模型"""
    operation_type: OperationType
    resource_type: ResourceType
    resource_id: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    before_data: Optional[Dict[str, Any]] = None
    after_data: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    """创建审计日志请求模型"""
    pass


class AuditLogDTO(BaseModel):
    """审计日志响应模型"""
    id: str
    operation_type: OperationType
    resource_type: ResourceType
    resource_id: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    before_data: Optional[Dict[str, Any]] = None
    after_data: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """审计日志列表响应模型"""
    total: int
    page: int
    page_size: int
    items: List[AuditLogDTO]


class AuditLogQueryParams(BaseModel):
    """审计日志查询参数模型"""
    operation_type: Optional[OperationType] = None
    resource_type: Optional[ResourceType] = None
    resource_id: Optional[str] = None
    user_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
