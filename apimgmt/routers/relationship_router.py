from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List
import uuid

from apimgmt.db.database import get_db
from apimgmt.schemas.relationship import CreateRelationshipRequest, UpdateRelationshipRequest, RelationshipDTO
from apimgmt.services.relationship_service import RelationshipService
from apimgmt.repositories.relationship_repository import RelationshipRepository
from apimgmt.repositories.api_repository import ApiRepository
from apimgmt.repositories.endpoint_repository import EndpointRepository
from apimgmt.repositories.audit_repository import AuditLogRepository
from apimgmt.services.audit_service import AuditLogService
from apimgmt.exceptions import ResourceNotFoundException
from apimgmt.dependencies.auth_dependency import get_current_user


router = APIRouter()


def get_relationship_service(db: Session = Depends(get_db)) -> RelationshipService:
    """获取关系服务"""
    relationship_repository = RelationshipRepository(db)
    api_repository = ApiRepository(db)
    endpoint_repository = EndpointRepository(db)
    audit_repository = AuditLogRepository(db)
    audit_service = AuditLogService(audit_repository)
    return RelationshipService(relationship_repository, api_repository, endpoint_repository, audit_service)


@router.post("", response_model=RelationshipDTO, status_code=201)
async def create_relationship(
    request: CreateRelationshipRequest,
    current_user = Depends(get_current_user),
    relationship_service: RelationshipService = Depends(get_relationship_service)
):
    """创建调用关系"""
    try:
        return relationship_service.create_relationship(request)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("", response_model=List[RelationshipDTO])
async def get_relationships(
    caller_type: str = None,
    caller_id: uuid.UUID = None,
    callee_type: str = None,
    callee_id: uuid.UUID = None,
    relationship_service: RelationshipService = Depends(get_relationship_service)
):
    """获取调用关系列表"""
    try:
        if caller_type and caller_id:
            return relationship_service.get_relationships_by_caller(caller_type, caller_id)
        elif callee_type and callee_id:
            return relationship_service.get_relationships_by_callee(callee_type, callee_id)
        else:
            return relationship_service.get_all_relationships()
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{relationship_id}", response_model=RelationshipDTO)
async def get_relationship(
    relationship_id: uuid.UUID,
    relationship_service: RelationshipService = Depends(get_relationship_service)
):
    """根据ID获取调用关系"""
    try:
        return relationship_service.get_relationship_by_id(relationship_id)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{relationship_id}", response_model=RelationshipDTO)
async def update_relationship(
    relationship_id: uuid.UUID,
    request: UpdateRelationshipRequest,
    current_user = Depends(get_current_user),
    relationship_service: RelationshipService = Depends(get_relationship_service)
):
    """更新调用关系"""
    try:
        return relationship_service.update_relationship(relationship_id, request)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{relationship_id}", status_code=204)
async def delete_relationship(
    relationship_id: uuid.UUID,
    current_user = Depends(get_current_user),
    relationship_service: RelationshipService = Depends(get_relationship_service)
):
    """删除调用关系"""
    try:
        relationship_service.delete_relationship(relationship_id)
        return None
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
