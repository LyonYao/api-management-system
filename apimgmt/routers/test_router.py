from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from apimgmt.db.database import get_db
from apimgmt.dependencies.auth_dependency import get_current_user
from apimgmt.models.user import User
from apimgmt.schemas.test import (
    CreateEndpointTestRequest, EndpointTestDTO, UpdateEndpointTestRequest,
    TestRunResponse, TestResultDTO, TestTrendResponse, TestTrendQueryParams,
    TestBatchDTO, TestBatchListResponse, TestRunInitiationResponse
)
from apimgmt.services.test_service import TestService

router = APIRouter(prefix="/api/v1/tests", tags=["tests"])


@router.post("/", response_model=EndpointTestDTO)
async def create_test(
    request: CreateEndpointTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建测试用例"""
    try:
        test_service = TestService(db)
        test = test_service.create_test(request)
        return test
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="创建测试用例失败")


@router.get("/endpoint/{endpoint_id}", response_model=List[EndpointTestDTO])
async def get_endpoint_tests(
    endpoint_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定Endpoint的所有测试用例"""
    test_service = TestService(db)
    tests = test_service.get_tests_by_endpoint(endpoint_id)
    return tests


@router.get("/{test_id}", response_model=EndpointTestDTO)
async def get_test(
    test_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取测试用例详情"""
    test_service = TestService(db)
    test = test_service.get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    return test


@router.put("/{test_id}", response_model=EndpointTestDTO)
async def update_test(
    test_id: str,
    request: UpdateEndpointTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新测试用例"""
    try:
        test_service = TestService(db)
        test = test_service.update_test(test_id, request)
        if not test:
            raise HTTPException(status_code=404, detail="测试用例不存在")
        return test
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="更新测试用例失败")


@router.delete("/{test_id}")
async def delete_test(
    test_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除测试用例"""
    test_service = TestService(db)
    success = test_service.delete_test(test_id)
    if not success:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    return {"message": "测试用例删除成功"}


@router.post("/api/{api_id}/run", response_model=TestRunInitiationResponse)
async def run_api_tests(
    api_id: str,
    environment: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """运行API的所有测试用例"""
    try:
        test_service = TestService(db)
        result = await test_service.run_api_tests(api_id, environment)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"运行测试失败: {str(e)}")


@router.post("/endpoint/{endpoint_id}/run", response_model=TestRunResponse)
async def run_endpoint_tests(
    endpoint_id: str,
    environment: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """运行Endpoint的所有测试用例"""
    try:
        test_service = TestService(db)
        result = await test_service.run_endpoint_tests(endpoint_id, environment)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"运行测试失败: {str(e)}")


@router.get("/results/system/{system_id}", response_model=TestBatchListResponse)
async def get_system_test_results(
    system_id: str,
    api_id: str = None,
    start_time: str = None,
    end_time: str = None,
    environment: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """根据系统ID查询测试批次列表"""
    test_service = TestService(db)
    batches = test_service.get_test_batches({"system_id": system_id, "api_id": api_id, "start_date": start_time, "end_date": end_time, "environment": environment})
    # 转换为DTO
    batch_dtos = [
        TestBatchDTO(
            batch_id=batch["batch_id"],
            executed_at=batch["executed_at"],
            total_count=batch["total_count"],
            pass_count=batch["pass_count"],
            fail_count=batch["fail_count"],
            error_count=batch["error_count"],
            system_id=batch.get("system_id"),
            system_name=batch.get("system_name"),
            api_id=batch.get("api_id"),
            api_name=batch.get("api_name"),
            environment=batch.get("environment")
        )
        for batch in batches
    ]
    return TestBatchListResponse(
        items=batch_dtos,
        total=len(batch_dtos)
    )


@router.get("/results/batch/{batch_id}", response_model=List[TestResultDTO])
async def get_batch_test_results(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """根据批次ID查询测试结果"""
    test_service = TestService(db)
    results = test_service.get_test_results({"batch_id": batch_id})
    return results


@router.post("/trends", response_model=TestTrendResponse)
async def get_test_trends(
    query: TestTrendQueryParams,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取测试趋势分析"""
    try:
        test_service = TestService(db)
        trends = test_service.get_test_trends(query.model_dump())
        return trends
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取测试趋势失败")
