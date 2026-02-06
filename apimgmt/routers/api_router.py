from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Set
import uuid

from apimgmt.db.database import get_db
from apimgmt.schemas.api import CreateApiRequest, UpdateApiRequest, ApiDTO
from apimgmt.services.api_service import ApiService
from apimgmt.repositories.api_repository import ApiRepository
from apimgmt.repositories.system_repository import SystemRepository
from apimgmt.repositories.tag_repository import TagRepository
from apimgmt.exceptions import ResourceNotFoundException, ValidationException


router = APIRouter()


def get_api_service(db: Session = Depends(get_db)) -> ApiService:
    """获取API服务"""
    api_repository = ApiRepository(db)
    system_repository = SystemRepository(db)
    tag_repository = TagRepository(db)
    return ApiService(api_repository, system_repository, tag_repository)


@router.post("", response_model=ApiDTO, status_code=201)
async def create_api(
    request: CreateApiRequest,
    api_service: ApiService = Depends(get_api_service)
):
    """创建API"""
    try:
        return api_service.create_api(request)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("", response_model=List[ApiDTO])
async def get_apis(
    system_id: uuid.UUID = Query(None, description="系统ID"),
    tags: Set[str] = Query(None, description="标签列表"),
    api_service: ApiService = Depends(get_api_service)
):
    """获取API列表"""
    try:
        if system_id:
            return api_service.get_apis_by_system_id(system_id)
        elif tags:
            return api_service.get_apis_by_tags(tags)
        else:
            return api_service.get_all_apis()
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/search", response_model=List[ApiDTO])
async def search_apis(
    systemId: uuid.UUID = Query(None, description="系统ID"),
    tags: Set[str] = Query(None, description="标签列表"),
    api_service: ApiService = Depends(get_api_service)
):
    """搜索API"""
    try:
        if systemId:
            return api_service.get_apis_by_system_id(systemId)
        elif tags:
            return api_service.get_apis_by_tags(tags)
        else:
            return api_service.get_all_apis()
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{api_id}", response_model=ApiDTO)
async def get_api(
    api_id: uuid.UUID,
    api_service: ApiService = Depends(get_api_service)
):
    """根据ID获取API"""
    try:
        return api_service.get_api_by_id(api_id)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{api_id}", response_model=ApiDTO)
async def update_api(
    api_id: uuid.UUID,
    request: UpdateApiRequest,
    api_service: ApiService = Depends(get_api_service)
):
    """更新API"""
    try:
        return api_service.update_api(api_id, request)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{api_id}", status_code=204)
async def delete_api(
    api_id: uuid.UUID,
    api_service: ApiService = Depends(get_api_service)
):
    """删除API"""
    try:
        api_service.delete_api(api_id)
        return None
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
