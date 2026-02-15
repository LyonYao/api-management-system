from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from apimgmt.db.database import get_db
from apimgmt.schemas.audit import AuditLogDTO, AuditLogListResponse
from apimgmt.services.audit_service import AuditLogService
from apimgmt.repositories.audit_repository import AuditLogRepository
from apimgmt.models.audit import OperationType, ResourceType
from apimgmt.dependencies.auth_dependency import get_current_user


router = APIRouter(tags=["audit"])


def get_audit_service(db: Session = Depends(get_db)) -> AuditLogService:
    """获取审计日志服务"""
    audit_repository = AuditLogRepository(db)
    return AuditLogService(audit_repository)


@router.get("", response_model=AuditLogListResponse)
async def get_audit_logs(
    operation_type: Optional[OperationType] = Query(None, description="操作类型"),
    resource_type: Optional[ResourceType] = Query(None, description="资源类型"),
    resource_id: Optional[str] = Query(None, description="资源ID"),
    username: Optional[str] = Query(None, description="用户名"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    audit_service: AuditLogService = Depends(get_audit_service),
    current_user = Depends(get_current_user)
):
    """获取审计日志列表"""
    try:
        result = audit_service.get_audit_logs(
            operation_type=operation_type,
            resource_type=resource_type,
            resource_id=resource_id,
            username=username,
            start_time=start_time,
            end_time=end_time,
            page=page,
            page_size=page_size
        )
        
        # 转换为DTO
        items = []
        for audit_log in result["items"]:
            # 解析JSON数据
            before_data = None
            after_data = None
            if audit_log.before_data:
                import json
                before_data = json.loads(audit_log.before_data)
            if audit_log.after_data:
                import json
                after_data = json.loads(audit_log.after_data)
            
            items.append(AuditLogDTO(
                id=audit_log.id,
                operation_type=audit_log.operation_type,
                resource_type=audit_log.resource_type,
                resource_id=audit_log.resource_id,
                user_id=audit_log.user_id,
                username=audit_log.username,
                ip_address=audit_log.ip_address,
                before_data=before_data,
                after_data=after_data,
                description=audit_log.description,
                created_at=audit_log.created_at
            ))
        
        return AuditLogListResponse(
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            items=items
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{audit_id}", response_model=AuditLogDTO)
async def get_audit_log(
    audit_id: str,
    audit_service: AuditLogService = Depends(get_audit_service),
    current_user = Depends(get_current_user)
):
    """获取单个审计日志"""
    try:
        audit_log = audit_service.get_audit_log_by_id(audit_id)
        if not audit_log:
            raise HTTPException(status_code=404, detail="Audit log not found")
        
        # 解析JSON数据
        before_data = None
        after_data = None
        if audit_log.before_data:
            import json
            before_data = json.loads(audit_log.before_data)
        if audit_log.after_data:
            import json
            after_data = json.loads(audit_log.after_data)
        
        return AuditLogDTO(
            id=audit_log.id,
            operation_type=audit_log.operation_type,
            resource_type=audit_log.resource_type,
            resource_id=audit_log.resource_id,
            user_id=audit_log.user_id,
            username=audit_log.username,
            ip_address=audit_log.ip_address,
            before_data=before_data,
            after_data=after_data,
            description=audit_log.description,
            created_at=audit_log.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
