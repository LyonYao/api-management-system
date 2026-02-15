from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List, Set, Dict, Any, Union
import uuid
import re
import json

from apimgmt.enums.auth_type import AuthType
from apimgmt.enums.api_type import ApiType


class CreateApiRequest(BaseModel):
    """创建API请求"""
    system_id: str = Field(..., description="系统ID")
    name: str = Field(..., min_length=1, max_length=255, description="API名称")
    description: Optional[str] = Field(None, description="API描述")
    api_type: ApiType = Field(default=ApiType.SYSTEM, description="API类型")
    auth_type: Optional[AuthType] = Field(None, description="认证类型")
    spec_link: Optional[str] = Field(None, max_length=500, description="API文档链接")
    department: Optional[str] = Field(None, max_length=255, description="部门")
    contact_name: Optional[str] = Field(None, max_length=255, description="联系人")
    contact_emails: List[str] = Field(..., min_items=1, max_items=10, description="联系邮箱列表")
    tags: Optional[Set[str]] = Field(None, description="标签列表")
    dev_host: Optional[str] = Field(None, max_length=500, description="开发环境Host")
    uat_host: Optional[str] = Field(None, max_length=500, description="测试环境Host")
    prod_host: Optional[str] = Field(None, max_length=500, description="生产环境Host")
    health_check_path: Optional[str] = Field(None, description="健康检查路径")
    health_check_rule: Optional[str] = Field(None, description="健康检查规则")
    
    @field_validator('health_check_rule')
    @classmethod
    def validate_health_check_rule(cls, v):
        """验证健康检查规则是否为有效的字符串"""
        # 只接受字符串类型，不进行JSON解析
        if v and not isinstance(v, str):
            raise ValueError("health_check_rule must be a string")
        return v
    
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
    api_type: Optional[ApiType] = Field(None, description="API类型")
    auth_type: Optional[AuthType] = Field(None, description="认证类型")
    spec_link: Optional[str] = Field(None, max_length=500, description="API文档链接")
    department: Optional[str] = Field(None, max_length=255, description="部门")
    contact_name: Optional[str] = Field(None, max_length=255, description="联系人")
    contact_emails: Optional[List[str]] = Field(None, min_items=1, max_items=10, description="联系邮箱列表")
    tags: Optional[Set[str]] = Field(None, description="标签列表")
    dev_host: Optional[str] = Field(None, max_length=500, description="开发环境Host")
    uat_host: Optional[str] = Field(None, max_length=500, description="测试环境Host")
    prod_host: Optional[str] = Field(None, max_length=500, description="生产环境Host")
    health_check_path: Optional[str] = Field(None, description="健康检查路径")
    health_check_rule: Optional[str] = Field(None, description="健康检查规则")
    
    @field_validator('health_check_rule')
    @classmethod
    def validate_health_check_rule(cls, v):
        """验证健康检查规则是否为有效的字符串"""
        # 只接受字符串类型，不进行JSON解析
        if v and not isinstance(v, str):
            raise ValueError("health_check_rule must be a string")
        return v
    
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
    id: str
    system_id: str
    system_name: Optional[str]
    name: str
    description: Optional[str]
    api_type: ApiType
    auth_type: Optional[AuthType]
    spec_link: Optional[str]
    department: Optional[str]
    contact_name: Optional[str]
    contact_emails: List[str]
    tags: Set[str]
    dev_host: Optional[str]
    uat_host: Optional[str]
    prod_host: Optional[str]
    health_check_path: Optional[str]
    health_check_rule: Optional[str]
    endpoints: List[dict] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
