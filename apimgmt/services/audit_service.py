from typing import Optional, Dict, Any, List, Set, Tuple
from datetime import datetime
import json

from apimgmt.repositories.audit_repository import AuditLogRepository
from apimgmt.models.audit import AuditLog, OperationType, ResourceType


def _serialize_data(data: Any) -> Any:
    """序列化数据，确保所有类型都能正确转换为JSON
    
    Args:
        data: 需要序列化的数据
        
    Returns:
        序列化后的数据
    """
    if isinstance(data, (list, tuple)):
        return [_serialize_data(item) for item in data]
    elif isinstance(data, dict):
        return {key: _serialize_data(value) for key, value in data.items()}
    elif isinstance(data, (set, frozenset)):
        return list(data)
    elif hasattr(data, "model_dump"):
        # 处理Pydantic模型
        return _serialize_data(data.model_dump())
    else:
        return data


class AuditLogService:
    """审计日志服务"""
    
    def __init__(self, audit_repository: AuditLogRepository):
        self.audit_repository = audit_repository
    
    def create_audit_log(
        self,
        operation_type: OperationType,
        resource_type: ResourceType,
        resource_id: str,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        before_data: Optional[Dict[str, Any]] = None,
        after_data: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ) -> AuditLog:
        """创建审计日志
        
        Args:
            operation_type: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            user_id: 用户ID
            username: 用户名
            ip_address: IP地址
            before_data: 操作前的数据
            after_data: 操作后的数据
            description: 描述
            
        Returns:
            创建的审计日志
        """
        # 序列化数据，确保所有类型都能正确转换为JSON
        serialized_before = _serialize_data(before_data)
        serialized_after = _serialize_data(after_data)
        
        # 转换数据为JSON字符串，确保中文字符不被转码
        before_data_json = json.dumps(serialized_before, ensure_ascii=False) if serialized_before else None
        after_data_json = json.dumps(serialized_after, ensure_ascii=False) if serialized_after else None
        
        # 创建审计日志
        audit_log = AuditLog(
            operation_type=operation_type,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            before_data=before_data_json,
            after_data=after_data_json,
            description=description
        )
        
        return self.audit_repository.create(audit_log)
    
    def get_audit_log_by_id(self, audit_id: str) -> Optional[AuditLog]:
        """根据ID获取审计日志"""
        return self.audit_repository.find_by_id(audit_id)
    
    def get_audit_logs(
        self,
        operation_type: Optional[OperationType] = None,
        resource_type: Optional[ResourceType] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """分页获取审计日志
        
        Args:
            operation_type: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            user_id: 用户ID
            username: 用户名
            start_time: 开始时间
            end_time: 结束时间
            page: 页码，从1开始
            page_size: 每页数量
            
        Returns:
            包含审计日志列表和总数的字典
        """
        return self.audit_repository.find_all(
            operation_type=operation_type,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            username=username,
            start_time=start_time,
            end_time=end_time,
            page=page,
            page_size=page_size
        )
    
    def get_audit_logs_by_resource(
        self,
        resource_type: ResourceType,
        resource_id: str
    ) -> list:
        """根据资源类型和ID获取审计日志
        
        Args:
            resource_type: 资源类型
            resource_id: 资源ID
            
        Returns:
            审计日志列表
        """
        return self.audit_repository.find_by_resource_id(
            resource_type=resource_type,
            resource_id=resource_id
        )
