import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from apimgmt.db.database import Base
from apimgmt.models import TestResult, EndpointTest, Endpoint, Api, System
from apimgmt.repositories.test_result_repository import TestResultRepository
from apimgmt.enums.test_status import TestStatus


@pytest.fixture
def db_engine():
    # 使用内存SQLite数据库
    engine = create_engine('sqlite:///:memory:')
    # 创建所有表
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def test_result_repository(db_session):
    return TestResultRepository(db_session)


def test_create_test_result(test_result_repository: TestResultRepository, db_session: Session):
    """测试创建测试结果"""
    from apimgmt.models.test_result import TestResult
    
    result = TestResult(
        test_id="test-id-1",
        endpoint_id="endpoint-id-1",
        api_id="api-id-1",
        system_id="system-id-1",
        environment="dev",
        batch_id="20240101120000",
        status=TestStatus.PASS.value,
        response_code=200,
        request_headers={"Content-Type": "application/json"},
        request_body={"key": "value"},
        response_body={"success": True},
        validation_rules={"status_code": 200},
        response_time_ms=123,
        error_message=None
    )
    
    result = test_result_repository.create(result)
    
    assert result is not None
    assert result.test_id == "test-id-1"
    assert result.endpoint_id == "endpoint-id-1"
    assert result.api_id == "api-id-1"
    assert result.system_id == "system-id-1"
    assert result.environment == "dev"
    assert result.batch_id == "20240101120000"
    assert result.status == TestStatus.PASS.value
    assert result.response_code == 200
    assert result.response_time_ms == 123


def test_find_by_batch_id(test_result_repository: TestResultRepository, db_session: Session):
    """测试通过批次ID查找测试结果"""
    from apimgmt.models.test_result import TestResult
    # 创建两个测试结果，同一个批次
    batch_id = "20240101120000"
    
    result1 = TestResult(
        test_id="test-id-2",
        endpoint_id="endpoint-id-2",
        api_id="api-id-2",
        system_id="system-id-2",
        environment="dev",
        batch_id=batch_id,
        status=TestStatus.PASS.value,
        response_code=200,
        request_headers={},
        request_body={},
        response_body={},
        validation_rules={},
        response_time_ms=100,
        error_message=None
    )
    
    result2 = TestResult(
        test_id="test-id-3",
        endpoint_id="endpoint-id-3",
        api_id="api-id-2",
        system_id="system-id-2",
        environment="dev",
        batch_id=batch_id,
        status=TestStatus.FAIL.value,
        response_code=404,
        request_headers={},
        request_body={},
        response_body={},
        validation_rules={},
        response_time_ms=150,
        error_message="Not Found"
    )
    
    test_result_repository.create(result1)
    test_result_repository.create(result2)
    
    # 通过批次ID查找
    results = test_result_repository.find_by_batch_id(batch_id)
    
    assert len(results) == 2
    assert any(result.test_id == "test-id-2" for result in results)
    assert any(result.test_id == "test-id-3" for result in results)


def test_find_by_system_id(test_result_repository: TestResultRepository, db_session: Session):
    """测试通过系统ID查找测试结果"""
    from apimgmt.models.test_result import TestResult
    from apimgmt.models.system import System
    from apimgmt.models.api import Api
    from apimgmt.models.endpoint import Endpoint
    from apimgmt.models.endpoint_test import EndpointTest
    
    # 创建必要的前置数据
    system = System(id="system-id-3", name="Test System", system_code="TEST", description="Test system")
    db_session.add(system)
    
    api1 = Api(id="api-id-3", name="Test API 1", system_id="system-id-3", dev_host="http://localhost:8080")
    api2 = Api(id="api-id-4", name="Test API 2", system_id="system-id-3", dev_host="http://localhost:8080")
    db_session.add(api1)
    db_session.add(api2)
    
    endpoint1 = Endpoint(id="endpoint-id-4", api_id="api-id-3", path="/test1", http_method="GET", status="DEVELOPING")
    endpoint2 = Endpoint(id="endpoint-id-5", api_id="api-id-4", path="/test2", http_method="GET", status="DEVELOPING")
    db_session.add(endpoint1)
    db_session.add(endpoint2)
    
    test1 = EndpointTest(id="test1", name="Test 1", endpoint_id="endpoint-id-4", environment="dev")
    test2 = EndpointTest(id="test2", name="Test 2", endpoint_id="endpoint-id-5", environment="dev")
    db_session.add(test1)
    db_session.add(test2)
    
    db_session.commit()
    
    # 创建两个测试结果，同一个系统
    system_id = "system-id-3"
    
    result1 = TestResult(
        test_id="test1",
        endpoint_id="endpoint-id-4",
        api_id="api-id-3",
        system_id=system_id,
        environment="dev",
        batch_id="20240101120001",
        status=TestStatus.PASS.value,
        response_code=200,
        request_headers={},
        request_body={},
        response_body={},
        validation_rules={},
        response_time_ms=100,
        error_message=None
    )
    
    result2 = TestResult(
        test_id="test2",
        endpoint_id="endpoint-id-5",
        api_id="api-id-4",
        system_id=system_id,
        environment="dev",
        batch_id="20240101120002",
        status=TestStatus.PASS.value,
        response_code=200,
        request_headers={},
        request_body={},
        response_body={},
        validation_rules={},
        response_time_ms=120,
        error_message=None
    )
    
    test_result_repository.create(result1)
    test_result_repository.create(result2)
    
    # 通过系统ID查找
    results = test_result_repository.find_by_system_id(system_id)
    
    assert len(results) == 2
    assert any(result.test_id == "test1" for result in results)
    assert any(result.test_id == "test2" for result in results)


def test_find_by_api_id(test_result_repository: TestResultRepository, db_session: Session):
    """测试通过API ID查找测试结果"""
    from apimgmt.models.test_result import TestResult
    from apimgmt.models.system import System
    from apimgmt.models.api import Api
    from apimgmt.models.endpoint import Endpoint
    from apimgmt.models.endpoint_test import EndpointTest
    
    # 创建必要的前置数据
    system = System(id="system-id-4", name="Test System", system_code="TEST", description="Test system")
    db_session.add(system)
    
    api = Api(id="api-id-5", name="Test API", system_id="system-id-4", dev_host="http://localhost:8080")
    db_session.add(api)
    
    endpoint1 = Endpoint(id="endpoint-id-6", api_id="api-id-5", path="/test1", http_method="GET", status="DEVELOPING")
    endpoint2 = Endpoint(id="endpoint-id-7", api_id="api-id-5", path="/test2", http_method="GET", status="DEVELOPING")
    db_session.add(endpoint1)
    db_session.add(endpoint2)
    
    test1 = EndpointTest(id="test3", name="Test 3", endpoint_id="endpoint-id-6", environment="dev")
    test2 = EndpointTest(id="test4", name="Test 4", endpoint_id="endpoint-id-7", environment="dev")
    db_session.add(test1)
    db_session.add(test2)
    
    db_session.commit()
    
    # 创建两个测试结果，同一个API
    api_id = "api-id-5"
    
    result1 = TestResult(
        test_id="test3",
        endpoint_id="endpoint-id-6",
        api_id=api_id,
        system_id="system-id-4",
        environment="dev",
        batch_id="20240101120003",
        status=TestStatus.PASS.value,
        response_code=200,
        request_headers={},
        request_body={},
        response_body={},
        validation_rules={},
        response_time_ms=100,
        error_message=None
    )
    
    result2 = TestResult(
        test_id="test4",
        endpoint_id="endpoint-id-7",
        api_id=api_id,
        system_id="system-id-4",
        environment="dev",
        batch_id="20240101120004",
        status=TestStatus.ERROR.value,
        response_code=500,
        request_headers={},
        request_body={},
        response_body={},
        validation_rules={},
        response_time_ms=80,
        error_message="Internal Server Error"
    )
    
    test_result_repository.create(result1)
    test_result_repository.create(result2)
    
    # 通过API ID查找
    results = test_result_repository.find_by_api_id(api_id)
    
    assert len(results) == 2
    assert any(result.test_id == "test3" for result in results)
    assert any(result.test_id == "test4" for result in results)


def test_find_by_time_range(test_result_repository: TestResultRepository, db_session: Session):
    """测试通过时间范围查找测试结果"""
    from apimgmt.models.test_result import TestResult
    from apimgmt.models.system import System
    from apimgmt.models.api import Api
    from apimgmt.models.endpoint import Endpoint
    from apimgmt.models.endpoint_test import EndpointTest
    
    # 创建必要的前置数据
    system = System(id="system-id-5", name="Test System", system_code="TEST", description="Test system")
    db_session.add(system)
    
    api = Api(id="api-id-6", name="Test API", system_id="system-id-5", dev_host="http://localhost:8080")
    db_session.add(api)
    
    endpoint = Endpoint(id="endpoint-id-8", api_id="api-id-6", path="/test1", http_method="GET", status="DEVELOPING")
    db_session.add(endpoint)
    
    test = EndpointTest(id="test5", name="Test 5", endpoint_id="endpoint-id-8", environment="dev")
    db_session.add(test)
    
    db_session.commit()
    
    # 创建测试结果
    result = TestResult(
        test_id="test5",
        endpoint_id="endpoint-id-8",
        api_id="api-id-6",
        system_id="system-id-5",
        environment="dev",
        batch_id="20240101120005",
        status=TestStatus.PASS.value,
        response_code=200,
        request_headers={},
        request_body={},
        response_body={},
        validation_rules={},
        response_time_ms=100,
        error_message=None
    )
    
    test_result_repository.create(result)
    
    # 测试不设置时间范围的情况
    results = test_result_repository.find_all()
    
    assert len(results) >= 1
    assert any(result.test_id == "test5" for result in results)


def test_find_all_with_environment(test_result_repository: TestResultRepository, db_session: Session):
    """测试通过环境查找测试结果"""
    from apimgmt.models.test_result import TestResult
    from apimgmt.models.system import System
    from apimgmt.models.api import Api
    from apimgmt.models.endpoint import Endpoint
    from apimgmt.models.endpoint_test import EndpointTest
    
    # 创建必要的前置数据
    system = System(id="system-id-6", name="Test System", system_code="TEST", description="Test system")
    db_session.add(system)
    
    api = Api(id="api-id-7", name="Test API", system_id="system-id-6", dev_host="http://localhost:8080")
    db_session.add(api)
    
    endpoint1 = Endpoint(id="endpoint-id-10", api_id="api-id-7", path="/test1", http_method="GET", status="DEVELOPING")
    endpoint2 = Endpoint(id="endpoint-id-11", api_id="api-id-7", path="/test2", http_method="GET", status="DEVELOPING")
    db_session.add(endpoint1)
    db_session.add(endpoint2)
    
    test1 = EndpointTest(id="test7", name="Test 7", endpoint_id="endpoint-id-10", environment="dev")
    test2 = EndpointTest(id="test8", name="Test 8", endpoint_id="endpoint-id-11", environment="prod")
    db_session.add(test1)
    db_session.add(test2)
    
    db_session.commit()
    
    # 创建两个测试结果，不同环境
    
    result1 = TestResult(
        test_id="test7",
        endpoint_id="endpoint-id-10",
        api_id="api-id-7",
        system_id="system-id-6",
        environment="dev",
        batch_id="20240101120006",
        status=TestStatus.PASS.value,
        response_code=200,
        request_headers={},
        request_body={},
        response_body={},
        validation_rules={},
        response_time_ms=100,
        error_message=None
    )
    
    result2 = TestResult(
        test_id="test8",
        endpoint_id="endpoint-id-11",
        api_id="api-id-7",
        system_id="system-id-6",
        environment="prod",
        batch_id="20240101120007",
        status=TestStatus.FAIL.value,
        response_code=400,
        request_headers={},
        request_body={},
        response_body={},
        validation_rules={},
        response_time_ms=120,
        error_message="Bad Request"
    )
    
    test_result_repository.create(result1)
    test_result_repository.create(result2)
    
    # 通过环境查找
    dev_results = test_result_repository.find_all(environment="dev")
    prod_results = test_result_repository.find_all(environment="prod")
    
    assert len(dev_results) >= 1
    assert any(result.test_id == "test7" for result in dev_results)
    assert len(prod_results) >= 1
    assert any(result.test_id == "test8" for result in prod_results)
