from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from apimgmt.db.database import get_db
from apimgmt.schemas.auth import LoginRequest, LoginResponse, UserDTO
from apimgmt.services.auth_service import AuthService
from apimgmt.repositories.user_repository import UserRepository
from apimgmt.exceptions import AuthenticationException
from apimgmt.dependencies.auth_dependency import get_current_user

auth_router = APIRouter(tags=["auth"])
security = HTTPBearer()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """获取认证服务"""
    user_repository = UserRepository(db)
    return AuthService(user_repository)


@auth_router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(
    login_request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """用户登录接口"""
    try:
        return auth_service.login(login_request)
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@auth_router.get("/me", response_model=UserDTO, summary="获取当前用户信息")
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """获取当前登录用户信息"""
    try:
        user = auth_service.get_current_active_user(credentials.credentials)
        return UserDTO(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            is_active=user.is_active,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@auth_router.post("/register", response_model=UserDTO, summary="注册新用户")
async def register(
    username: str,
    password: str,
    full_name: str = None,
    email: str = None,
    auth_service: AuthService = Depends(get_auth_service),
    current_user = Depends(get_current_user)
):
    """注册新用户接口"""
    try:
        user = auth_service.create_user(username, password, full_name, email)
        return UserDTO(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            is_active=user.is_active,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
