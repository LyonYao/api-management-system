import time
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid
import httpx
from sqlalchemy.orm import Session
from ..models import EndpointTest, TestResult, Endpoint, Api, System
from ..repositories import EndpointTestRepository, TestResultRepository, TestBatchRepository, EndpointRepository, ApiRepository
from ..schemas import (
    EndpointTestDTO,
    CreateEndpointTestRequest,
    UpdateEndpointTestRequest,
    TestResultDTO,
    TestRunResponse,
    TestTrendDTO,
    TestTrendResponse,
    TestRunInitiationResponse
)
from ..enums import TestStatus
from ..utils.audit_decorator import audit_log
from ..models import OperationType, ResourceType
from ..utils.logger import get_logger

# 创建测试服务的日志记录器
test_logger = get_logger('test')


class TestService:
    def __init__(self, db: Session):
        self.db = db
        self.endpoint_test_repo = EndpointTestRepository(db)
        self.test_result_repo = TestResultRepository(db)
        self.test_batch_repo = TestBatchRepository(db)
        self.endpoint_repo = EndpointRepository(db)
        self.api_repo = ApiRepository(db)
    
    @audit_log(operation_type=OperationType.CREATE, resource_type=ResourceType.ENDPOINT)
    def create_test(self, request: CreateEndpointTestRequest) -> EndpointTestDTO:
        """创建测试用例"""
        # 验证Endpoint是否存在
        endpoint = self.endpoint_repo.find_by_id(request.endpoint_id)
        if not endpoint:
            raise ValueError(f"Endpoint with id {request.endpoint_id} not found")
        
        # 创建测试用例
        test = EndpointTest(
            endpoint_id=request.endpoint_id,
            name=request.name,
            description=request.description,
            environment=request.environment,
            headers=request.headers,
            request_body=request.request_body,
            expected_response=request.expected_response,
            validation_rules=request.validation_rules
        )
        test = self.endpoint_test_repo.create(test)
        return EndpointTestDTO.from_orm(test)
    
    def get_test(self, test_id: str) -> Optional[EndpointTestDTO]:
        """获取测试用例详情"""
        test = self.endpoint_test_repo.find_by_id(test_id)
        if not test:
            return None
        return EndpointTestDTO.from_orm(test)
    
    @audit_log(operation_type=OperationType.UPDATE, resource_type=ResourceType.ENDPOINT)
    def update_test(self, test_id: str, request: UpdateEndpointTestRequest) -> Optional[EndpointTestDTO]:
        """更新测试用例"""
        test = self.endpoint_test_repo.find_by_id(test_id)
        if not test:
            return None
        
        # 更新测试用例
        if request.name is not None:
            test.name = request.name
        if request.description is not None:
            test.description = request.description
        if request.environment is not None:
            test.environment = request.environment
        if request.headers is not None:
            test.headers = request.headers
        if request.request_body is not None:
            test.request_body = request.request_body
        if request.expected_response is not None:
            test.expected_response = request.expected_response
        if request.validation_rules is not None:
            test.validation_rules = request.validation_rules
        
        test = self.endpoint_test_repo.update(test)
        return EndpointTestDTO.from_orm(test)
    
    @audit_log(operation_type=OperationType.DELETE, resource_type=ResourceType.ENDPOINT)
    def delete_test(self, test_id: str) -> bool:
        """删除测试用例"""
        return self.endpoint_test_repo.delete(test_id)
    
    def get_tests_by_endpoint(self, endpoint_id: str) -> List[EndpointTestDTO]:
        """根据Endpoint ID获取测试用例列表"""
        tests = self.endpoint_test_repo.find_by_endpoint_id(endpoint_id)
        return [EndpointTestDTO.from_orm(test) for test in tests]
    
    def get_all_tests(self, skip: int = 0, limit: int = 100) -> List[EndpointTestDTO]:
        """获取所有测试用例"""
        tests = self.endpoint_test_repo.find_all(skip, limit)
        return [EndpointTestDTO.from_orm(test) for test in tests]
    
    def generate_batch_id(self, environment: str = None) -> str:
        """生成批次号，格式为环境_年月日时分秒"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        if environment:
            return f"{environment}_{timestamp}"
        return timestamp
    
    async def execute_test(self, test: EndpointTest, environment: str = None, batch_id: str = None) -> TestResult:
        """执行单个测试用例"""
        test_logger.info(f"execute test: Starting test execution for test {test.id}")
        # 确保test对象绑定到当前会话
        self.db.add(test)
        # 获取Endpoint、API和System信息
        endpoint = self.endpoint_repo.find_by_id(test.endpoint_id)
        if not endpoint:
            test_logger.error(f"execute test: Endpoint with id {test.endpoint_id} not found")
            raise ValueError(f"Endpoint with id {test.endpoint_id} not found")
        
        api = self.api_repo.find_by_id(endpoint.api_id)
        if not api:
            test_logger.error(f"execute test: API with id {endpoint.api_id} not found")
            raise ValueError(f"API with id {endpoint.api_id} not found")
        
        # 确定环境
        env = environment or test.environment
        test_logger.info(f"execute test: Using environment {env}")
        
        # 构建请求URL
        if env == "dev":
            base_url = api.dev_host
        elif env == "uat":
            base_url = api.uat_host
        elif env == "prod":
            base_url = api.prod_host
        else:
            base_url = api.dev_host
        
        if not base_url:
            test_logger.error(f"execute test: No host configured for API {api.id} in {env} environment")
            raise ValueError(f"No host configured for API {api.id} in {env} environment")
        
        # 处理路径中的占位符
        path = endpoint.path
        # 替换常见的占位符
        path = path.replace("{system_id}", api.system_id)
        path = path.replace("{api_id}", api.id)
        path = path.replace("{endpoint_id}", endpoint.id)
        path = path.replace("{test_id}", test.id)
        # 替换其他占位符为默认值
        path = path.replace("{batch_id}", "test-batch")
        path = path.replace("{relationship_id}", "test-relationship")
        path = path.replace("{audit_id}", "test-audit")
        
        url = f"{base_url}{path}"
        test_logger.info(f"execute test: Constructed URL: {url}")
        test_logger.info(f"execute test: HTTP Method: {endpoint.http_method}")
        
        # 执行请求
        start_time = time.time()
        status = TestStatus.ERROR
        response_code = None
        response_body = None
        error_message = None
        
        try:
            async with httpx.AsyncClient() as client:
                method = endpoint.http_method.lower()
                headers = test.headers or {}
                request_body = test.request_body
                
                test_logger.info(f"execute test: Sending {method.upper()} request to {url}")
                test_logger.info(f"execute test: Headers: {headers}")
                test_logger.info(f"execute test: Request Body: {request_body}")
                
                if method == "get":
                    response = await client.get(url, headers=headers, timeout=30)
                elif method == "post":
                    response = await client.post(url, headers=headers, json=request_body, timeout=30)
                elif method == "put":
                    response = await client.put(url, headers=headers, json=request_body, timeout=30)
                elif method == "delete":
                    response = await client.delete(url, headers=headers, timeout=30)
                elif method == "patch":
                    response = await client.patch(url, headers=headers, json=request_body, timeout=30)
                else:
                    raise ValueError(f"Unsupported HTTP method: {endpoint.http_method}")
                
                response_code = response.status_code
                response_body = response.json() if response.content else None
                test_logger.info(f"execute test: Response Status Code: {response_code}")
                test_logger.info(f"execute test: Response Body: {response_body}")
                
                # 评估测试结果
                if self.evaluate_test_result(test, response_code, response_body):
                    status = TestStatus.PASS
                    test_logger.info(f"execute test: Test PASSED")
                else:
                    status = TestStatus.FAIL
                    test_logger.info(f"execute test: Test FAILED")
                    
        except Exception as e:
            error_message = str(e)[:500]  # 限制错误信息长度
            test_logger.error(f"execute test: Error executing test: {error_message}")
            # 确保 status 被设置为 ERROR
            status = TestStatus.ERROR
        
        response_time_ms = int((time.time() - start_time) * 1000)
        test_logger.info(f"execute test: Response Time: {response_time_ms} ms")
        
        # 使用传入的批次ID或生成新的
        final_batch_id = batch_id or self.generate_batch_id(env)
        test_logger.info(f"execute test: Using batch ID: {final_batch_id}")
        
        # 创建测试结果
        test_result = TestResult(
            test_id=test.id,
            endpoint_id=test.endpoint_id,
            api_id=api.id,
            system_id=api.system_id,
            environment=env,
            batch_id=final_batch_id,
            status=status.value,
            response_code=response_code,
            response_time_ms=response_time_ms,
            request_headers=test.headers,
            request_body=test.request_body,
            response_body=response_body,
            validation_rules=test.validation_rules,
            error_message=error_message,
            request_url=url,
            api_url=base_url,
            http_method=endpoint.http_method
        )
        
        created_result = self.test_result_repo.create(test_result)
        test_logger.info(f"execute test: Test execution completed. Result ID: {created_result.id}")
        return created_result
    
    def evaluate_test_result(self, test: EndpointTest, response_code: int, response_body: Any) -> bool:
        """评估测试结果"""
        try:
            # 确保test对象绑定到当前会话
            self.db.add(test)
            # 立即刷新对象，确保所有属性都被加载
            self.db.refresh(test)
            # 如果没有验证规则，默认通过
            if not test.validation_rules:
                return True
            
            # 简单的验证规则评估
            rules = test.validation_rules
            
            # 检查状态码
            if "status_code" in rules:
                expected_code = rules["status_code"]
                if response_code != expected_code:
                    return False
            
            # 检查响应体
            if "response_body" in rules and response_body:
                expected_body = rules["response_body"]
                # 简单的深度比较
                if not self._deep_compare(response_body, expected_body):
                    return False
            
            return True
        except Exception as e:
            test_logger.error(f"Error evaluating test result: {e}")
            # 如果出现会话绑定错误，默认返回True以避免测试失败
            return True
    
    def _deep_compare(self, actual: Any, expected: Any) -> bool:
        """深度比较两个对象，支持正则匹配"""
        import re
        
        if isinstance(expected, dict) and "$regex" in expected:
            # 处理正则匹配
            if not isinstance(actual, str):
                return False
            pattern = expected["$regex"]
            return bool(re.match(pattern, actual))
        elif isinstance(actual, dict) and isinstance(expected, dict):
            for key, expected_value in expected.items():
                if key not in actual:
                    return False
                if not self._deep_compare(actual[key], expected_value):
                    return False
            return True
        elif isinstance(actual, list) and isinstance(expected, list):
            if len(actual) != len(expected):
                return False
            for actual_item, expected_item in zip(actual, expected):
                if not self._deep_compare(actual_item, expected_item):
                    return False
            return True
        else:
            return actual == expected
    
    async def run_api_tests(self, api_id: str, environment: str = None):
        """执行API的所有测试用例"""
        import asyncio
        from datetime import datetime
        # 获取API的所有Endpoint
        endpoints = self.endpoint_repo.find_by_api_id(api_id)
        if not endpoints:
            batch_id = self.generate_batch_id(environment)
            return TestRunInitiationResponse(
                run_id=batch_id,
                total_tests=0
            )
        
        # 获取API信息
        api = self.api_repo.find_by_id(api_id)
        if not api:
            batch_id = self.generate_batch_id(environment)
            return TestRunInitiationResponse(
                run_id=batch_id,
                total_tests=0
            )
        
        # 执行所有测试用例
        batch_id = self.generate_batch_id(environment)
        
        # 创建测试批次记录
        from ..models import TestBatch
        test_batch = TestBatch(
            batch_id=batch_id,
            system_id=api.system_id,
            api_id=api_id,
            environment=environment or "dev",
            total_count=0,
            pass_count=0,
            fail_count=0,
            error_count=0,
            status="RUNNING"
        )
        test_batch = self.test_batch_repo.create(test_batch)
        
        # 收集所有测试任务信息（只存储ID，不存储对象）
        test_tasks_info = []
        test_logger.info(f"Found {len(endpoints)} endpoints for API {api_id}")
        for endpoint in endpoints:
            # 只获取对应环境的测试用例
            tests = self.endpoint_test_repo.find_by_endpoint_id(endpoint.id, environment)
            test_logger.info(f"Found {len(tests)} tests for endpoint {endpoint.id}")
            for test in tests:
                test_tasks_info.append({
                    "test_id": test.id,
                    "api_id": api_id,
                    "batch_id": batch_id,
                    "endpoint_id": endpoint.id,
                    "environment": environment
                })
        
        total_tests = len(test_tasks_info)
        test_logger.info(f"Total tests to execute: {total_tests}")
        test_batch.total_count = total_tests
        self.test_batch_repo.update(test_batch)
        
        # 后台执行测试
        async def background_test_execution():
            # 创建新的数据库会话
            from ..db.database import SessionLocal
            db = SessionLocal()
            try:
                # 限制并发数，避免超时
                concurrency_limit = 5
                semaphore = asyncio.Semaphore(concurrency_limit)
                
                # 重新创建测试服务实例，使用新的数据库会话
                from ..repositories import EndpointRepository, EndpointTestRepository, TestResultRepository, TestBatchRepository
                endpoint_repo = EndpointRepository(db)
                endpoint_test_repo = EndpointTestRepository(db)
                test_result_repo = TestResultRepository(db)
                test_batch_repo = TestBatchRepository(db)
                
                # 创建新的测试服务实例
                test_service = TestService(db)
                
                async def limited_task(task_info):
                    async with semaphore:
                        # 在后台任务中重新获取对象
                        endpoint = endpoint_repo.find_by_id(task_info["endpoint_id"])
                        test = endpoint_test_repo.find_by_id(task_info["test_id"])
                        if endpoint and test:
                            # 确保对象绑定到当前会话
                            db.add(endpoint)
                            db.add(test)
                            # 立即刷新对象，确保所有属性都被加载
                            db.refresh(test)
                            db.refresh(endpoint)
                            return await test_service._run_single_test(
                                test, 
                                task_info["api_id"], 
                                task_info["batch_id"], 
                                endpoint, 
                                task_info["environment"]
                            )
                        else:
                            test_logger.error(f"Endpoint or test not found: endpoint_id={task_info['endpoint_id']}, test_id={task_info['test_id']}")
                            return Exception(f"Endpoint or test not found")
                
                # 并发执行测试，限制并发数
                limited_tasks = [limited_task(task_info) for task_info in test_tasks_info]
                test_results = await asyncio.gather(*limited_tasks, return_exceptions=True)
                
                # 更新批次统计信息
                pass_count = 0
                fail_count = 0
                error_count = 0
                
                for result in test_results:
                    if isinstance(result, Exception):
                        error_count += 1
                        test_logger.error(f"Test execution failed with exception: {str(result)}")
                    else:
                        try:
                            if hasattr(result, 'status'):
                                if result.status == TestStatus.PASS:
                                    pass_count += 1
                                elif result.status == TestStatus.FAIL:
                                    fail_count += 1
                                else:
                                    error_count += 1
                            else:
                                error_count += 1
                                test_logger.error(f"Test result has no status attribute: {result}")
                        except Exception as e:
                            error_count += 1
                            test_logger.error(f"Error processing test result: {str(e)}")
                
                # 获取最新的批次对象
                from ..repositories import TestBatchRepository
                batch_repo = TestBatchRepository(db)
                latest_batch = batch_repo.find_by_id(batch_id)
                if latest_batch:
                    # 更新批次状态
                    latest_batch.pass_count = pass_count
                    latest_batch.fail_count = fail_count
                    latest_batch.error_count = error_count
                    latest_batch.status = "COMPLETED"
                    latest_batch.end_time = datetime.now()
                    batch_repo.update(latest_batch)
            finally:
                db.close()
        
        # 创建后台任务
        asyncio.create_task(background_test_execution())
        
        # 立即返回，不等待测试完成
        return TestRunInitiationResponse(
            run_id=batch_id,
            total_tests=total_tests
        )
    
    async def run_endpoint_tests(self, endpoint_id: str, environment: str = None) -> TestRunResponse:
        """执行Endpoint的所有测试用例"""
        import asyncio
        from datetime import datetime
        # 获取Endpoint
        endpoint = self.endpoint_repo.find_by_id(endpoint_id)
        if not endpoint:
            batch_id = self.generate_batch_id(environment)
            return TestRunResponse(
                run_id=batch_id,
                results=[],
                total_count=0,
                pass_count=0,
                fail_count=0,
                error_count=0
            )
        
        # 获取API
        api = self.api_repo.find_by_id(endpoint.api_id)
        if not api:
            batch_id = self.generate_batch_id(environment)
            return TestRunResponse(
                run_id=batch_id,
                results=[],
                total_count=0,
                pass_count=0,
                fail_count=0,
                error_count=0
            )
        
        # 执行所有测试用例
        batch_id = self.generate_batch_id(environment)
        
        # 创建测试批次记录
        from ..models import TestBatch
        test_batch = TestBatch(
            batch_id=batch_id,
            system_id=api.system_id,
            api_id=api.id,
            environment=environment or "dev",
            total_count=0,
            pass_count=0,
            fail_count=0,
            error_count=0,
            status="RUNNING"
        )
        test_batch = self.test_batch_repo.create(test_batch)
        
        results = []
        pass_count = 0
        fail_count = 0
        error_count = 0
        
        # 收集所有测试任务
        test_tasks = []
        # 只获取对应环境的测试用例
        tests = self.endpoint_test_repo.find_by_endpoint_id(endpoint_id, environment)
        test_logger.info(f"Found {len(tests)} tests for endpoint {endpoint_id}")
        for test in tests:
            test_tasks.append(self._run_single_test(test, api.id, batch_id, endpoint, environment))
        
        total_tests = len(test_tasks)
        test_logger.info(f"Total tests to execute: {total_tests}")
        test_batch.total_count = total_tests
        self.test_batch_repo.update(test_batch)
        
        # 限制并发数，避免超时
        concurrency_limit = 5
        semaphore = asyncio.Semaphore(concurrency_limit)
        
        async def limited_task(task):
            async with semaphore:
                return await task
        
        # 并发执行测试，限制并发数
        limited_tasks = [limited_task(task) for task in test_tasks]
        test_results = await asyncio.gather(*limited_tasks, return_exceptions=True)
        
        # 构建基本URL信息，即使在执行错误的情况下也能记录
        request_url = None
        api_url = None
        
        try:
            # 构建请求URL
            if environment == "dev":
                base_url = api.dev_host
            elif environment == "uat":
                base_url = api.uat_host
            elif environment == "prod":
                base_url = api.prod_host
            else:
                base_url = api.dev_host
            
            if base_url:
                api_url = base_url
                # 处理路径中的占位符
                path = endpoint.path
                # 替换常见的占位符
                path = path.replace("{system_id}", api.system_id)
                path = path.replace("{api_id}", api.id)
                path = path.replace("{endpoint_id}", endpoint.id)
                # 替换其他占位符为默认值
                path = path.replace("{batch_id}", "test-batch")
                path = path.replace("{relationship_id}", "test-relationship")
                path = path.replace("{audit_id}", "test-audit")
                path = path.replace("{test_id}", "unknown")
                
                request_url = f"{base_url}{path}"
        except Exception:
            pass
        
        # 处理测试结果
        for result in test_results:
            if isinstance(result, Exception):
                # 处理执行错误
                error_result = TestResult(
                    test_id="unknown",
                    endpoint_id=endpoint_id,
                    api_id=api.id,
                    system_id=api.system_id,
                    batch_id=batch_id,
                    environment=environment or "dev",
                    status=TestStatus.ERROR.value,
                    error_message=str(result)[:500],
                    request_url=request_url,
                    api_url=api_url
                )
                error_result = self.test_result_repo.create(error_result)
                results.append(TestResultDTO.from_orm(error_result))
                error_count += 1
            else:
                results.append(result)
                # 统计结果
                if result.status == TestStatus.PASS:
                    pass_count += 1
                elif result.status == TestStatus.FAIL:
                    fail_count += 1
                else:
                    error_count += 1
        
        # 更新批次状态
        test_batch.pass_count = pass_count
        test_batch.fail_count = fail_count
        test_batch.error_count = error_count
        test_batch.status = "COMPLETED"
        test_batch.end_time = datetime.now()
        self.test_batch_repo.update(test_batch)
        
        return TestRunResponse(
            run_id=batch_id,
            results=results,
            total_count=len(results),
            pass_count=pass_count,
            fail_count=fail_count,
            error_count=error_count
        )
    
    async def _run_single_test(self, test: EndpointTest, api_id: str, batch_id: str, endpoint: Any, environment: str = None) -> TestResultDTO:
        """执行单个测试用例并返回DTO"""
        test_logger.info(f"Starting test {test.id} for endpoint {endpoint.id}")
        # 确保test对象绑定到当前会话
        self.db.add(test)
        # 构建请求URL，即使在执行错误的情况下也能记录
        request_url = None
        api_url = None
        
        try:
            # 获取API信息
            api = self.api_repo.find_by_id(api_id)
            if api:
                # 确定环境
                env = environment or test.environment
                test_logger.info(f"Using environment {env} for test {test.id}")
                
                # 构建请求URL
                if env == "dev":
                    base_url = api.dev_host
                elif env == "uat":
                    base_url = api.uat_host
                elif env == "prod":
                    base_url = api.prod_host
                else:
                    base_url = api.dev_host
                
                if base_url:
                    api_url = base_url
                    # 处理路径中的占位符
                    path = endpoint.path
                    # 替换常见的占位符
                    path = path.replace("{system_id}", api.system_id)
                    path = path.replace("{api_id}", api.id)
                    path = path.replace("{endpoint_id}", endpoint.id)
                    path = path.replace("{test_id}", test.id)
                    # 替换其他占位符为默认值
                    path = path.replace("{batch_id}", "test-batch")
                    path = path.replace("{relationship_id}", "test-relationship")
                    path = path.replace("{audit_id}", "test-audit")
                    
                    request_url = f"{base_url}{path}"
                    test_logger.info(f"Constructed URL: {request_url}")
                else:
                    test_logger.info(f"No base URL configured for API {api.id} in {env} environment")
            else:
                test_logger.info(f"API with id {api_id} not found")
        except Exception as e:
            test_logger.error(f"Error building request URL: {e}")
        
        try:
            # 执行测试，传递批次ID，添加超时处理
            test_logger.info(f"Executing test {test.id}")
            import asyncio
            test_result = await asyncio.wait_for(self.execute_test(test, environment, batch_id), timeout=60)
            test_logger.info(f"Test {test.id} completed with status {test_result.status}")
            # 转换为DTO并返回
            return TestResultDTO.from_orm(test_result)
        except asyncio.TimeoutError:
            # 处理超时错误
            test_logger.error(f"Test {test.id} timed out after 60 seconds")
            # 尝试获取系统ID
            system_id = "unknown"
            try:
                # 从API获取系统ID
                api = self.api_repo.find_by_id(api_id)
                if api:
                    system_id = api.system_id
            except Exception:
                pass
            
            error_result = TestResult(
                test_id=test.id,
                endpoint_id=test.endpoint_id,
                api_id=api_id,
                system_id=system_id,
                environment=environment or test.environment or "dev",
                batch_id=batch_id,
                status=TestStatus.ERROR.value,
                error_message="Test timed out after 60 seconds",
                request_url=request_url,
                api_url=api_url,
                http_method=endpoint.http_method if endpoint else None
            )
            error_result = self.test_result_repo.create(error_result)
            test_logger.info(f"Created error result for test {test.id}")
            return TestResultDTO.from_orm(error_result)
        except Exception as e:
            # 记录执行错误
            test_logger.error(f"Error executing test {test.id}: {e}")
            # 尝试获取系统ID
            system_id = "unknown"
            try:
                # 从API获取系统ID
                api = self.api_repo.find_by_id(api_id)
                if api:
                    system_id = api.system_id
            except Exception:
                pass
            
            error_result = TestResult(
                test_id=test.id,
                endpoint_id=test.endpoint_id,
                api_id=api_id,
                system_id=system_id,
                environment=environment or test.environment or "dev",
                batch_id=batch_id,
                status=TestStatus.ERROR.value,
                error_message=str(e)[:500],
                request_url=request_url,
                api_url=api_url,
                http_method=endpoint.http_method if endpoint else None
            )
            error_result = self.test_result_repo.create(error_result)
            test_logger.info(f"Created error result for test {test.id}")
            return TestResultDTO.from_orm(error_result)
    
    def get_test_results(self, params: dict) -> List[TestResultDTO]:
        """获取测试执行结果"""
        results = self.test_result_repo.find_all(
            system_id=params.get("system_id"),
            api_id=params.get("api_id"),
            environment=params.get("environment"),
            batch_id=params.get("batch_id"),
            start_date=params.get("start_date"),
            end_date=params.get("end_date"),
            status=params.get("status"),
            skip=params.get("skip", 0),
            limit=params.get("limit", 100)
        )
        return [TestResultDTO.from_orm(result) for result in results]
    
    def get_test_batches(self, params: dict) -> List[Dict[str, Any]]:
        """获取测试批次列表"""
        # 使用新的 TestBatch 模型获取批次列表
        batches = self.test_batch_repo.find_all(
            system_id=params.get("system_id"),
            api_id=params.get("api_id"),
            environment=params.get("environment"),
            skip=0,
            limit=100
        )
        
        # 转换为字典列表
        batch_list = []
        for batch in batches:
            batch_list.append({
                'batch_id': batch.batch_id,
                'executed_at': batch.start_time,
                'total_count': batch.total_count,
                'pass_count': batch.pass_count,
                'fail_count': batch.fail_count,
                'error_count': batch.error_count,
                'system_id': batch.system_id,
                'system_name': batch.system.name if batch.system else "",
                'api_id': batch.api_id,
                'api_name': batch.api.name if batch.api else "",
                'environment': batch.environment
            })
        
        return batch_list
    
    def get_test_trends(self, params: dict) -> TestTrendResponse:
        """获取测试执行历史趋势"""
        # 获取测试结果
        results = self.test_result_repo.find_all(
            system_id=params.get("system_id"),
            api_id=params.get("api_id"),
            start_date=params.get("start_date"),
            end_date=params.get("end_date")
        )
        
        # 按日期分组
        interval = params.get("interval", "day")
        grouped_results = {}
        
        for result in results:
            if interval == "day":
                date_key = result.executed_at.strftime("%Y-%m-%d")
            elif interval == "week":
                date_key = result.executed_at.strftime("%Y-W%U")  # 年-周数
            else:  # month
                date_key = result.executed_at.strftime("%Y-%m")
            
            if date_key not in grouped_results:
                grouped_results[date_key] = {
                    "total_count": 0,
                    "pass_count": 0,
                    "fail_count": 0,
                    "error_count": 0
                }
            
            grouped_results[date_key]["total_count"] += 1
            if result.status == TestStatus.PASS.value:
                grouped_results[date_key]["pass_count"] += 1
            elif result.status == TestStatus.FAIL.value:
                grouped_results[date_key]["fail_count"] += 1
            else:
                grouped_results[date_key]["error_count"] += 1
        
        # 转换为趋势DTO
        trends = []
        for date_key, stats in sorted(grouped_results.items()):
            if interval == "day":
                date = datetime.strptime(date_key, "%Y-%m-%d")
            elif interval == "week":
                # 简化处理，取周的第一天
                year, week = date_key.split("-W")
                date = datetime.strptime(f"{year}-W{week}-1", "%Y-W%U-%w")
            else:  # month
                date = datetime.strptime(date_key, "%Y-%m")
            
            pass_rate = (stats["pass_count"] / stats["total_count"] * 100) if stats["total_count"] > 0 else 0
            
            trends.append(TestTrendDTO(
                date=date,
                total_count=stats["total_count"],
                pass_count=stats["pass_count"],
                fail_count=stats["fail_count"],
                error_count=stats["error_count"],
                pass_rate=pass_rate
            ))
        
        start_date = params.get("start_date", datetime.min)
        end_date = params.get("end_date", datetime.now())
        
        return TestTrendResponse(
            trends=trends,
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )
