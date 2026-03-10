from typing import List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models import TestBatch


class TestBatchRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, test_batch: TestBatch) -> TestBatch:
        """创建测试批次"""
        self.db.add(test_batch)
        self.db.commit()
        self.db.refresh(test_batch)
        return test_batch
    
    def find_by_id(self, batch_id: str) -> Optional[TestBatch]:
        """根据批次ID查找测试批次"""
        return self.db.query(TestBatch).filter(TestBatch.batch_id == batch_id).first()
    
    def find_by_system_id(self, system_id: Union[str, bytes]) -> List[TestBatch]:
        """根据系统ID查找测试批次"""
        return self.db.query(TestBatch).filter(TestBatch.system_id == system_id).order_by(desc(TestBatch.start_time)).all()
    
    def find_by_api_id(self, api_id: Union[str, bytes]) -> List[TestBatch]:
        """根据API ID查找测试批次"""
        return self.db.query(TestBatch).filter(TestBatch.api_id == api_id).order_by(desc(TestBatch.start_time)).all()
    
    def find_all(self, system_id: Optional[Union[str, bytes]] = None,
                 api_id: Optional[Union[str, bytes]] = None,
                 environment: Optional[str] = None,
                 skip: int = 0, limit: int = 100) -> List[TestBatch]:
        """查找所有测试批次"""
        query = self.db.query(TestBatch)
        
        if system_id:
            query = query.filter(TestBatch.system_id == system_id)
        if api_id:
            query = query.filter(TestBatch.api_id == api_id)
        if environment:
            query = query.filter(TestBatch.environment == environment)
        
        return query.order_by(desc(TestBatch.start_time)).offset(skip).limit(limit).all()
    
    def update(self, test_batch: TestBatch) -> TestBatch:
        """更新测试批次"""
        self.db.add(test_batch)
        self.db.commit()
        self.db.refresh(test_batch)
        return test_batch
    
    def delete(self, batch_id: str) -> bool:
        """删除测试批次"""
        batch = self.find_by_id(batch_id)
        if not batch:
            return False
        self.db.delete(batch)
        self.db.commit()
        return True
