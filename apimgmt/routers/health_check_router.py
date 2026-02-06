from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from apimgmt.db.database import get_db
from apimgmt.schemas.health_check import HealthCheckResultDTO, BatchHealthCheckRequest, BatchHealthCheckResponse
from apimgmt.services.health_check_service import HealthCheckService
from apimgmt.repositories.health_check_result_repository import HealthCheckResultRepository
from apimgmt.repositories.endpoint_repository import EndpointRepository
from apimgmt.repositories.api_repository import ApiRepository
from apimgmt.exceptions import ResourceNotFoundException


router = APIRouter()


def get_health_check_service(db: Session = Depends(get_db)) -> HealthCheckService:
    """获取健康检查服务"""
    health_check_result_repository = HealthCheckResultRepository(db)
    endpoint_repository = EndpointRepository(db)
    api_repository = ApiRepository(db)
    return HealthCheckService(health_check_result_repository, endpoint_repository, api_repository)


@router.post("/check/{endpoint_id}", response_model=HealthCheckResultDTO)
async def check_endpoint_health(
    endpoint_id: uuid.UUID,
    health_check_service: HealthCheckService = Depends(get_health_check_service)
):
    """检查端点健康状态"""
    try:
        return await health_check_service.check_endpoint_health(endpoint_id)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/batch", response_model=BatchHealthCheckResponse)
async def batch_health_check(
    request: BatchHealthCheckRequest,
    health_check_service: HealthCheckService = Depends(get_health_check_service)
):
    """批量检查端点健康状态"""
    try:
        return await health_check_service.batch_health_check(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/results", response_model=List[HealthCheckResultDTO])
async def get_recent_health_check_results(
    limit: int = 100,
    health_check_service: HealthCheckService = Depends(get_health_check_service)
):
    """获取最近的健康检查结果"""
    try:
        return health_check_service.get_recent_health_check_results(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/results/{endpoint_id}", response_model=List[HealthCheckResultDTO])
async def get_health_check_results(
    endpoint_id: uuid.UUID,
    health_check_service: HealthCheckService = Depends(get_health_check_service)
):
    """获取端点的健康检查结果"""
    try:
        return health_check_service.get_health_check_results(endpoint_id)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
