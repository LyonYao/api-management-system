import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
# 从环境变量中读取过期时间，默认8小时（480分钟）
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """解码访问令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def refresh_access_token(token: str) -> Optional[str]:
    """刷新访问令牌"""
    payload = decode_access_token(token)
    if payload:
        # 检查token是否在过期前10分钟内，如果是则刷新
        exp = datetime.fromtimestamp(payload.get("exp"))
        time_until_expiry = exp - datetime.utcnow()
        
        # 如果token在10分钟内过期，则刷新
        if 0 < time_until_expiry.total_seconds() < 600:
            # 移除过期时间和签发时间
            payload.pop("exp", None)
            payload.pop("iat", None)
            # 创建新的token
            return create_access_token(payload)
    return None


def get_user_id_from_token(token: str) -> Optional[uuid.UUID]:
    """从令牌中获取用户ID"""
    payload = decode_access_token(token)
    if payload and "sub" in payload:
        try:
            return uuid.UUID(payload["sub"])
        except ValueError:
            return None
    return None


def get_username_from_token(token: str) -> Optional[str]:
    """从令牌中获取用户名"""
    payload = decode_access_token(token)
    if payload and "username" in payload:
        return payload["username"]
    return None
