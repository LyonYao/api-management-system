from typing import List, Dict, Any
import uuid
import asyncio
import httpx
from datetime import datetime

from apimgmt.repositories.health_check_result_repository import HealthCheckResultRepository
from apimgmt.repositories.endpoint_repository import EndpointRepository
from apimgmt.repositories.api_repository import ApiRepository
from apimgmt.models.health_check_result import HealthCheckResult
from apimgmt.schemas.health_check import HealthCheckResultDTO, BatchHealthCheckRequest, BatchHealthCheckResponse
from apimgmt.enums.health_check_status import HealthCheckStatus
from apimgmt.exceptions import ResourceNotFoundException


class HealthCheckService:
    def __init__(self, health_check_result_repository: HealthCheckResultRepository, endpoint_repository: EndpointRepository, api_repository: ApiRepository):
        self.health_check_result_repository = health_check_result_repository
        self.endpoint_repository = endpoint_repository
        self.api_repository = api_repository
        self.timeout = 30  # 30秒超时
    
    async def check_endpoint_health(self, endpoint_id: uuid.UUID) -> HealthCheckResultDTO:
        """检查端点健康状态"""
        # 验证端点是否存在
        endpoint = self.endpoint_repository.find_by_id(endpoint_id)
        if not endpoint:
            raise ResourceNotFoundException("Endpoint", endpoint_id)
        
        # 验证API是否存在
        api = self.api_repository.find_by_id(endpoint.api_id)
        if not api:
            raise ResourceNotFoundException("API", endpoint.api_id)
        
        # 构建完整URL（这里简化处理，实际应该从配置或API信息中获取基础URL）
        url = f"http://localhost:8080{endpoint.path}"
        
        # 执行健康检查
        status = HealthCheckStatus.SUCCESS
        response_code = None
        response_time_ms = None
        error_message = None
        
        try:
            start_time = datetime.utcnow()
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if endpoint.method == "GET":
                    response = await client.get(url)
                elif endpoint.method == "POST":
                    response = await client.post(url, json={})
                elif endpoint.method == "PUT":
                    response = await client.put(url, json={})
                elif endpoint.method == "DELETE":
                    response = await client.delete(url)
                else:
                    status = HealthCheckStatus.ERROR
                    error_message = f"Unsupported HTTP method: {endpoint.method}"
                    response_code = 0
                
                if status == HealthCheckStatus.SUCCESS:
                    end_time = datetime.utcnow()
                    response_time_ms = int((end_time - start_time).total_seconds() * 1000)
                    response_code = response.status_code
                    
                    if response_code >= 400:
                        status = HealthCheckStatus.FAILURE
                        error_message = f"HTTP error: {response_code}"
        except httpx.TimeoutException:
            status = HealthCheckStatus.TIMEOUT
            error_message = "Request timed out"
            response_time_ms = self.timeout * 1000
        except Exception as e:
            status = HealthCheckStatus.ERROR
            error_message = str(e)
        
        # 保存健康检查结果
        health_check_result = HealthCheckResult(
            id=uuid.uuid4(),
            endpoint_id=endpoint_id,
            status=status.value,
            response_code=response_code,
            response_time_ms=response_time_ms,
            error_message=error_message,
            checked_at=datetime.utcnow()
        )
        
        created_result = self.health_check_result_repository.create(health_check_result)
        return HealthCheckResultDTO.model_validate(created_result)
    
    async def batch_health_check(self, request: BatchHealthCheckRequest) -> BatchHealthCheckResponse:
        """批量检查端点健康状态"""
        if not request.endpoint_ids:
            return BatchHealthCheckResponse(results=[])
        
        # 限制批量检查数量
        endpoint_ids = request.endpoint_ids[:100]  # 最多检查100个端点
        
        # 并发执行健康检查
        tasks = [self.check_endpoint_health(endpoint_id) for endpoint_id in endpoint_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        valid_results = []
        for result in results:
            if isinstance(result, HealthCheckResultDTO):
                valid_results.append(result)
        
        return BatchHealthCheckResponse(results=valid_results)
    
    def get_health_check_results(self, endpoint_id: uuid.UUID) -> List[HealthCheckResultDTO]:
        """获取端点的健康检查结果"""
        # 验证端点是否存在
        endpoint = self.endpoint_repository.find_by_id(endpoint_id)
        if not endpoint:
            raise ResourceNotFoundException("Endpoint", endpoint_id)
        
        results = self.health_check_result_repository.find_by_endpoint_id(endpoint_id)
        return [HealthCheckResultDTO.model_validate(result) for result in results]
    
    def get_recent_health_check_results(self, limit: int = 100) -> List[HealthCheckResultDTO]:
        """获取最近的健康检查结果"""
        results = self.health_check_result_repository.find_recent(limit)
        return [HealthCheckResultDTO.model_validate(result) for result in results]
