from typing import List, Optional, Union, Dict, Any
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models import TestResult, EndpointTest, Endpoint, Api


class TestResultRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, test_result: TestResult) -> TestResult:
        """创建测试执行结果"""
        self.db.add(test_result)
        self.db.commit()
        self.db.refresh(test_result)
        return test_result
    
    def find_by_id(self, result_id: Union[uuid.UUID, str]) -> Optional[TestResult]:
        """根据ID查找测试执行结果"""
        return self.db.query(TestResult).filter(TestResult.id == result_id).first()
    
    def find_by_test_id(self, test_id: Union[uuid.UUID, str]) -> List[TestResult]:
        """根据测试用例ID查找测试执行结果"""
        return self.db.query(TestResult).filter(TestResult.test_id == test_id).order_by(desc(TestResult.executed_at)).all()
    
    def find_by_endpoint_id(self, endpoint_id: Union[uuid.UUID, str]) -> List[TestResult]:
        """根据Endpoint ID查找测试执行结果"""
        return self.db.query(TestResult).join(EndpointTest).filter(EndpointTest.endpoint_id == endpoint_id).order_by(desc(TestResult.executed_at)).all()
    
    def find_by_api_id(self, api_id: Union[uuid.UUID, str]) -> List[TestResult]:
        """根据API ID查找测试执行结果"""
        return self.db.query(TestResult).join(EndpointTest).join(Endpoint).filter(Endpoint.api_id == api_id).order_by(desc(TestResult.executed_at)).all()
    
    def find_by_system_id(self, system_id: Union[uuid.UUID, str]) -> List[TestResult]:
        """根据系统ID查找测试执行结果"""
        return self.db.query(TestResult).join(EndpointTest).join(Endpoint).join(Api).filter(Api.system_id == system_id).order_by(desc(TestResult.executed_at)).all()
    
    def find_by_batch_id(self, batch_id: str) -> List[TestResult]:
        """根据批次ID查找测试执行结果"""
        return self.db.query(TestResult).filter(TestResult.batch_id == batch_id).order_by(desc(TestResult.executed_at)).all()
    
    def find_all(self, system_id: Optional[Union[uuid.UUID, str]] = None, 
                 api_id: Optional[Union[uuid.UUID, str]] = None, 
                 environment: Optional[str] = None,
                 batch_id: Optional[str] = None,
                 start_date: Optional[datetime] = None, 
                 end_date: Optional[datetime] = None, 
                 status: Optional[str] = None, 
                 skip: int = 0, limit: int = 100) -> List[TestResult]:
        """根据条件查找测试执行结果"""
        query = self.db.query(TestResult).join(EndpointTest).join(Endpoint).join(Api)
        
        if system_id:
            query = query.filter(Api.system_id == system_id)
        if api_id:
            query = query.filter(Endpoint.api_id == api_id)
        if environment:
            query = query.filter(TestResult.environment == environment)
        if batch_id:
            query = query.filter(TestResult.batch_id == batch_id)
        if start_date:
            query = query.filter(TestResult.executed_at >= start_date)
        if end_date:
            query = query.filter(TestResult.executed_at <= end_date)
        if status:
            query = query.filter(TestResult.status == status)
        
        return query.order_by(desc(TestResult.executed_at)).offset(skip).limit(limit).all()
    
    def find_batches(self, system_id: Optional[Union[uuid.UUID, str]] = None, 
                     api_id: Optional[Union[uuid.UUID, str]] = None,
                     environment: Optional[str] = None,
                     start_date: Optional[datetime] = None, 
                     end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """根据条件查找测试批次列表"""
        from sqlalchemy import func
        from ..models import System
        
        # 先获取所有符合条件的测试结果
        base_query = self.db.query(TestResult).join(EndpointTest).join(Endpoint).join(Api).join(System)
        
        if system_id:
            base_query = base_query.filter(Api.system_id == system_id)
        if api_id:
            base_query = base_query.filter(Api.id == api_id)
        if environment:
            base_query = base_query.filter(TestResult.environment == environment)
        if start_date:
            base_query = base_query.filter(TestResult.executed_at >= start_date)
        if end_date:
            base_query = base_query.filter(TestResult.executed_at <= end_date)
        
        # 获取所有测试结果
        test_results = base_query.all()
        
        # 按批次分组
        batch_dict = {}
        for result in test_results:
            batch_id = result.batch_id
            if batch_id not in batch_dict:
                # 获取系统和API信息
                system_name = result.endpoint_test.endpoint.api.system.name if result.endpoint_test and result.endpoint_test.endpoint and result.endpoint_test.endpoint.api and result.endpoint_test.endpoint.api.system else ""
                api_name = result.endpoint_test.endpoint.api.name if result.endpoint_test and result.endpoint_test.endpoint and result.endpoint_test.endpoint.api else ""
                api_id_val = result.endpoint_test.endpoint.api.id if result.endpoint_test and result.endpoint_test.endpoint and result.endpoint_test.endpoint.api else None
                system_id_val = result.endpoint_test.endpoint.api.system_id if result.endpoint_test and result.endpoint_test.endpoint and result.endpoint_test.endpoint.api else None
                
                batch_dict[batch_id] = {
                    'batch_id': batch_id,
                    'executed_at': result.executed_at,
                    'total_count': 0,
                    'pass_count': 0,
                    'fail_count': 0,
                    'error_count': 0,
                    'system_id': str(system_id_val) if system_id_val else "",
                    'system_name': system_name,
                    'api_id': str(api_id_val) if api_id_val else "",
                    'api_name': api_name
                }
            
            # 更新计数
            batch_dict[batch_id]['total_count'] += 1
            if result.status == 'PASS':
                batch_dict[batch_id]['pass_count'] += 1
            elif result.status == 'FAIL':
                batch_dict[batch_id]['fail_count'] += 1
            elif result.status == 'ERROR':
                batch_dict[batch_id]['error_count'] += 1
        
        # 转换为列表并按执行时间排序
        batches = list(batch_dict.values())
        batches.sort(key=lambda x: x['executed_at'], reverse=True)
        
        return batches
