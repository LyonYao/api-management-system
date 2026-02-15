from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from apimgmt.models.audit import AuditLog, OperationType, ResourceType


class AuditLogRepository:
    """审计日志仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, audit_log: AuditLog) -> AuditLog:
        """创建审计日志"""
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        return audit_log
    
    def find_by_id(self, audit_id: str) -> Optional[AuditLog]:
        """根据ID查找审计日志"""
        return self.db.query(AuditLog).filter(AuditLog.id == audit_id).first()
    
    def find_all(
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
        """分页查询审计日志
        
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
        # 构建查询条件
        filters = []
        
        if operation_type:
            filters.append(AuditLog.operation_type == operation_type)
        
        if resource_type:
            filters.append(AuditLog.resource_type == resource_type)
        
        if resource_id:
            filters.append(AuditLog.resource_id == resource_id)
        
        if user_id:
            filters.append(AuditLog.user_id == user_id)
        
        if username:
            filters.append(AuditLog.username == username)
        
        if start_time:
            filters.append(AuditLog.created_at >= start_time)
        
        if end_time:
            filters.append(AuditLog.created_at <= end_time)
        
        # 计算总数
        total = self.db.query(AuditLog).filter(*filters).count()
        
        # 分页查询
        offset = (page - 1) * page_size
        audit_logs = self.db.query(AuditLog)\
            .filter(*filters)\
            .order_by(AuditLog.created_at.desc())\
            .offset(offset)\
            .limit(page_size)\
            .all()
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": audit_logs
        }
    
    def find_by_resource_id(self, resource_type: ResourceType, resource_id: str) -> List[AuditLog]:
        """根据资源ID查找审计日志"""
        return self.db.query(AuditLog)\
            .filter(
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == resource_id
            )\
            .order_by(AuditLog.created_at.desc())\
            .all()
