from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import uuid

from apimgmt.db.database import get_db
from apimgmt.schemas.system import CreateSystemRequest, UpdateSystemRequest, SystemDTO
from apimgmt.services.system_service import SystemService
from apimgmt.repositories.system_repository import SystemRepository
from apimgmt.repositories.audit_repository import AuditLogRepository
from apimgmt.services.audit_service import AuditLogService
from apimgmt.exceptions import ResourceNotFoundException, DuplicateResourceException, ValidationException
from apimgmt.dependencies.auth_dependency import get_current_user


router = APIRouter()


def get_system_service(db: Session = Depends(get_db)) -> SystemService:
    """获取系统服务"""
    system_repository = SystemRepository(db)
    audit_repository = AuditLogRepository(db)
    audit_service = AuditLogService(audit_repository)
    return SystemService(system_repository, audit_service)


@router.post("", response_model=SystemDTO, status_code=201)
async def create_system(
    request: CreateSystemRequest,
    current_user = Depends(get_current_user),
    system_service: SystemService = Depends(get_system_service)
):
    """创建系统"""
    try:
        return system_service.create_system(request)
    except DuplicateResourceException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("", response_model=List[SystemDTO])
async def get_all_systems(
    system_service: SystemService = Depends(get_system_service)
):
    """获取所有系统"""
    try:
        return system_service.get_all_systems()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{system_id}", response_model=SystemDTO)
async def get_system(
    system_id: str,
    system_service: SystemService = Depends(get_system_service)
):
    """根据ID获取系统"""
    try:
        return system_service.get_system_by_id(system_id)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{system_id}", response_model=SystemDTO)
async def update_system(
    system_id: str,
    request: UpdateSystemRequest,
    current_user = Depends(get_current_user),
    system_service: SystemService = Depends(get_system_service)
):
    """更新系统"""
    try:
        return system_service.update_system(system_id, request)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DuplicateResourceException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{system_id}", status_code=204)
async def delete_system(
    system_id: str,
    current_user = Depends(get_current_user),
    system_service: SystemService = Depends(get_system_service)
):
    """删除系统"""
    try:
        system_service.delete_system(system_id)
        return None
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
