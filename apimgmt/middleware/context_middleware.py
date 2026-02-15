from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from apimgmt.utils.context import UserContext

class UserContextMiddleware(BaseHTTPMiddleware):
    """用户上下文中间件"""
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        try:
            # 处理请求
            response = await call_next(request)
            
            return response
        finally:
            # 重置用户上下文
            # 注意：这里的重置会在请求完全处理后执行，包括装饰器中的代码
            UserContext.reset()