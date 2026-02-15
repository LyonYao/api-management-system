from pydantic import BaseModel, Field, field_validator
from typing import Optional
import uuid
from datetime import datetime


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=1, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="Bearer", description="令牌类型")
    expires_in: int = Field(default=1800, description="过期时间（秒）")
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    full_name: Optional[str] = Field(None, description="用户全名")


class TokenData(BaseModel):
    """令牌数据"""
    user_id: Optional[str] = None
    username: Optional[str] = None


class UserDTO(BaseModel):
    """用户DTO"""
    id: str
    username: str
    full_name: Optional[str]
    email: Optional[str]
    is_active: str
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
