import pytest
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime

from apimgmt.db.database import Base
from apimgmt.models.endpoint import Endpoint
from apimgmt.models.api import Api
from apimgmt.models.system import System
from apimgmt.repositories.endpoint_repository import EndpointRepository
from apimgmt.repositories.api_repository import ApiRepository


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
def endpoint_repository(db_session):
    """创建Endpoint仓库实例"""
    return EndpointRepository(db_session)


@pytest.fixture
def api_repository(db_session):
    """创建API仓库实例"""
    return ApiRepository(db_session)


def test_create_endpoint(endpoint_repository, api_repository, db_session):
    """测试创建Endpoint"""
    # 创建系统
    system = System(
        id=str(uuid.uuid4()),
        name="Test System",
        system_code="TESTAA16F5A6",
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
        uat_host="http://uat.example.com",
        prod_host="http://prod.example.com",
        health_check_path="/health",
        health_check_rule='{"expected_status": 200, "expected_body": "OK"}',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_api = api_repository.create(api)
    
    # 创建Endpoint
    endpoint = Endpoint(
        id=str(uuid.uuid4()),
        api_id=created_api.id,
        path="/test",
        http_method="GET",
        description="Test Endpoint",
        status="DEVELOPING",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # 保存Endpoint
    created_endpoint = endpoint_repository.create(endpoint)
    
    # 验证结果
    assert created_endpoint is not None
    assert created_endpoint.id == endpoint.id
    assert created_endpoint.path == endpoint.path
    assert created_endpoint.api_id == created_api.id


def test_find_by_id(endpoint_repository, api_repository, db_session):
    """测试根据ID查找Endpoint"""
    # 创建系统
    system = System(
        id=str(uuid.uuid4()),
        name="Test System",
        system_code="TESTFD0FA10F",
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
        uat_host="http://uat.example.com",
        prod_host="http://prod.example.com",
        health_check_path="/health",
        health_check_rule='{"expected_status": 200, "expected_body": "OK"}',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_api = api_repository.create(api)
    
    # 创建Endpoint
    endpoint = Endpoint(
        id=str(uuid.uuid4()),
        api_id=api.id,
        path="/test",
        http_method="GET",
        description="Test Endpoint",
        status="DEVELOPING",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_endpoint = endpoint_repository.create(endpoint)
    
    # 查找Endpoint
    found_endpoint = endpoint_repository.find_by_id(created_endpoint.id)
    
    # 验证结果
    assert found_endpoint is not None
    assert found_endpoint.id == created_endpoint.id
    assert found_endpoint.path == created_endpoint.path


def test_find_by_api_id(endpoint_repository, api_repository, db_session):
    """测试根据API ID查找Endpoint"""
    # 创建系统
    system = System(
        id=str(uuid.uuid4()),
        name="Test System",
        system_code="TESTBF13FCA0",
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
        uat_host="http://uat.example.com",
        prod_host="http://prod.example.com",
        health_check_path="/health",
        health_check_rule='{"expected_status": 200, "expected_body": "OK"}',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_api = api_repository.create(api)
    
    # 创建多个Endpoint
    for i in range(3):
        endpoint = Endpoint(
                id=str(uuid.uuid4()),
                api_id=created_api.id,
                path=f"/test/{i}",
                http_method="GET",
                description=f"Test Endpoint {i}",
                status="DEVELOPING",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        endpoint_repository.create(endpoint)
    
    # 查找Endpoint
    endpoints = endpoint_repository.find_by_api_id(created_api.id)
    
    # 验证结果
    assert len(endpoints) >= 3


def test_update(endpoint_repository, api_repository, db_session):
    """测试更新Endpoint"""
    # 创建系统
    system = System(
        id=str(uuid.uuid4()),
        name="Test System",
        system_code="TESTE6D4EBB9",
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
        uat_host="http://uat.example.com",
        prod_host="http://prod.example.com",
        health_check_path="/health",
        health_check_rule='{"expected_status": 200, "expected_body": "OK"}',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_api = api_repository.create(api)
    
    # 创建Endpoint
    endpoint = Endpoint(
        id=str(uuid.uuid4()),
        api_id=created_api.id,
        path="/test",
        http_method="GET",
        description="Test Endpoint",
        status="DEVELOPING",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_endpoint = endpoint_repository.create(endpoint)
    
    # 更新Endpoint
    created_endpoint.path = "/updated"
    created_endpoint.http_method = "POST"
    updated_endpoint = endpoint_repository.update(created_endpoint)
    
    # 验证结果
    assert updated_endpoint is not None
    assert updated_endpoint.path == "/updated"
    assert updated_endpoint.http_method == "POST"


def test_delete(endpoint_repository, api_repository, db_session):
    """测试删除Endpoint"""
    # 创建系统
    system = System(
        id=str(uuid.uuid4()),
        name="Test System",
        system_code="TEST904AD989",
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
        uat_host="http://uat.example.com",
        prod_host="http://prod.example.com",
        health_check_path="/health",
        health_check_rule='{"expected_status": 200, "expected_body": "OK"}',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_api = api_repository.create(api)
    
    # 创建Endpoint
    endpoint = Endpoint(
            id=str(uuid.uuid4()),
            api_id=created_api.id,
            path="/test",
            http_method="GET",
            description="Test Endpoint",
            status="DEVELOPING",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    created_endpoint = endpoint_repository.create(endpoint)
    
    # 删除Endpoint
    deleted = endpoint_repository.delete(created_endpoint.id)
    
    # 验证结果
    assert deleted is True
    
    # 验证Endpoint已删除
    found_endpoint = endpoint_repository.find_by_id(created_endpoint.id)
    assert found_endpoint is None
