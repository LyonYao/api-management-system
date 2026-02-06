import pytest
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime

from apimgmt.db.database import Base
from apimgmt.models.system import System
from apimgmt.repositories.system_repository import SystemRepository


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
def system_repository(db_session):
    """创建系统仓库实例"""
    return SystemRepository(db_session)


def test_create_system(system_repository):
    """测试创建系统"""
    # 创建系统
    system = System(
        id=str(uuid.uuid4()),
        name="Test System",
        description="Test Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # 保存系统
    created_system = system_repository.create(system)
    
    # 验证结果
    assert created_system is not None
    assert created_system.id == system.id
    assert created_system.name == system.name
    assert created_system.description == system.description


def test_find_by_id(system_repository):
    """测试根据ID查找系统"""
    # 创建系统
    system = System(
        id=str(uuid.uuid4()),
        name="Test System",
        description="Test Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_system = system_repository.create(system)
    
    # 查找系统
    found_system = system_repository.find_by_id(created_system.id)
    
    # 验证结果
    assert found_system is not None
    assert found_system.id == created_system.id
    assert found_system.name == created_system.name


def test_find_by_name(system_repository):
    """测试根据名称查找系统"""
    # 创建系统
    system = System(
        id=str(uuid.uuid4()),
        name="Test System",
        description="Test Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_system = system_repository.create(system)
    
    # 查找系统
    found_system = system_repository.find_by_name(created_system.name)
    
    # 验证结果
    assert found_system is not None
    assert found_system.name == created_system.name


def test_find_all(system_repository):
    """测试查找所有系统"""
    # 创建多个系统
    for i in range(3):
        system = System(
            id=str(uuid.uuid4()),
            name=f"Test System {i}",
            description=f"Test Description {i}",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        system_repository.create(system)
    
    # 查找所有系统
    systems = system_repository.find_all()
    
    # 验证结果
    assert len(systems) >= 3


def test_update(system_repository):
    """测试更新系统"""
    # 创建系统
    system = System(
        id=str(uuid.uuid4()),
        name="Test System",
        description="Test Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_system = system_repository.create(system)
    
    # 更新系统
    created_system.name = "Updated System"
    created_system.description = "Updated Description"
    updated_system = system_repository.update(created_system)
    
    # 验证结果
    assert updated_system is not None
    assert updated_system.name == "Updated System"
    assert updated_system.description == "Updated Description"


def test_delete(system_repository):
    """测试删除系统"""
    # 创建系统
    system = System(
        id=str(uuid.uuid4()),
        name="Test System",
        description="Test Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_system = system_repository.create(system)
    
    # 删除系统
    deleted = system_repository.delete(created_system.id)
    
    # 验证结果
    assert deleted is True
    
    # 验证系统已删除
    found_system = system_repository.find_by_id(created_system.id)
    assert found_system is None
