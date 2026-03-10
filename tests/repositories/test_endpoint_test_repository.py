import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from apimgmt.db.database import Base
from apimgmt.models import EndpointTest, System, Api, Endpoint
from apimgmt.repositories.endpoint_test_repository import EndpointTestRepository


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
def endpoint_test_repository(db_session):
    return EndpointTestRepository(db_session)


def test_create_endpoint_test(endpoint_test_repository: EndpointTestRepository, db_session: Session):
    """测试创建测试用例"""
    from apimgmt.models.endpoint_test import EndpointTest
    from apimgmt.models.system import System
    from apimgmt.models.api import Api
    from apimgmt.models.endpoint import Endpoint
    
    # 创建必要的前置数据
    system = System(id="system-test", name="Test System", system_code="TEST", description="Test system")
    db_session.add(system)
    
    api = Api(id="api-test", name="Test API", system_id="system-test", dev_host="http://localhost:8080")
    db_session.add(api)
    
    endpoint = Endpoint(id="test-endpoint-id", api_id="api-test", path="/test", http_method="GET", status="DEVELOPING")
    db_session.add(endpoint)
    db_session.commit()
    
    test = EndpointTest(
        name="Test Case 1",
        description="Test description",
        endpoint_id="test-endpoint-id",
        environment="dev",
        headers={"Content-Type": "application/json"},
        request_body={"key": "value"},
        expected_response={},  # 添加expected_response字段
        validation_rules={"status_code": 200, "body": {"success": True}}
    )
    
    test = endpoint_test_repository.create(test)
    
    assert test is not None
    assert test.name == "Test Case 1"
    assert test.description == "Test description"
    assert test.endpoint_id == "test-endpoint-id"
    assert test.environment == "dev"
    assert test.headers == {"Content-Type": "application/json"}
    assert test.request_body == {"key": "value"}
    assert test.validation_rules == {"status_code": 200, "body": {"success": True}}


def test_find_by_id(endpoint_test_repository: EndpointTestRepository, db_session: Session):
    """测试通过ID查找测试用例"""
    from apimgmt.models.endpoint_test import EndpointTest
    # 先创建一个测试用例
    test = EndpointTest(
        name="Test Case 2",
        description="Test description",
        endpoint_id="test-endpoint-id-2",
        environment="dev",
        headers={},
        request_body={},
        expected_response={},
        validation_rules={}
    )
    test = endpoint_test_repository.create(test)
    
    # 通过ID查找
    found_test = endpoint_test_repository.find_by_id(test.id)
    
    assert found_test is not None
    assert found_test.id == test.id
    assert found_test.name == "Test Case 2"


def test_find_by_endpoint_id(endpoint_test_repository: EndpointTestRepository, db_session: Session):
    """测试通过Endpoint ID查找测试用例"""
    from apimgmt.models.endpoint_test import EndpointTest
    # 先创建两个测试用例，同一个endpoint
    test1 = EndpointTest(
        name="Test Case 3",
        description="Test description 1",
        endpoint_id="test-endpoint-id-3",
        environment="dev",
        headers={},
        request_body={},
        expected_response={},
        validation_rules={}
    )
    test2 = EndpointTest(
        name="Test Case 4",
        description="Test description 2",
        endpoint_id="test-endpoint-id-3",
        environment="dev",
        headers={},
        request_body={},
        expected_response={},
        validation_rules={}
    )
    
    endpoint_test_repository.create(test1)
    endpoint_test_repository.create(test2)
    
    # 查找该endpoint的所有测试用例
    tests = endpoint_test_repository.find_by_endpoint_id("test-endpoint-id-3")
    
    assert len(tests) == 2
    assert any(test.name == "Test Case 3" for test in tests)
    assert any(test.name == "Test Case 4" for test in tests)


# 添加测试environment参数的功能
def test_find_by_endpoint_id_with_environment(endpoint_test_repository: EndpointTestRepository, db_session: Session):
    """测试通过Endpoint ID和环境查找测试用例"""
    from apimgmt.models.endpoint_test import EndpointTest
    # 先创建两个测试用例，同一个endpoint但不同环境
    test1 = EndpointTest(
        name="Test Case 5",
        description="Test description 1",
        endpoint_id="test-endpoint-id-4",
        environment="dev",
        headers={},
        request_body={},
        expected_response={},
        validation_rules={}
    )
    test2 = EndpointTest(
        name="Test Case 6",
        description="Test description 2",
        endpoint_id="test-endpoint-id-4",
        environment="prod",
        headers={},
        request_body={},
        expected_response={},
        validation_rules={}
    )
    
    endpoint_test_repository.create(test1)
    endpoint_test_repository.create(test2)
    
    # 按环境查找
    dev_tests = endpoint_test_repository.find_by_endpoint_id("test-endpoint-id-4", environment="dev")
    prod_tests = endpoint_test_repository.find_by_endpoint_id("test-endpoint-id-4", environment="prod")
    
    assert len(dev_tests) >= 1
    assert any(test.name == "Test Case 5" for test in dev_tests)
    assert len(prod_tests) >= 1
    assert any(test.name == "Test Case 6" for test in prod_tests)


def test_update_endpoint_test(endpoint_test_repository: EndpointTestRepository, db_session: Session):
    """测试更新测试用例"""
    from apimgmt.models.endpoint_test import EndpointTest
    # 先创建一个测试用例
    test = EndpointTest(
        name="Test Case 5",
        description="Test description",
        endpoint_id="test-endpoint-id-5",
        environment="dev",
        headers={},
        request_body={},
        expected_response={},
        validation_rules={}
    )
    test = endpoint_test_repository.create(test)
    
    # 更新测试用例
    test.name = "Updated Test Case 5"
    test.description = "Updated test description"
    updated_test = endpoint_test_repository.update(test)
    
    assert updated_test is not None
    assert updated_test.name == "Updated Test Case 5"
    assert updated_test.description == "Updated test description"
    assert updated_test.environment == "dev"


def test_delete_endpoint_test(endpoint_test_repository: EndpointTestRepository, db_session: Session):
    """测试删除测试用例"""
    from apimgmt.models.endpoint_test import EndpointTest
    # 先创建一个测试用例
    test = EndpointTest(
        name="Test Case 6",
        description="Test description",
        endpoint_id="test-endpoint-id-6",
        environment="dev",
        headers={},
        request_body={},
        expected_response={},
        validation_rules={}
    )
    test = endpoint_test_repository.create(test)
    
    # 删除测试用例
    success = endpoint_test_repository.delete(test.id)
    
    assert success is True
    
    # 验证测试用例已被删除
    deleted_test = endpoint_test_repository.find_by_id(test.id)
    assert deleted_test is None
