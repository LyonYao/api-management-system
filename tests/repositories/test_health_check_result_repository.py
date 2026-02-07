import pytest
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime

from apimgmt.db.database import Base
from apimgmt.models.health_check_result import HealthCheckResult
from apimgmt.models.endpoint import Endpoint
from apimgmt.repositories.health_check_result_repository import HealthCheckResultRepository
from apimgmt.repositories.api_repository import ApiRepository
from apimgmt.repositories.endpoint_repository import EndpointRepository
from apimgmt.models.api import Api
from apimgmt.models.system import System


@pytest.fixture
def db_session():
    """创建内存数据库会话"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def health_check_result_repository(db_session):
    """创建HealthCheckResult仓库实例"""
    return HealthCheckResultRepository(db_session)


@pytest.fixture
def api_repository(db_session):
    """创建API仓库实例"""
    return ApiRepository(db_session)


@pytest.fixture
def endpoint_repository(db_session):
    """创建Endpoint仓库实例"""
    return EndpointRepository(db_session)


def test_create_health_check_result(health_check_result_repository, api_repository, endpoint_repository, db_session):
    """测试创建健康检查结果"""
    # 创建系统
    system = System(
        id=str(uuid.uuid4()),
        name="Test System",
        description="Test Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(system)
    db_session.commit()
    
    # 创建API
    api = Api(
        id=str(uuid.uuid4()),
        system_id=system.id,
        name="Test API",
        description="Test Description",
        auth_type="NONE",
        spec_link="https://example.com/spec",
        department="Engineering",
        contact_name="Test Contact",
        contact_emails="test@example.com",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(api)
    db_session.commit()
    
    # 创建Endpoint
    endpoint = Endpoint(
            id=str(uuid.uuid4()),
            api_id=api.id,
            path="/test",
            http_method="GET",
            description="Test Endpoint",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    db_session.add(endpoint)
    db_session.commit()
    
    # 创建健康检查结果
    health_check_result = HealthCheckResult(
        id=str(uuid.uuid4()),
        endpoint_id=endpoint.id,
        status="SUCCESS",
        response_code=200,
        response_time_ms=100,
        checked_at=datetime.utcnow(),
        error_message=None
    )
    
    # 保存健康检查结果
    created_health_check_result = health_check_result_repository.create(health_check_result)
    
    # 验证结果
    assert created_health_check_result is not None
    assert created_health_check_result.id == health_check_result.id
    assert created_health_check_result.endpoint_id == endpoint.id
    assert created_health_check_result.status == "SUCCESS"


def test_find_by_endpoint_id(health_check_result_repository, api_repository, endpoint_repository, db_session):
    """测试根据Endpoint ID查找健康检查结果"""
    # 创建系统
    system = System(
        id=str(uuid.uuid4()),
        name="Test System",
        description="Test Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(system)
    db_session.commit()
    
    # 创建API
    api = Api(
        id=str(uuid.uuid4()),
        system_id=system.id,
        name="Test API",
        description="Test Description",
        auth_type="NONE",
        spec_link="https://example.com/spec",
        department="Engineering",
        contact_name="Test Contact",
        contact_emails="test@example.com",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(api)
    db_session.commit()
    
    # 创建Endpoint
    endpoint = Endpoint(
            id=str(uuid.uuid4()),
            api_id=api.id,
            path="/test",
            http_method="GET",
            description="Test Endpoint",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    db_session.add(endpoint)
    db_session.commit()
    
    # 创建多个健康检查结果
    for i in range(3):
        health_check_result = HealthCheckResult(
            id=str(uuid.uuid4()),
            endpoint_id=endpoint.id,
            status="SUCCESS",
            response_code=200,
            response_time_ms=100 + i * 50,
            checked_at=datetime.utcnow(),
            error_message=None
        )
        health_check_result_repository.create(health_check_result)
    
    # 查找健康检查结果
    health_check_results = health_check_result_repository.find_by_endpoint_id(endpoint.id)
    
    # 验证结果
    assert len(health_check_results) >= 3


def test_find_latest_by_endpoint_id(health_check_result_repository, api_repository, endpoint_repository, db_session):
    """测试查找Endpoint的最新健康检查结果"""
    # 创建系统
    system = System(
        id=str(uuid.uuid4()),
        name="Test System",
        description="Test Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(system)
    db_session.commit()
    
    # 创建API
    api = Api(
        id=str(uuid.uuid4()),
        system_id=system.id,
        name="Test API",
        description="Test Description",
        auth_type="NONE",
        spec_link="https://example.com/spec",
        department="Engineering",
        contact_name="Test Contact",
        contact_emails="test@example.com",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(api)
    db_session.commit()
    
    # 创建Endpoint
    endpoint = Endpoint(
            id=str(uuid.uuid4()),
            api_id=api.id,
            path="/test",
            http_method="GET",
            description="Test Endpoint",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    db_session.add(endpoint)
    db_session.commit()
    
    # 创建多个健康检查结果
    for i in range(3):
        health_check_result = HealthCheckResult(
            id=str(uuid.uuid4()),
            endpoint_id=endpoint.id,
            status="SUCCESS",
            response_code=200,
            response_time_ms=100 + i * 50,
            checked_at=datetime.utcnow(),
            error_message=None
        )
        health_check_result_repository.create(health_check_result)
    
    # 查找最新健康检查结果
    latest_health_check_result = health_check_result_repository.find_latest_by_endpoint_id(endpoint.id)
    
    # 验证结果
    assert latest_health_check_result is not None
    assert latest_health_check_result.endpoint_id == endpoint.id


def test_delete(health_check_result_repository, api_repository, endpoint_repository, db_session):
    """测试删除健康检查结果"""
    # 创建系统
    system = System(
        id=str(uuid.uuid4()),
        name="Test System",
        description="Test Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(system)
    db_session.commit()
    
    # 创建API
    api = Api(
        id=str(uuid.uuid4()),
        system_id=system.id,
        name="Test API",
        description="Test Description",
        auth_type="NONE",
        spec_link="https://example.com/spec",
        department="Engineering",
        contact_name="Test Contact",
        contact_emails="test@example.com",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(api)
    db_session.commit()
    
    # 创建Endpoint
    endpoint = Endpoint(
            id=str(uuid.uuid4()),
            api_id=api.id,
            path="/test",
            http_method="GET",
            description="Test Endpoint",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    db_session.add(endpoint)
    db_session.commit()
    
    # 创建健康检查结果
    health_check_result = HealthCheckResult(
        id=str(uuid.uuid4()),
        endpoint_id=endpoint.id,
        status="SUCCESS",
        response_code=200,
        response_time_ms=100,
        checked_at=datetime.utcnow(),
        error_message=None
    )
    created_health_check_result = health_check_result_repository.create(health_check_result)
    
    # 删除健康检查结果
    deleted = health_check_result_repository.delete(created_health_check_result.id)
    
    # 验证结果
    assert deleted is True
    
    # 验证健康检查结果已删除
    found_health_check_result = health_check_result_repository.find_by_id(created_health_check_result.id)
    assert found_health_check_result is None
