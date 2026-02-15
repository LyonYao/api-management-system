from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from apimgmt.db.database import get_db
from apimgmt.schemas.health_check import HealthCheckResultDTO, BatchHealthCheckResponse, EnvironmentHealthCheckRequest, HealthCheckBatchListResponse, HealthCheckBatchDTO
from apimgmt.services.health_check_service import HealthCheckService
from apimgmt.repositories.health_check_result_repository import HealthCheckResultRepository
from apimgmt.repositories.endpoint_repository import EndpointRepository
from apimgmt.repositories.api_repository import ApiRepository
from apimgmt.repositories.system_repository import SystemRepository
from apimgmt.exceptions import ResourceNotFoundException
from apimgmt.dependencies.auth_dependency import get_current_user


router = APIRouter()


def get_health_check_service(db: Session = Depends(get_db)) -> HealthCheckService:
    """获取健康检查服务"""
    health_check_result_repository = HealthCheckResultRepository(db)
    endpoint_repository = EndpointRepository(db)
    api_repository = ApiRepository(db)
    system_repository = SystemRepository(db)
    return HealthCheckService(health_check_result_repository, endpoint_repository, api_repository, system_repository)


@router.post("/system/environment", response_model=BatchHealthCheckResponse)
async def check_system_health_with_environment(
    request: EnvironmentHealthCheckRequest,
    health_check_service: HealthCheckService = Depends(get_health_check_service),
    current_user = Depends(get_current_user)
):
    """带环境参数的系统健康检查"""
    try:
        print(f"执行系统健康检查 - system_id: {request.system_id}, environment: {request.environment}")
        result = await health_check_service.check_system_health(request.system_id, request.environment)
        print(f"系统健康检查完成 - 结果数量: {len(result.results)}")
        return result
    except ResourceNotFoundException as e:
        print(f"系统健康检查失败 - 资源未找到: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"系统健康检查失败 - 内部错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/results/system/{system_id}", response_model=List[HealthCheckResultDTO])
async def get_system_health_check_results(
    system_id: str,
    health_check_service: HealthCheckService = Depends(get_health_check_service),
    current_user = Depends(get_current_user)
):
    """获取系统的健康检查结果"""
    try:
        return health_check_service.get_health_check_results_by_system(system_id)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/batches", response_model=HealthCheckBatchListResponse)
async def get_health_check_batches(
    system_id: Optional[str] = Query(None, description="系统ID，用于过滤批次列表"),
    environment: Optional[str] = Query(None, description="环境，用于过滤批次列表"),
    health_check_service: HealthCheckService = Depends(get_health_check_service)
):
    """获取健康检查批次列表，支持按系统和环境过滤"""
    try:
        print(f"获取批次列表 - system_id: {system_id}, environment: {environment}")
        batches = health_check_service.get_health_check_batches(system_id, environment)
        print(f"获取到批次数量: {len(batches)}")
        
        # 转换为DTO，只处理batch_id不为None的记录
        batch_dtos = []
        for batch in batches:
            print(f"批次信息: {batch}")
            if batch and batch.get('batch_id'):
                try:
                    batch_dto = HealthCheckBatchDTO(
                        batch_id=batch['batch_id'],
                        system_id=batch['system_id'],
                        environment=batch['environment'],
                        total_count=batch['total_count'],
                        success_count=batch['success_count'],
                        failure_count=batch['failure_count'],
                        checked_at=batch['checked_at']
                    )
                    batch_dtos.append(batch_dto)
                    print(f"成功添加批次: {batch['batch_id']}")
                except Exception as e:
                    print(f"创建DTO失败: {str(e)}")
                    continue
            else:
                print(f"跳过批次，batch_id为None: {batch}")
        
        print(f"转换为DTO数量: {len(batch_dtos)}")
        return HealthCheckBatchListResponse(
            items=batch_dtos,
            total=len(batch_dtos)
        )
    except Exception as e:
        print(f"错误详情: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/batch/{batch_id}", response_model=List[HealthCheckResultDTO])
async def get_batch_health_check_results(
    batch_id: str,
    health_check_service: HealthCheckService = Depends(get_health_check_service),
    current_user = Depends(get_current_user)
):
    """获取批次的健康检查结果"""
    try:
        return health_check_service.get_health_check_results_by_batch(batch_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

