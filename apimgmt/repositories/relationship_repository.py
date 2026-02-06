from sqlalchemy.orm import Session
import uuid
from typing import List, Optional, Union

from apimgmt.models.relationship import Relationship


class RelationshipRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, relationship: Relationship) -> Relationship:
        """创建调用关系"""
        # 关系ID会在模型的默认值中设置，不需要在这里设置
        self.db.add(relationship)
        self.db.commit()
        self.db.refresh(relationship)
        return relationship
    
    def find_by_id(self, relationship_id: Union[uuid.UUID, str]) -> Optional[Relationship]:
        """根据ID查找调用关系"""
        return self.db.query(Relationship).filter(Relationship.id == relationship_id).first()
    
    def find_all(self) -> List[Relationship]:
        """查找所有调用关系"""
        return self.db.query(Relationship).all()
    
    def find_by_caller(self, caller_type: str, caller_id: Union[uuid.UUID, str]) -> List[Relationship]:
        """根据调用方查找调用关系"""
        return (
            self.db.query(Relationship)
            .filter(
                Relationship.caller_type == caller_type,
                Relationship.caller_id == caller_id
            )
            .all()
        )
    
    def find_by_callee(self, callee_type: str, callee_id: Union[uuid.UUID, str]) -> List[Relationship]:
        """根据被调用方查找调用关系"""
        return (
            self.db.query(Relationship)
            .filter(
                Relationship.callee_type == callee_type,
                Relationship.callee_id == callee_id
            )
            .all()
        )
    
    def update(self, relationship: Relationship) -> Optional[Relationship]:
        """更新调用关系"""
        existing_relationship = self.find_by_id(relationship.id)
        if existing_relationship:
            for key, value in relationship.__dict__.items():
                if key != '_sa_instance_state':
                    setattr(existing_relationship, key, value)
            self.db.commit()
            self.db.refresh(existing_relationship)
            return existing_relationship
        return None
    
    def delete(self, relationship_id: Union[uuid.UUID, str]) -> bool:
        """删除调用关系"""
        relationship = self.find_by_id(relationship_id)
        if relationship:
            self.db.delete(relationship)
            self.db.commit()
            return True
        return False
