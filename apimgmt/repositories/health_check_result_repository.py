from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
import uuid
from typing import List, Optional, Union, Dict, Any

from apimgmt.models.health_check_result import HealthCheckResult


class HealthCheckResultRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, health_check_result: HealthCheckResult) -> HealthCheckResult:
        """创建健康检查结果"""
        # 结果ID会在模型的默认值中设置，不需要在这里设置
        self.db.add(health_check_result)
        self.db.commit()
        self.db.refresh(health_check_result)
        return health_check_result
    
    def find_by_id(self, result_id: Union[uuid.UUID, str]) -> Optional[HealthCheckResult]:
        """根据ID查找健康检查结果"""
        # 确保result_id是字符串类型
        result_id_str = str(result_id)
        return self.db.query(HealthCheckResult).filter(HealthCheckResult.id == result_id_str).first()
    
    def find_by_endpoint_id(self, endpoint_id: Union[uuid.UUID, str]) -> List[HealthCheckResult]:
        """根据端点ID查找健康检查结果"""
        # 确保endpoint_id是字符串类型
        endpoint_id_str = str(endpoint_id)
        return (
            self.db.query(HealthCheckResult)
            .filter(HealthCheckResult.endpoint_id == endpoint_id_str)
            .order_by(desc(HealthCheckResult.checked_at))
            .all()
        )
    
    def find_by_endpoint_id_ordered_by_time(self, endpoint_id: Union[uuid.UUID, str]) -> List[HealthCheckResult]:
        """根据端点ID查找健康检查结果，按时间排序"""
        return self.find_by_endpoint_id(endpoint_id)
    
    def find_latest_by_endpoint_id(self, endpoint_id: Union[uuid.UUID, str]) -> Optional[HealthCheckResult]:
        """查找端点的最新健康检查结果"""
        # 确保endpoint_id是字符串类型
        endpoint_id_str = str(endpoint_id)
        return (
            self.db.query(HealthCheckResult)
            .filter(HealthCheckResult.endpoint_id == endpoint_id_str)
            .order_by(desc(HealthCheckResult.checked_at))
            .first()
        )
    
    def find_by_system_id(self, system_id: Union[uuid.UUID, str]) -> List[HealthCheckResult]:
        """根据系统ID查找健康检查结果"""
        # 确保system_id是字符串类型
        system_id_str = str(system_id)
        return (
            self.db.query(HealthCheckResult)
            .filter(HealthCheckResult.system_id == system_id_str)
            .order_by(desc(HealthCheckResult.checked_at))
            .all()
        )
    
    def find_by_api_id(self, api_id: Union[uuid.UUID, str]) -> List[HealthCheckResult]:
        """根据API ID查找健康检查结果"""
        # 确保api_id是字符串类型
        api_id_str = str(api_id)
        return (
            self.db.query(HealthCheckResult)
            .filter(HealthCheckResult.api_id == api_id_str)
            .order_by(desc(HealthCheckResult.checked_at))
            .all()
        )
    
    def find_recent(self, limit: int = 100) -> List[HealthCheckResult]:
        """查找最近的健康检查结果"""
        return (
            self.db.query(HealthCheckResult)
            .order_by(desc(HealthCheckResult.checked_at))
            .limit(limit)
            .all()
        )
    
    def find_recent_with_limit(self, limit: int) -> List[HealthCheckResult]:
        """查找最近的健康检查结果，限制数量"""
        return self.find_recent(limit)
    
    def find_with_pagination(self, page: int = 1, page_size: int = 20, system_id: Optional[Union[uuid.UUID, str]] = None, api_id: Optional[Union[uuid.UUID, str]] = None) -> List[HealthCheckResult]:
        """分页查询健康检查结果"""
        query = self.db.query(HealthCheckResult)
        
        # 添加过滤条件
        if system_id:
            # 确保system_id是字符串类型
            system_id_str = str(system_id)
            query = query.filter(HealthCheckResult.system_id == system_id_str)
        if api_id:
            # 确保api_id是字符串类型
            api_id_str = str(api_id)
            query = query.filter(HealthCheckResult.api_id == api_id_str)
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        return (
            query
            .order_by(desc(HealthCheckResult.checked_at))
            .offset(offset)
            .limit(page_size)
            .all()
        )
    
    def count_total(self, system_id: Optional[Union[uuid.UUID, str]] = None, api_id: Optional[Union[uuid.UUID, str]] = None) -> int:
        """计算健康检查结果总数"""
        query = self.db.query(HealthCheckResult)
        
        # 添加过滤条件
        if system_id:
            # 确保system_id是字符串类型
            system_id_str = str(system_id)
            query = query.filter(HealthCheckResult.system_id == system_id_str)
        if api_id:
            # 确保api_id是字符串类型
            api_id_str = str(api_id)
            query = query.filter(HealthCheckResult.api_id == api_id_str)
        
        return query.count()
    
    def delete(self, result_id: Union[uuid.UUID, str]) -> bool:
        """删除健康检查结果"""
        # 确保result_id是字符串类型
        result_id_str = str(result_id)
        result = self.db.query(HealthCheckResult).filter(HealthCheckResult.id == result_id_str).first()
        if result:
            self.db.delete(result)
            self.db.commit()
            return True
        return False
    
    def find_by_batch_id(self, batch_id: str) -> List[HealthCheckResult]:
        """根据批次ID查找健康检查结果"""
        return (
            self.db.query(HealthCheckResult)
            .filter(HealthCheckResult.batch_id == batch_id)
            .order_by(desc(HealthCheckResult.checked_at))
            .all()
        )
    
    def find_batches(self, system_id: Optional[str] = None, environment: Optional[str] = None) -> List[Dict[str, Any]]:
        """查询健康检查批次列表，支持按系统和环境过滤"""
        # 构建基础查询
        query = (
            self.db.query(HealthCheckResult)
            .filter(HealthCheckResult.batch_id.isnot(None))  # 只处理有batch_id的记录
        )
        
        # 添加过滤条件
        if system_id:
            query = query.filter(HealthCheckResult.system_id == system_id)
        if environment:
            query = query.filter(HealthCheckResult.environment == environment)
        
        # 执行查询
        results = query.all()
        
        # 按批次分组
        batches = {}
        for result in results:
            batch_id = result.batch_id
            if batch_id:
                if batch_id not in batches:
                    batches[batch_id] = {
                        'batch_id': batch_id,
                        'system_id': result.system_id,
                        'environment': result.environment,
                        'total_count': 0,
                        'success_count': 0,
                        'failure_count': 0,
                        'checked_at': result.checked_at
                    }
                
                # 更新统计信息
                batches[batch_id]['total_count'] += 1
                if result.status == 'SUCCESS':
                    batches[batch_id]['success_count'] += 1
                else:
                    batches[batch_id]['failure_count'] += 1
                
                # 更新检查时间为最新的
                if result.checked_at > batches[batch_id]['checked_at']:
                    batches[batch_id]['checked_at'] = result.checked_at
        
        # 转换为列表并按检查时间倒序排序
        batch_list = list(batches.values())
        batch_list.sort(key=lambda x: x['checked_at'], reverse=True)
        
        return batch_list
