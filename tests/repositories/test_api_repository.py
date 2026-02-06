import pytest
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime

from apimgmt.db.database import Base
from apimgmt.models.api import Api
from apimgmt.models.system import System
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
def api_repository(db_session):
    """创建API仓库实例"""
    return ApiRepository(db_session)


def test_create_api(api_repository, db_session):
    """测试创建API"""
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
    
    # 保存API
    created_api = api_repository.create(api)
    
    # 验证结果
    assert created_api is not None
    assert created_api.id == api.id
    assert created_api.name == api.name
    assert created_api.system_id == system.id


def test_find_by_id(api_repository, db_session):
    """测试根据ID查找API"""
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
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_api = api_repository.create(api)
    
    # 查找API
    found_api = api_repository.find_by_id(created_api.id)
    
    # 验证结果
    assert found_api is not None
    assert found_api.id == created_api.id
    assert found_api.name == created_api.name


def test_find_by_system_id(api_repository, db_session):
    """测试根据系统ID查找API"""
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
    
    # 创建多个API
    for i in range(3):
        api = Api(
            id=str(uuid.uuid4()),
            system_id=system.id,
            name=f"Test API {i}",
            description=f"Test Description {i}",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        api_repository.create(api)
    
    # 查找API
    apis = api_repository.find_by_system_id(system.id)
    
    # 验证结果
    assert len(apis) >= 3


def test_update(api_repository, db_session):
    """测试更新API"""
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
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_api = api_repository.create(api)
    
    # 更新API
    created_api.name = "Updated API"
    created_api.description = "Updated Description"
    updated_api = api_repository.update(created_api)
    
    # 验证结果
    assert updated_api is not None
    assert updated_api.name == "Updated API"
    assert updated_api.description == "Updated Description"


def test_delete(api_repository, db_session):
    """测试删除API"""
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
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_api = api_repository.create(api)
    
    # 删除API
    deleted = api_repository.delete(created_api.id)
    
    # 验证结果
    assert deleted is True
    
    # 验证API已删除
    found_api = api_repository.find_by_id(created_api.id)
    assert found_api is None
