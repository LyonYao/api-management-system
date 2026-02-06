from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class CreateEndpointRequest(BaseModel):
    """创建端点请求"""
    api_id: uuid.UUID = Field(..., description="API ID")
    path: str = Field(..., min_length=1, description="端点路径")
    http_method: str = Field(..., description="HTTP方法")
    description: Optional[str] = Field(None, description="端点描述")


class UpdateEndpointRequest(BaseModel):
    """更新端点请求"""
    path: Optional[str] = Field(None, description="端点路径")
    http_method: Optional[str] = Field(None, description="HTTP方法")
    description: Optional[str] = Field(None, description="端点描述")


class EndpointDTO(BaseModel):
    """端点DTO"""
    id: uuid.UUID
    api_id: uuid.UUID
    path: str
    http_method: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
