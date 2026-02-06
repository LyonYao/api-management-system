import pytest
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime

from apimgmt.db.database import Base
from apimgmt.models.tag import Tag
from apimgmt.models.api_tag import ApiTag
from apimgmt.models.api import Api
from apimgmt.models.system import System
from apimgmt.repositories.tag_repository import TagRepository
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
def tag_repository(db_session):
    """创建Tag仓库实例"""
    return TagRepository(db_session)


@pytest.fixture
def api_repository(db_session):
    """创建API仓库实例"""
    return ApiRepository(db_session)


def test_create_tag(tag_repository):
    """测试创建Tag"""
    # 创建Tag
    tag_name = "test-tag"
    created_tag = tag_repository.create(tag_name)
    
    # 验证结果
    assert created_tag is not None
    assert created_tag.name == tag_name


def test_find_by_id(tag_repository):
    """测试根据ID查找Tag"""
    # 创建Tag
    tag_name = "test-tag"
    created_tag = tag_repository.create(tag_name)
    
    # 查找Tag
    found_tag = tag_repository.find_by_id(created_tag.id)
    
    # 验证结果
    assert found_tag is not None
    assert found_tag.id == created_tag.id
    assert found_tag.name == tag_name


def test_find_by_name(tag_repository):
    """测试根据名称查找Tag"""
    # 创建Tag
    tag_name = "test-tag"
    tag_repository.create(tag_name)
    
    # 查找Tag
    found_tag = tag_repository.find_by_name(tag_name)
    
    # 验证结果
    assert found_tag is not None
    assert found_tag.name == tag_name


def test_find_all(tag_repository):
    """测试查找所有Tag"""
    # 创建多个Tag
    tag_names = ["tag1", "tag2", "tag3"]
    for name in tag_names:
        tag_repository.create(name)
    
    # 查找所有Tag
    tags = tag_repository.find_all()
    
    # 验证结果
    assert len(tags) >= len(tag_names)


def test_find_by_api_id(tag_repository, api_repository, db_session):
    """测试根据API ID查找Tag"""
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
    
    # 创建Tag
    tag1 = tag_repository.create("tag1")
    tag2 = tag_repository.create("tag2")
    
    # 创建ApiTag关联
    api_tag1 = ApiTag(
        api_id=created_api.id,
        tag_id=tag1.id
    )
    api_tag2 = ApiTag(
        api_id=created_api.id,
        tag_id=tag2.id
    )
    db_session.add_all([api_tag1, api_tag2])
    db_session.commit()
    
    # 查找Tag
    tags = tag_repository.find_by_api_id(created_api.id)
    
    # 验证结果
    assert len(tags) >= 2


def test_delete(tag_repository):
    """测试删除Tag"""
    # 创建Tag
    tag_name = "test-tag"
    created_tag = tag_repository.create(tag_name)
    
    # 删除Tag
    deleted = tag_repository.delete(created_tag.id)
    
    # 验证结果
    assert deleted is True
    
    # 验证Tag已删除
    found_tag = tag_repository.find_by_id(created_tag.id)
    assert found_tag is None
