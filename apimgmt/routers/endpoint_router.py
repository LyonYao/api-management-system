from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import uuid

from apimgmt.db.database import get_db
from apimgmt.schemas.endpoint import CreateEndpointRequest, UpdateEndpointRequest, EndpointDTO
from apimgmt.services.endpoint_service import EndpointService
from apimgmt.repositories.endpoint_repository import EndpointRepository
from apimgmt.repositories.api_repository import ApiRepository
from apimgmt.repositories.audit_repository import AuditLogRepository
from apimgmt.services.audit_service import AuditLogService
from apimgmt.exceptions import ResourceNotFoundException
from apimgmt.dependencies.auth_dependency import get_current_user


router = APIRouter()


def get_endpoint_service(db: Session = Depends(get_db)) -> EndpointService:
    """获取端点服务"""
    endpoint_repository = EndpointRepository(db)
    api_repository = ApiRepository(db)
    audit_repository = AuditLogRepository(db)
    audit_service = AuditLogService(audit_repository)
    return EndpointService(endpoint_repository, api_repository, audit_service)


@router.post("", response_model=EndpointDTO, status_code=201)
async def create_endpoint(
    request: CreateEndpointRequest,
    current_user = Depends(get_current_user),
    endpoint_service: EndpointService = Depends(get_endpoint_service)
):
    """创建端点"""
    try:
        return endpoint_service.create_endpoint(request)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("", response_model=List[EndpointDTO])
async def get_all_endpoints(
    endpoint_service: EndpointService = Depends(get_endpoint_service)
):
    """获取所有端点"""
    try:
        return endpoint_service.get_all_endpoints()
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/api/{api_id}", response_model=List[EndpointDTO])
async def get_endpoints_by_api(
    api_id: str,
    endpoint_service: EndpointService = Depends(get_endpoint_service)
):
    """根据API ID获取端点"""
    try:
        return endpoint_service.get_endpoints_by_api_id(api_id)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{endpoint_id}", response_model=EndpointDTO)
async def get_endpoint(
    endpoint_id: str,
    endpoint_service: EndpointService = Depends(get_endpoint_service)
):
    """根据ID获取端点"""
    try:
        return endpoint_service.get_endpoint_by_id(endpoint_id)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{endpoint_id}", response_model=EndpointDTO)
async def update_endpoint(
    endpoint_id: str,
    request: UpdateEndpointRequest,
    current_user = Depends(get_current_user),
    endpoint_service: EndpointService = Depends(get_endpoint_service)
):
    """更新端点"""
    try:
        return endpoint_service.update_endpoint(endpoint_id, request)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{endpoint_id}", status_code=204)
async def delete_endpoint(
    endpoint_id: str,
    current_user = Depends(get_current_user),
    endpoint_service: EndpointService = Depends(get_endpoint_service)
):
    """删除端点"""
    try:
        endpoint_service.delete_endpoint(endpoint_id)
        return None
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
