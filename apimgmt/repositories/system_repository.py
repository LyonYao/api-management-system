from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid
from typing import List, Optional, Union

from apimgmt.models.system import System


class SystemRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, system: System) -> System:
        """创建系统"""
        # 系统ID会在模型的默认值中设置，不需要在这里设置
        self.db.add(system)
        self.db.commit()
        self.db.refresh(system)
        return system
    
    def find_by_id(self, system_id: Union[uuid.UUID, str]) -> Optional[System]:
        """根据ID查找系统"""
        return self.db.query(System).filter(System.id == system_id).first()
    
    def find_by_name(self, name: str) -> Optional[System]:
        """根据名称查找系统"""
        return self.db.query(System).filter(System.name == name).first()
    
    def find_all(self) -> List[System]:
        """查找所有系统"""
        return self.db.query(System).order_by(System.name).all()
    
    def update(self, system: System) -> Optional[System]:
        """更新系统"""
        existing_system = self.find_by_id(system.id)
        if existing_system:
            for key, value in system.__dict__.items():
                if key != '_sa_instance_state':
                    setattr(existing_system, key, value)
            self.db.commit()
            self.db.refresh(existing_system)
            return existing_system
        return None
    
    def delete(self, system_id: Union[uuid.UUID, str]) -> bool:
        """删除系统"""
        system = self.find_by_id(system_id)
        if system:
            self.db.delete(system)
            self.db.commit()
            return True
        return False
    
    def count_apis_by_system_id(self, system_id: Union[uuid.UUID, str]) -> int:
        """统计系统的API数量"""
        from apimgmt.models.api import Api
        return self.db.query(func.count(Api.id)).filter(Api.system_id == system_id).scalar() or 0
