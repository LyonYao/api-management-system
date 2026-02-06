from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import uuid
from typing import List, Optional, Set, Union

from apimgmt.models.api import Api
from apimgmt.models.tag import Tag
from apimgmt.models.api_tag import ApiTag


class ApiRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, api: Api) -> Api:
        """创建API"""
        # API ID会在模型的默认值中设置，不需要在这里设置
        self.db.add(api)
        self.db.commit()
        self.db.refresh(api)
        return api
    
    def find_by_id(self, api_id: Union[uuid.UUID, str]) -> Optional[Api]:
        """根据ID查找API"""
        return self.db.query(Api).filter(Api.id == api_id).first()
    
    def find_all(self) -> List[Api]:
        """查找所有API"""
        return self.db.query(Api).order_by(Api.name).all()
    
    def find_by_system_id(self, system_id: Union[uuid.UUID, str]) -> List[Api]:
        """根据系统ID查找API"""
        return self.db.query(Api).filter(Api.system_id == system_id).order_by(Api.name).all()
    
    def find_by_tags(self, tags: Set[str]) -> List[Api]:
        """根据标签查找API"""
        if not tags:
            return self.find_all()
        
        # 查找包含所有指定标签的API
        subquery = (
            self.db.query(ApiTag.api_id)
            .join(Tag, ApiTag.tag_id == Tag.id)
            .filter(Tag.name.in_(tags))
            .group_by(ApiTag.api_id)
            .having(func.count(func.distinct(Tag.name)) == len(tags))
            .subquery()
        )
        
        return (
            self.db.query(Api)
            .filter(Api.id.in_(subquery))
            .order_by(Api.name)
            .all()
        )
    
    def update(self, api: Api) -> Optional[Api]:
        """更新API"""
        existing_api = self.find_by_id(api.id)
        if existing_api:
            for key, value in api.__dict__.items():
                if key != '_sa_instance_state':
                    setattr(existing_api, key, value)
            self.db.commit()
            self.db.refresh(existing_api)
            return existing_api
        return None
    
    def delete(self, api_id: Union[uuid.UUID, str]) -> bool:
        """删除API"""
        api = self.find_by_id(api_id)
        if api:
            # 先删除关联的标签关系
            self.clear_tags(api_id)
            # 再删除API
            self.db.delete(api)
            self.db.commit()
            return True
        return False
    
    def associate_tags(self, api_id: Union[uuid.UUID, str], tag_ids: Set[Union[uuid.UUID, str]]) -> None:
        """关联标签"""
        if not tag_ids:
            return
        
        # 清除现有关联
        self.clear_tags(api_id)
        
        # 添加新关联
        for tag_id in tag_ids:
            api_tag = ApiTag(api_id=api_id, tag_id=tag_id)
            self.db.add(api_tag)
        
        self.db.commit()
    
    def clear_tags(self, api_id: Union[uuid.UUID, str]) -> None:
        """清除标签关联"""
        self.db.query(ApiTag).filter(ApiTag.api_id == api_id).delete()
        self.db.commit()
    
    def get_api_tags(self, api_id: Union[uuid.UUID, str]) -> Set[str]:
        """获取API的标签"""
        tags = (
            self.db.query(Tag.name)
            .join(ApiTag, Tag.id == ApiTag.tag_id)
            .filter(ApiTag.api_id == api_id)
            .all()
        )
        return {tag.name for tag in tags}
