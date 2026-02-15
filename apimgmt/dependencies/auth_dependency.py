from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from apimgmt.db.database import get_db
from apimgmt.services.auth_service import AuthService
from apimgmt.repositories.user_repository import UserRepository
from apimgmt.exceptions import AuthenticationException
from apimgmt.utils.context import UserContext

security = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取当前用户（作为依赖）"""
    # 打印调试信息
    import logging
    logging.info("get_current_user called")
    
    user_repository = UserRepository(db)
    auth_service = AuthService(user_repository)
    
    try:
        user = auth_service.get_current_active_user(credentials.credentials)
        # 设置用户上下文
        ip_address = request.client.host if request.client else None
        UserContext.set_user_context(
            user_id=str(user.id),
            username=user.username,
            ip_address=ip_address
        )
        # 打印调试信息
        logging.info(f"User context set for user {user.username} (ID: {user.id})")
        # 验证用户上下文是否设置成功
        logging.info(f"UserContext.get_user_id(): {UserContext.get_user_id()}")
        logging.info(f"UserContext.get_username(): {UserContext.get_username()}")
        logging.info(f"UserContext.get_ip_address(): {UserContext.get_ip_address()}")
        return user
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_id(
    current_user = Depends(get_current_user)
):
    """获取当前用户ID（作为依赖）"""
    return current_user.id


def get_current_username(
    current_user = Depends(get_current_user)
):
    """获取当前用户名（作为依赖）"""
    return current_user.username
