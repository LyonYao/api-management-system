from sqlalchemy.orm import Session
import uuid
from typing import List, Optional, Union

from apimgmt.models.endpoint import Endpoint


class EndpointRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, endpoint: Endpoint) -> Endpoint:
        """创建端点"""
        # 端点ID会在模型的默认值中设置，不需要在这里设置
        self.db.add(endpoint)
        self.db.commit()
        self.db.refresh(endpoint)
        return endpoint
    
    def find_by_id(self, endpoint_id: Union[uuid.UUID, str]) -> Optional[Endpoint]:
        """根据ID查找端点"""
        # 确保endpoint_id是字符串类型
        endpoint_id_str = str(endpoint_id)
        return self.db.query(Endpoint).filter(Endpoint.id == endpoint_id_str).first()
    
    def find_by_api_id(self, api_id: Union[uuid.UUID, str]) -> List[Endpoint]:
        """根据API ID查找端点"""
        # 确保api_id是字符串类型
        api_id_str = str(api_id)
        return self.db.query(Endpoint).filter(Endpoint.api_id == api_id_str).order_by(Endpoint.path, Endpoint.http_method).all()
    
    def find_all(self) -> List[Endpoint]:
        """查找所有端点"""
        return self.db.query(Endpoint).order_by(Endpoint.path, Endpoint.http_method).all()
    
    def find_by_api_id_path_and_method(self, api_id: Union[uuid.UUID, str], path: str, method: str) -> Optional[Endpoint]:
        """根据API ID、路径和HTTP方法查找端点"""
        # 确保api_id是字符串类型
        api_id_str = str(api_id)
        return (
            self.db.query(Endpoint)
            .filter(
                Endpoint.api_id == api_id_str,
                Endpoint.path == path,
                Endpoint.http_method == method
            )
            .first()
        )
    
    def update(self, endpoint: Endpoint) -> Optional[Endpoint]:
        """更新端点"""
        existing_endpoint = self.find_by_id(endpoint.id)
        if existing_endpoint:
            for key, value in endpoint.__dict__.items():
                if key != '_sa_instance_state':
                    setattr(existing_endpoint, key, value)
            self.db.commit()
            self.db.refresh(existing_endpoint)
            return existing_endpoint
        return None
    
    def delete(self, endpoint_id: Union[uuid.UUID, str]) -> bool:
        """删除端点"""
        endpoint = self.find_by_id(endpoint_id)
        if endpoint:
            self.db.delete(endpoint)
            self.db.commit()
            return True
        return False
