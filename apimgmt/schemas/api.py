from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List, Set
import uuid
import re

from apimgmt.enums.auth_type import AuthType


class CreateApiRequest(BaseModel):
    """创建API请求"""
    system_id: uuid.UUID = Field(..., description="系统ID")
    name: str = Field(..., min_length=1, max_length=255, description="API名称")
    description: Optional[str] = Field(None, description="API描述")
    auth_type: Optional[AuthType] = Field(None, description="认证类型")
    spec_link: Optional[str] = Field(None, max_length=500, description="API文档链接")
    department: Optional[str] = Field(None, max_length=255, description="部门")
    contact_name: Optional[str] = Field(None, max_length=255, description="联系人")
    contact_emails: List[str] = Field(..., min_items=1, max_items=10, description="联系邮箱列表")
    tags: Optional[Set[str]] = Field(None, description="标签列表")
    
    @field_validator('contact_emails')
    @classmethod
    def validate_emails(cls, v):
        """验证邮箱格式"""
        email_pattern = re.compile(r'^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
        for email in v:
            if not email_pattern.match(email):
                raise ValueError(f"Invalid email format: {email}")
        return v


class UpdateApiRequest(BaseModel):
    """更新API请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="API名称")
    description: Optional[str] = Field(None, description="API描述")
    auth_type: Optional[AuthType] = Field(None, description="认证类型")
    spec_link: Optional[str] = Field(None, max_length=500, description="API文档链接")
    department: Optional[str] = Field(None, max_length=255, description="部门")
    contact_name: Optional[str] = Field(None, max_length=255, description="联系人")
    contact_emails: Optional[List[str]] = Field(None, min_items=1, max_items=10, description="联系邮箱列表")
    tags: Optional[Set[str]] = Field(None, description="标签列表")
    
    @field_validator('contact_emails')
    @classmethod
    def validate_emails(cls, v):
        """验证邮箱格式"""
        if v:
            email_pattern = re.compile(r'^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
            for email in v:
                if not email_pattern.match(email):
                    raise ValueError(f"Invalid email format: {email}")
        return v


class ApiDTO(BaseModel):
    """API DTO"""
    id: uuid.UUID
    system_id: uuid.UUID
    system_name: Optional[str]
    name: str
    description: Optional[str]
    auth_type: Optional[AuthType]
    spec_link: Optional[str]
    department: Optional[str]
    contact_name: Optional[str]
    contact_emails: List[str]
    tags: Set[str]
    endpoints: List[dict] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
