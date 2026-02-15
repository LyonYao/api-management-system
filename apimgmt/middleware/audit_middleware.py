from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import json
import time
from typing import Optional

from apimgmt.db.database import SessionLocal
from apimgmt.services.audit_service import AuditLogService
from apimgmt.repositories.audit_repository import AuditLogRepository
from apimgmt.models.audit import OperationType, ResourceType
from apimgmt.utils.jwt_util import decode_access_token
from apimgmt.utils.logger import audit_logger

class AuditMiddleware(BaseHTTPMiddleware):
    """审计中间件
    
    用于自动记录所有HTTP请求的审计日志，无需手动在每个路由中添加审计日志代码。
    """
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # 开始时间
        start_time = time.time()
        
        # 提取请求信息
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else None
        
        # 跳过OPTIONS请求，避免预检请求被审计中间件处理
        if method == 'OPTIONS':
            response = await call_next(request)
            return response
        
        # 跳过对审计日志API本身的记录，避免递归调用
        if '/audit/' in path:
            response = await call_next(request)
            return response
        
        # 对于登录请求，直接执行，不记录审计日志
        if '/auth/login' in path:
            response = await call_next(request)
            return response
        
        # 提取用户信息
        user_id = None
        username = None
        
        # 从Authorization头中提取token
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = decode_access_token(token)
                user_id = payload.get('sub')
                username = payload.get('username')
            except Exception as e:
                audit_logger.error(f"Failed to extract user info: {str(e)}")
        
        # 提取请求体（用于记录审计日志）
        request_body = None
        response = None
        
        # 直接执行请求
        response = await call_next(request)
        
        # 注意：在FastAPI中，请求体只能被读取一次
        # 为了避免消耗请求体，我们需要使用一种特殊的方法
        # 这里我们使用一种更简单的方法，直接从请求中获取一些信息
        # 但更好的方法是在路由处理函数中直接记录审计日志
        # 或者使用依赖注入来获取请求体
        
        # 由于我们不能在中间件中直接获取请求体而不消耗它
        # 我们需要修改路由处理函数来记录审计日志
        # 但为了保持中间件的通用性，我们可以尝试从request对象中获取一些信息
        # 注意：这种方法可能不总是有效
        audit_logger.info(f"Request processed: {method} {path}, status code: {response.status_code}")
        
        # 结束时间
        end_time = time.time()
        process_time = end_time - start_time
        
        # 提取响应信息
        status_code = response.status_code
        
        # 确定操作类型
        operation_type = self._get_operation_type(method)
        
        # 确定资源类型和ID
        resource_type, resource_id = self._get_resource_info(path)
        
        # 生成描述
        description = f"{method} {path}"
        
        # 准备审计日志数据
        before_data = None
        after_data = None
        
        # 根据操作类型设置数据
        if operation_type == OperationType.CREATE or operation_type == OperationType.UPDATE:
            after_data = request_body
        elif operation_type == OperationType.DELETE:
            before_data = request_body
        
        # 注意：审计日志现在在服务层记录，不再在中间件中记录
        # 这样可以避免重复记录，并且服务层能够直接访问请求体数据
        audit_logger.info(f"Audit log will be recorded at service layer: {method} {path}")
        
        return response
    
    async def _log_audit_async(self, operation_type, resource_type, resource_id, user_id, username, ip_address, before_data, after_data, description):
        """异步记录审计日志，避免阻塞请求"""
        try:
            # 使用新的数据库会话记录审计日志
            db = SessionLocal()
            try:
                audit_service = AuditLogService(AuditLogRepository(db))
                audit_service.create_audit_log(
                    operation_type=operation_type,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    user_id=user_id,
                    username=username,
                    ip_address=ip_address,
                    before_data=before_data,
                    after_data=after_data,
                    description=description
                )
            finally:
                db.close()
        except Exception as e:
            # 审计日志失败不应影响请求处理，但记录错误信息便于调试
            audit_logger.error(f"Audit log error: {str(e)}")
            pass
    
    def _get_resource_state(self, db, resource_type, resource_id):
        """获取资源状态"""
        try:
            # 根据资源类型获取资源
            if resource_type == ResourceType.SYSTEM:
                from apimgmt.repositories.system_repository import SystemRepository
                repo = SystemRepository(db)
                system = repo.find_by_id(resource_id)
                if system:
                    return {
                        "id": system.id,
                        "name": system.name,
                        "system_code": system.system_code,
                        "description": system.description
                    }
            
            elif resource_type == ResourceType.API:
                from apimgmt.repositories.api_repository import ApiRepository
                repo = ApiRepository(db)
                api = repo.find_by_id(resource_id)
                if api:
                    return {
                        "id": api.id,
                        "system_id": api.system_id,
                        "name": api.name,
                        "description": api.description,
                        "api_type": api.api_type
                    }
            
            elif resource_type == ResourceType.ENDPOINT:
                from apimgmt.repositories.endpoint_repository import EndpointRepository
                repo = EndpointRepository(db)
                endpoint = repo.find_by_id(resource_id)
                if endpoint:
                    return {
                        "id": endpoint.id,
                        "api_id": endpoint.api_id,
                        "path": endpoint.path,
                        "http_method": endpoint.http_method,
                        "description": endpoint.description
                    }
            
            elif resource_type == ResourceType.RELATIONSHIP:
                from apimgmt.repositories.relationship_repository import RelationshipRepository
                repo = RelationshipRepository(db)
                relationship = repo.find_by_id(resource_id)
                if relationship:
                    return {
                        "id": relationship.id,
                        "caller_type": relationship.caller_type,
                        "caller_id": relationship.caller_id,
                        "callee_type": relationship.callee_type,
                        "callee_id": relationship.callee_id
                    }
        except:
            pass
        
        return None
    
    def _get_operation_type(self, method: str) -> OperationType:
        """根据HTTP方法确定操作类型"""
        if method == 'POST':
            return OperationType.CREATE
        elif method == 'PUT' or method == 'PATCH':
            return OperationType.UPDATE
        elif method == 'DELETE':
            return OperationType.DELETE
        else:
            # 对于GET请求，返回None，不记录审计日志
            return None
    
    def _get_resource_info(self, path: str) -> tuple:
        """根据路径确定资源类型和ID"""
        # 分割路径
        parts = [p for p in path.split('/') if p]
        
        if not parts:
            return None, None
        
        # 处理API版本
        if parts[0] == 'api' and len(parts) > 1:
            parts = parts[2:]  # 跳过 /api/v1/
        
        if not parts:
            return None, None
        
        # 确定资源类型
        resource_type_map = {
            'systems': ResourceType.SYSTEM,
            'apis': ResourceType.API,
            'endpoints': ResourceType.ENDPOINT,
            'relationships': ResourceType.RELATIONSHIP,
            'users': ResourceType.USER
        }
        
        resource_type = None
        resource_id = None
        
        if parts[0] in resource_type_map:
            resource_type = resource_type_map[parts[0]]
            # 尝试获取资源ID
            if len(parts) > 1:
                resource_id = parts[1]
        
        return resource_type, resource_id
    
    def _get_resource_name(self, request_body: dict, response_body: dict) -> Optional[str]:
        """从请求体或响应体中获取资源名称"""
        if response_body and 'name' in response_body:
            return response_body['name']
        elif request_body and 'name' in request_body:
            return request_body['name']
        return None
