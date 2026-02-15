from typing import Optional
import uuid
from datetime import datetime, timedelta
import bcrypt

from apimgmt.repositories.user_repository import UserRepository
from apimgmt.models.user import User
from apimgmt.schemas.auth import LoginRequest, LoginResponse, TokenData
from apimgmt.utils.jwt_util import create_access_token, get_user_id_from_token, decode_access_token
from apimgmt.exceptions import AuthenticationException, ResourceNotFoundException


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """验证用户"""
        user = self.user_repository.find_by_username(username)
        if not user:
            return None
        
        # 检查用户是否激活
        if user.is_active != "Y":
            return None
        
        # 验证密码
        if not self.verify_password(password, user.password_hash):
            return None
        
        return user
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
    
    def get_password_hash(self, password: str) -> str:
        """获取密码哈希值"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def login(self, login_request: LoginRequest) -> LoginResponse:
        """用户登录"""
        # 验证用户
        user = self.authenticate_user(login_request.username, login_request.password)
        if not user:
            raise AuthenticationException("用户名或密码错误")
        
        # 更新最后登录时间
        self.user_repository.update_last_login(str(user.id))
        
        # 创建访问令牌
        from apimgmt.utils.jwt_util import ACCESS_TOKEN_EXPIRE_MINUTES
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user.id,
            username=user.username,
            full_name=user.full_name
        )
    
    def get_current_user(self, token: str) -> Optional[User]:
        """获取当前用户"""
        user_id = get_user_id_from_token(token)
        if not user_id:
            return None
        
        # 确保传递字符串类型的user_id
        user = self.user_repository.find_by_id(str(user_id))
        if not user or user.is_active != "Y":
            return None
        
        return user
    
    def get_current_active_user(self, token: str) -> User:
        """获取当前活跃用户"""
        user = self.get_current_user(token)
        if not user:
            raise AuthenticationException("用户未认证或已禁用")
        return user
    
    def create_user(self, username: str, password: str, full_name: Optional[str] = None, email: Optional[str] = None) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        existing_user = self.user_repository.find_by_username(username)
        if existing_user:
            raise AuthenticationException("用户名已存在")
        
        # 检查邮箱是否已存在
        if email:
            existing_email = self.user_repository.find_by_email(email)
            if existing_email:
                raise AuthenticationException("邮箱已存在")
        
        # 创建新用户
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            password_hash=self.get_password_hash(password),
            full_name=full_name,
            email=email,
            is_active="Y",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return self.user_repository.create(user)
    
    def validate_token(self, token: str) -> Optional[TokenData]:
        """验证令牌"""
        payload = decode_access_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        username = payload.get("username")
        if not user_id:
            return None
        
        return TokenData(user_id=uuid.UUID(user_id), username=username)
