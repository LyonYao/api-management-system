import pytest
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime

from apimgmt.db.database import Base
from apimgmt.models.relationship import Relationship
from apimgmt.models.api import Api
from apimgmt.models.system import System
from apimgmt.repositories.relationship_repository import RelationshipRepository
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
def relationship_repository(db_session):
    """创建Relationship仓库实例"""
    return RelationshipRepository(db_session)


@pytest.fixture
def api_repository(db_session):
    """创建API仓库实例"""
    return ApiRepository(db_session)


def test_create_relationship(relationship_repository, api_repository, db_session):
    """测试创建Relationship"""
    # 创建系统
    system1 = System(
        id=str(uuid.uuid4()),
        name="Source System",
        description="Source Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    system2 = System(
        id=str(uuid.uuid4()),
        name="Target System",
        description="Target Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add_all([system1, system2])
    db_session.commit()
    
    # 创建API
    api1 = Api(
        id=str(uuid.uuid4()),
        system_id=system1.id,
        name="Source API",
        description="Source Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    api2 = Api(
        id=str(uuid.uuid4()),
        system_id=system2.id,
        name="Target API",
        description="Target Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_api1 = api_repository.create(api1)
    created_api2 = api_repository.create(api2)
    
    # 创建Relationship
    relationship = Relationship(
        id=str(uuid.uuid4()),
        caller_type="API",
        caller_id=created_api1.id,
        callee_type="API",
        callee_id=created_api2.id,
        description="Test Relationship",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # 保存Relationship
    created_relationship = relationship_repository.create(relationship)
    
    # 验证结果
    assert created_relationship is not None
    assert created_relationship.id == relationship.id
    assert created_relationship.caller_id == created_api1.id
    assert created_relationship.callee_id == created_api2.id


def test_find_by_id(relationship_repository, api_repository, db_session):
    """测试根据ID查找Relationship"""
    # 创建系统
    system1 = System(
        id=str(uuid.uuid4()),
        name="Source System",
        description="Source Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    system2 = System(
        id=str(uuid.uuid4()),
        name="Target System",
        description="Target Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add_all([system1, system2])
    db_session.commit()
    
    # 创建API
    api1 = Api(
        id=str(uuid.uuid4()),
        system_id=system1.id,
        name="Source API",
        description="Source Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    api2 = Api(
        id=str(uuid.uuid4()),
        system_id=system2.id,
        name="Target API",
        description="Target Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_api1 = api_repository.create(api1)
    created_api2 = api_repository.create(api2)
    
    # 创建Relationship
    relationship = Relationship(
        id=str(uuid.uuid4()),
        caller_type="API",
        caller_id=created_api1.id,
        callee_type="API",
        callee_id=created_api2.id,
        description="Test Relationship",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_relationship = relationship_repository.create(relationship)
    
    # 查找Relationship
    found_relationship = relationship_repository.find_by_id(created_relationship.id)
    
    # 验证结果
    assert found_relationship is not None
    assert found_relationship.id == created_relationship.id
    assert found_relationship.caller_id == created_api1.id
    assert found_relationship.callee_id == created_api2.id


def test_update(relationship_repository, api_repository, db_session):
    """测试更新Relationship"""
    # 创建系统
    system1 = System(
        id=str(uuid.uuid4()),
        name="Source System",
        description="Source Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    system2 = System(
        id=str(uuid.uuid4()),
        name="Target System",
        description="Target Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add_all([system1, system2])
    db_session.commit()
    
    # 创建API
    api1 = Api(
        id=str(uuid.uuid4()),
        system_id=system1.id,
        name="Source API",
        description="Source Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    api2 = Api(
        id=str(uuid.uuid4()),
        system_id=system2.id,
        name="Target API",
        description="Target Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_api1 = api_repository.create(api1)
    created_api2 = api_repository.create(api2)
    
    # 创建Relationship
    relationship = Relationship(
        id=str(uuid.uuid4()),
        caller_type="API",
        caller_id=created_api1.id,
        callee_type="API",
        callee_id=created_api2.id,
        description="Test Relationship",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_relationship = relationship_repository.create(relationship)
    
    # 更新Relationship
    created_relationship.description = "Updated Relationship"
    updated_relationship = relationship_repository.update(created_relationship)
    
    # 验证结果
    assert updated_relationship is not None
    assert updated_relationship.description == "Updated Relationship"


def test_delete(relationship_repository, api_repository, db_session):
    """测试删除Relationship"""
    # 创建系统
    system1 = System(
        id=str(uuid.uuid4()),
        name="Source System",
        description="Source Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    system2 = System(
        id=str(uuid.uuid4()),
        name="Target System",
        description="Target Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add_all([system1, system2])
    db_session.commit()
    
    # 创建API
    api1 = Api(
        id=str(uuid.uuid4()),
        system_id=system1.id,
        name="Source API",
        description="Source Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    api2 = Api(
        id=str(uuid.uuid4()),
        system_id=system2.id,
        name="Target API",
        description="Target Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_api1 = api_repository.create(api1)
    created_api2 = api_repository.create(api2)
    
    # 创建Relationship
    relationship = Relationship(
        id=str(uuid.uuid4()),
        caller_type="API",
        caller_id=created_api1.id,
        callee_type="API",
        callee_id=created_api2.id,
        description="Test Relationship",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_relationship = relationship_repository.create(relationship)
    
    # 删除Relationship
    deleted = relationship_repository.delete(created_relationship.id)
    
    # 验证结果
    assert deleted is True
    
    # 验证Relationship已删除
    found_relationship = relationship_repository.find_by_id(created_relationship.id)
    assert found_relationship is None
