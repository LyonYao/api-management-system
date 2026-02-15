from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class CreateSystemRequest(BaseModel):
    """创建系统请求"""
    name: str = Field(..., min_length=1, max_length=255, description="系统名称")
    system_code: str = Field(..., min_length=5, max_length=12, description="系统唯一编号，5-12位字符")
    description: Optional[str] = Field(None, max_length=200, description="系统描述，最多200字")


class UpdateSystemRequest(BaseModel):
    """更新系统请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="系统名称")
    description: Optional[str] = Field(None, max_length=200, description="系统描述，最多200字")


class SystemDTO(BaseModel):
    """系统DTO"""
    id: str
    name: str
    system_code: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
