from typing import List, Optional, Union
import uuid
from sqlalchemy.orm import Session
from ..models import EndpointTest


class EndpointTestRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, test: EndpointTest) -> EndpointTest:
        """创建测试用例"""
        self.db.add(test)
        self.db.commit()
        self.db.refresh(test)
        return test
    
    def find_by_id(self, test_id: Union[uuid.UUID, str]) -> Optional[EndpointTest]:
        """根据ID查找测试用例"""
        return self.db.query(EndpointTest).filter(EndpointTest.id == test_id).first()
    
    def find_by_endpoint_id(self, endpoint_id: Union[uuid.UUID, str], environment: Optional[str] = None) -> List[EndpointTest]:
        """根据Endpoint ID查找测试用例"""
        # 确保endpoint_id是字符串类型
        endpoint_id_str = str(endpoint_id)
        query = self.db.query(EndpointTest).filter(EndpointTest.endpoint_id == endpoint_id_str)
        if environment:
            query = query.filter(EndpointTest.environment == environment)
        return query.all()
    
    def find_all(self, skip: int = 0, limit: int = 100) -> List[EndpointTest]:
        """查找所有测试用例"""
        return self.db.query(EndpointTest).offset(skip).limit(limit).all()
    
    def update(self, test: EndpointTest) -> Optional[EndpointTest]:
        """更新测试用例"""
        existing_test = self.find_by_id(test.id)
        if existing_test:
            for key, value in test.__dict__.items():
                if key != '_sa_instance_state':
                    setattr(existing_test, key, value)
            self.db.commit()
            self.db.refresh(existing_test)
            return existing_test
        return None
    
    def delete(self, test_id: Union[uuid.UUID, str]) -> bool:
        """删除测试用例"""
        test = self.find_by_id(test_id)
        if test:
            self.db.delete(test)
            self.db.commit()
            return True
        return False
