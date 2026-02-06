from sqlalchemy.orm import Session
import uuid
from typing import List, Optional, Union

from apimgmt.models.tag import Tag
from apimgmt.models.api_tag import ApiTag


class TagRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, name: str) -> Tag:
        """创建标签"""
        # 检查标签是否已存在
        existing_tag = self.find_by_name(name)
        if existing_tag:
            return existing_tag
        
        # 创建新标签
        # 标签ID会在模型的默认值中设置，不需要在这里设置
        tag = Tag(
            name=name
        )
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag
    
    def find_by_name(self, name: str) -> Optional[Tag]:
        """根据名称查找标签"""
        return self.db.query(Tag).filter(Tag.name == name).first()
    
    def find_by_id(self, tag_id: Union[uuid.UUID, str]) -> Optional[Tag]:
        """根据ID查找标签"""
        return self.db.query(Tag).filter(Tag.id == tag_id).first()
    
    def find_by_api_id(self, api_id: Union[uuid.UUID, str]) -> List[Tag]:
        """根据API ID查找标签"""
        return (
            self.db.query(Tag)
            .join(ApiTag)
            .filter(ApiTag.api_id == api_id)
            .order_by(Tag.name)
            .all()
        )
    
    def find_all(self) -> List[Tag]:
        """查找所有标签"""
        return self.db.query(Tag).order_by(Tag.name).all()
    
    def delete(self, tag_id: Union[uuid.UUID, str]) -> bool:
        """删除标签"""
        tag = self.find_by_id(tag_id)
        if tag:
            self.db.delete(tag)
            self.db.commit()
            return True
        return False
    
    def find_or_create(self, name: str) -> Tag:
        """查找或创建标签"""
        existing_tag = self.find_by_name(name)
        if existing_tag:
            return existing_tag
        return self.create(name)
