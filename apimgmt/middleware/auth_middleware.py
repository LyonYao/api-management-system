from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from typing import Optional

from apimgmt.utils.jwt_util import refresh_access_token


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件"""
    async def dispatch(self, request: Request, call_next):
        """处理请求和响应"""
        # 获取Authorization头
        auth_header = request.headers.get("Authorization")
        token = None
        
        # 提取token
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        
        # 处理token刷新
        if token:
            # 尝试刷新token
            new_token = refresh_access_token(token)
            if new_token:
                # 存储新token，后续在响应中返回
                request.state.new_token = new_token
        
        # 处理请求
        response = await call_next(request)
        
        # 如果有新token，在响应头中返回
        if hasattr(request.state, "new_token") and request.state.new_token:
            response.headers["X-Refreshed-Token"] = request.state.new_token
            response.headers["X-Token-Type"] = "Bearer"
        
        return response
