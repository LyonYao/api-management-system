from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Dict, Any, Union
import uuid
import json


class CreateRelationshipRequest(BaseModel):
    """创建调用关系请求"""
    caller_type: str = Field(..., description="调用方类型")
    caller_id: str = Field(..., description="调用方ID")
    callee_type: str = Field(..., description="被调用方类型")
    callee_id: str = Field(..., description="被调用方ID")
    endpoint_id: Optional[str] = Field(None, description="端点ID")
    auth_type: Optional[str] = Field(None, description="认证类型")
    auth_config: Optional[Dict[str, Any]] = Field(None, description="认证配置")
    description: Optional[str] = Field(None, description="调用关系描述")


class UpdateRelationshipRequest(BaseModel):
    """更新调用关系请求"""
    caller_type: Optional[str] = Field(None, description="调用方类型")
    caller_id: Optional[str] = Field(None, description="调用方ID")
    callee_type: Optional[str] = Field(None, description="被调用方类型")
    callee_id: Optional[str] = Field(None, description="被调用方ID")
    endpoint_id: Optional[str] = Field(None, description="端点ID")
    auth_type: Optional[str] = Field(None, description="认证类型")
    auth_config: Optional[Dict[str, Any]] = Field(None, description="认证配置")
    description: Optional[str] = Field(None, description="调用关系描述")


class RelationshipDTO(BaseModel):
    """调用关系DTO"""
    id: str
    caller_type: str
    caller_id: str
    callee_type: str
    callee_id: str
    endpoint_id: Optional[str]
    auth_type: Optional[str]
    auth_config: Optional[Dict[str, Any]]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    @field_validator('auth_config', mode='before')
    @classmethod
    def parse_auth_config(cls, v: Union[Dict[str, Any], str, None]) -> Optional[Dict[str, Any]]:
        """解析auth_config字段，从字符串转换为字典"""
        if v is None:
            return None
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return None
    
    class Config:
        from_attributes = True
