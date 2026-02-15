from typing import List, Dict, Any, Optional
import uuid
import asyncio
import httpx
import json
import re
from datetime import datetime

from apimgmt.repositories.health_check_result_repository import HealthCheckResultRepository
from apimgmt.repositories.endpoint_repository import EndpointRepository
from apimgmt.repositories.api_repository import ApiRepository
from apimgmt.repositories.system_repository import SystemRepository
from apimgmt.models.health_check_result import HealthCheckResult
from apimgmt.schemas.health_check import HealthCheckResultDTO, BatchHealthCheckResponse, EnvironmentHealthCheckRequest
from apimgmt.enums.health_check_status import HealthCheckStatus
from apimgmt.exceptions import ResourceNotFoundException


class HealthCheckService:
    def __init__(self, health_check_result_repository: HealthCheckResultRepository, endpoint_repository: EndpointRepository, api_repository: ApiRepository, system_repository: SystemRepository):
        self.health_check_result_repository = health_check_result_repository
        self.endpoint_repository = endpoint_repository
        self.api_repository = api_repository
        self.system_repository = system_repository
        self.timeout = 30  # 30秒超时
    
    def _parse_path(self, data: Any, path: str) -> Any:
        """解析路径获取值"""
        if not path:
            return data
        
        parts = re.split(r'\.|\[|\]', path)
        parts = [p for p in parts if p]
        
        current = data
        for part in parts:
            if part == '*':
                if isinstance(current, list):
                    return [self._parse_path(item, '.'.join(parts[parts.index('*')+1:])) for item in current]
                else:
                    return None
            elif part.isdigit():
                index = int(part)
                if isinstance(current, list) and 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
        return current
    
    def _evaluate_rule(self, data: Any, rule: Dict[str, Any]) -> bool:
        """评估单个规则"""
        path = rule.get('path')
        operator = rule.get('operator')
        expected_value = rule.get('value')
        
        if not path or not operator:
            return False
        
        actual_value = self._parse_path(data, path)
        
        if operator == 'equals':
            return actual_value == expected_value
        elif operator == 'not_equals':
            return actual_value != expected_value
        elif operator == 'contains':
            if isinstance(actual_value, str):
                return expected_value in actual_value
            elif isinstance(actual_value, list):
                return expected_value in actual_value
            return False
        elif operator == 'not_contains':
            if isinstance(actual_value, str):
                return expected_value not in actual_value
            elif isinstance(actual_value, list):
                return expected_value not in actual_value
            return True
        elif operator == 'greater_than':
            if isinstance(actual_value, (int, float)):
                return actual_value > expected_value
            return False
        elif operator == 'less_than':
            if isinstance(actual_value, (int, float)):
                return actual_value < expected_value
            return False
        elif operator == 'greater_than_or_equal':
            if isinstance(actual_value, (int, float)):
                return actual_value >= expected_value
            return False
        elif operator == 'less_than_or_equal':
            if isinstance(actual_value, (int, float)):
                return actual_value <= expected_value
            return False
        elif operator == 'exists':
            return actual_value is not None
        elif operator == 'not_exists':
            return actual_value is None
        elif operator == 'matches':
            if isinstance(actual_value, str):
                try:
                    return bool(re.match(expected_value, actual_value))
                except:
                    return False
            return False
        return False
    
    def _validate_response(self, response: httpx.Response, rules: List[Dict[str, Any]]) -> bool:
        """验证响应是否符合规则"""
        if not rules:
            return True
        
        try:
            data = response.json()
        except:
            return False
        
        for rule in rules:
            if not self._evaluate_rule(data, rule):
                return False
        
        return True
    
    async def _check_api_health(self, api_id: str, environment: str, batch_id: str) -> Optional[HealthCheckResultDTO]:
        """检查单个API的健康状态（内部方法）"""
        try:
            # 验证API是否存在
            api = self.api_repository.find_by_id(api_id)
            if not api:
                print(f"API不存在: {api_id}")
                return None
            
            # 根据环境选择Host
            if environment == "dev":
                base_url = api.dev_host or api.uat_host or api.prod_host or "http://localhost:8080"
            elif environment == "prod":
                base_url = api.prod_host or api.uat_host or api.dev_host or "http://localhost:8080"
            else:  # uat
                base_url = api.uat_host or api.prod_host or api.dev_host or "http://localhost:8080"
            
            # 构建完整URL - 使用API的健康检查路径
            path = api.health_check_path or '/health'
            if not path.startswith('/'):
                path = '/' + path
            url = f"{base_url.rstrip('/')}{path}"
            print(f"执行健康检查 - API: {api.id}, URL: {url}, 环境: {environment}")
            
            # 解析健康检查规则
            health_check_rule = None
            if api.health_check_rule:
                try:
                    health_check_rule = json.loads(api.health_check_rule)
                except Exception as e:
                    print(f"解析健康检查规则失败: {e}")
                    pass
            
            expected_status = health_check_rule.get('expected_status', 200) if health_check_rule else 200
            timeout = health_check_rule.get('timeout', 5000) if health_check_rule else 5000
            response_rules = health_check_rule.get('response_rules', []) if health_check_rule else []
            headers = health_check_rule.get('headers', {}) if health_check_rule else {}
            
            # 执行健康检查 - 只使用GET方法
            status = HealthCheckStatus.SUCCESS
            response_code = None
            response_time_ms = None
            error_message = None
            response_body = None
            response_headers = None
            
            try:
                start_time = datetime.utcnow()
                async with httpx.AsyncClient(timeout=timeout/1000) as client:
                    # 只使用GET方法进行健康检查
                    response = await client.get(url, headers=headers)
                    
                    end_time = datetime.utcnow()
                    response_time_ms = int((end_time - start_time).total_seconds() * 1000)
                    response_code = response.status_code
                    print(f"健康检查响应 - API: {api.id}, 状态码: {response_code}, 响应时间: {response_time_ms}ms")
                    
                    # 保存响应信息
                    try:
                        response_body = response.text[:10000]  # 限制响应体大小
                        response_headers = json.dumps(dict(response.headers), ensure_ascii=False)[:5000]  # 限制响应头大小
                    except Exception as e:
                        print(f"保存响应信息失败: {e}")
                        pass
                    
                    # 验证状态码
                    if response_code != expected_status:
                        status = HealthCheckStatus.FAILURE
                        error_message = f"HTTP error: {response_code}, expected: {expected_status}"
                        print(f"健康检查失败 - API: {api.id}, 错误: {error_message}")
                    else:
                        # 验证响应体
                        if response_rules and not self._validate_response(response, response_rules):
                            status = HealthCheckStatus.FAILURE
                            error_message = "Response does not match health check rules"
                            print(f"健康检查失败 - API: {api.id}, 错误: {error_message}")
            except httpx.TimeoutException:
                status = HealthCheckStatus.TIMEOUT
                error_message = f"Request timed out after {timeout}ms"
                response_time_ms = timeout
                print(f"健康检查超时 - API: {api.id}, URL: {url}, 超时: {timeout}ms")
            except Exception as e:
                status = HealthCheckStatus.ERROR
                error_message = str(e)
                print(f"健康检查错误 - API: {api.id}, URL: {url}, 错误: {e}")
                import traceback
                traceback.print_exc()
            
            # 构建完整的请求详情
            request_details = {
                "url": url,
                "method": "GET",  # 只使用GET方法
                "headers": headers,
                "timeout": timeout,
                "expected_status": expected_status,
                "response_rules": response_rules
            }
            
            # 保存健康检查结果
            health_check_result = HealthCheckResult(
                id=str(uuid.uuid4()),
                batch_id=batch_id,
                api_id=api.id,
                system_id=api.system_id,
                status=status.value,
                response_code=response_code,
                response_time_ms=response_time_ms,
                error_message=error_message,
                environment=environment,
                response_body=response_body,
                response_headers=response_headers,
                request_url=url,  # 记录请求的URL
                request_details=json.dumps(request_details, ensure_ascii=False),
                checked_at=datetime.utcnow()
            )
            
            try:
                created_result = self.health_check_result_repository.create(health_check_result)
                dto = HealthCheckResultDTO.model_validate(created_result)
                dto.api_id = api.id
                dto.system_id = api.system_id
                dto.environment = environment
                dto.batch_id = batch_id
                dto.response_body = response_body
                dto.response_headers = response_headers
                dto.request_url = url  # 设置请求的URL
                dto.request_details = json.dumps(request_details, ensure_ascii=False)  # 设置完整的请求详情
                print(f"健康检查完成 - API: {api.id}, 状态: {status.value}")
                return dto
            except Exception as e:
                print(f"保存健康检查结果失败: {e}")
                import traceback
                traceback.print_exc()
                return None
        except Exception as e:
            print(f"执行API健康检查失败 - API: {api_id}, 错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _check_endpoint_health(self, endpoint_id: str, environment: str, batch_id: str) -> Optional[HealthCheckResultDTO]:
        """检查端点健康状态（内部方法）"""
        try:
            # 验证端点是否存在
            endpoint = self.endpoint_repository.find_by_id(endpoint_id)
            if not endpoint:
                return None
            
            # 验证API是否存在
            api = self.api_repository.find_by_id(endpoint.api_id)
            if not api:
                return None
            
            # 根据环境选择Host
            if environment == "dev":
                base_url = api.dev_host or api.uat_host or api.prod_host or "http://localhost:8080"
            elif environment == "prod":
                base_url = api.prod_host or api.uat_host or api.dev_host or "http://localhost:8080"
            else:  # uat
                base_url = api.uat_host or api.prod_host or api.dev_host or "http://localhost:8080"
            
            # 构建完整URL - 使用API的健康检查路径
            path = api.health_check_path or '/health'
            if not path.startswith('/'):
                path = '/' + path
            url = f"{base_url.rstrip('/')}{path}"
            
            # 解析健康检查规则
            health_check_rule = None
            if api.health_check_rule:
                try:
                    health_check_rule = json.loads(api.health_check_rule)
                except:
                    pass
            
            expected_status = health_check_rule.get('expected_status', 200) if health_check_rule else 200
            timeout = health_check_rule.get('timeout', 5000) if health_check_rule else 5000
            response_rules = health_check_rule.get('response_rules', []) if health_check_rule else []
            headers = health_check_rule.get('headers', {}) if health_check_rule else {}
            
            # 执行健康检查
            status = HealthCheckStatus.SUCCESS
            response_code = None
            response_time_ms = None
            error_message = None
            response_body = None
            response_headers = None
            
            try:
                start_time = datetime.utcnow()
                async with httpx.AsyncClient(timeout=timeout/1000) as client:
                    if endpoint.http_method == "GET":
                        response = await client.get(url, headers=headers)
                    elif endpoint.http_method == "POST":
                        response = await client.post(url, headers=headers, json={})
                    elif endpoint.http_method == "PUT":
                        response = await client.put(url, headers=headers, json={})
                    elif endpoint.http_method == "DELETE":
                        response = await client.delete(url, headers=headers)
                    else:
                        status = HealthCheckStatus.ERROR
                        error_message = f"Unsupported HTTP method: {endpoint.http_method}"
                        response_code = 0
                    
                    if status == HealthCheckStatus.SUCCESS:
                        end_time = datetime.utcnow()
                        response_time_ms = int((end_time - start_time).total_seconds() * 1000)
                        response_code = response.status_code
                        
                        # 保存响应信息
                        try:
                            response_body = response.text[:10000]  # 限制响应体大小
                            response_headers = json.dumps(dict(response.headers), ensure_ascii=False)[:5000]  # 限制响应头大小
                        except:
                            pass
                        
                        # 验证状态码
                        if response_code != expected_status:
                            status = HealthCheckStatus.FAILURE
                            error_message = f"HTTP error: {response_code}, expected: {expected_status}"
                        else:
                            # 验证响应体
                            if response_rules and not self._validate_response(response, response_rules):
                                status = HealthCheckStatus.FAILURE
                                error_message = "Response does not match health check rules"
            except httpx.TimeoutException:
                status = HealthCheckStatus.TIMEOUT
                error_message = f"Request timed out after {timeout}ms"
                response_time_ms = timeout
            except Exception as e:
                status = HealthCheckStatus.ERROR
                error_message = str(e)
            
            # 构建完整的请求详情
            request_details = {
                "url": url,
                "method": endpoint.http_method,
                "headers": headers,
                "timeout": timeout,
                "expected_status": expected_status,
                "response_rules": response_rules
            }
            
            # 保存健康检查结果
            health_check_result = HealthCheckResult(
                id=str(uuid.uuid4()),
                batch_id=batch_id,
                api_id=api.id,
                system_id=api.system_id,
                status=status.value,
                response_code=response_code,
                response_time_ms=response_time_ms,
                error_message=error_message,
                environment=environment,
                response_body=response_body,
                response_headers=response_headers,
                request_url=url,  # 记录请求的URL
                request_details=json.dumps(request_details, ensure_ascii=False),
                checked_at=datetime.utcnow()
            )
            
            created_result = self.health_check_result_repository.create(health_check_result)
            dto = HealthCheckResultDTO.model_validate(created_result)
            dto.api_id = api.id
            dto.system_id = api.system_id
            dto.environment = environment
            dto.batch_id = batch_id
            dto.response_body = response_body
            dto.response_headers = response_headers
            dto.request_url = url  # 设置请求的URL
            dto.request_details = json.dumps(request_details, ensure_ascii=False)  # 设置完整的请求详情
            return dto
        except Exception:
            return None
    
    async def check_system_health(self, system_id: str, environment: str = "uat") -> BatchHealthCheckResponse:
        """检查系统健康状态"""
        # 验证系统是否存在
        system = self.system_repository.find_by_id(system_id)
        if not system:
            raise ResourceNotFoundException("System", system_id)
        
        # 获取系统下的所有API
        apis = self.api_repository.find_by_system_id(system_id)
        if not apis:
            return BatchHealthCheckResponse(results=[])
        
        # 生成批次ID
        batch_id = str(uuid.uuid4())
        
        # 并发执行健康检查 - 每个API只检查一次，使用GET方法
        tasks = [self._check_api_health(api.id, environment, batch_id) for api in apis]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        valid_results = []
        for result in results:
            if isinstance(result, HealthCheckResultDTO):
                valid_results.append(result)
        
        # 统计结果
        success_count = sum(1 for r in valid_results if r.status == HealthCheckStatus.SUCCESS.value)
        failure_count = len(valid_results) - success_count
        
        return BatchHealthCheckResponse(
            batch_id=batch_id,
            results=valid_results,
            total_count=len(apis),
            success_count=success_count,
            failure_count=failure_count
        )
    
    def get_health_check_results_by_system(self, system_id: str) -> List[HealthCheckResultDTO]:
        """获取系统的健康检查结果"""
        # 验证系统是否存在
        system = self.system_repository.find_by_id(system_id)
        if not system:
            raise ResourceNotFoundException("System", system_id)
        
        results = self.health_check_result_repository.find_by_system_id(system_id)
        return [HealthCheckResultDTO.model_validate(result) for result in results]
    
    def get_health_check_results_by_batch(self, batch_id: str) -> List[HealthCheckResultDTO]:
        """获取批次的健康检查结果"""
        results = self.health_check_result_repository.find_by_batch_id(batch_id)
        return [HealthCheckResultDTO.model_validate(result) for result in results]
    
    def get_health_check_batches(self, system_id: Optional[str] = None, environment: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取健康检查批次列表，支持按系统和环境过滤"""
        return self.health_check_result_repository.find_batches(system_id, environment)
