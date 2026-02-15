from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Dict, Any
import uuid
import json

from apimgmt.enums.endpoint_status import EndpointStatus


class CreateEndpointRequest(BaseModel):
    """创建端点请求"""
    api_id: str = Field(..., description="API ID")
    path: str = Field(..., min_length=1, description="端点路径")
    http_method: str = Field(..., description="HTTP方法")
    description: Optional[str] = Field(None, description="端点描述")
    status: EndpointStatus = Field(default=EndpointStatus.DEVELOPING, description="端点状态")
    online_date: Optional[datetime] = Field(None, description="上线日期")
    



class UpdateEndpointRequest(BaseModel):
    """更新端点请求"""
    path: Optional[str] = Field(None, description="端点路径")
    http_method: Optional[str] = Field(None, description="HTTP方法")
    description: Optional[str] = Field(None, description="端点描述")
    status: Optional[EndpointStatus] = Field(None, description="端点状态")
    online_date: Optional[datetime] = Field(None, description="上线日期")


class EndpointDTO(BaseModel):
    """端点DTO"""
    id: str
    api_id: str
    path: str
    http_method: str
    description: Optional[str]
    status: EndpointStatus
    online_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
