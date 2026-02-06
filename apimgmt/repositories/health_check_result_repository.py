from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid
from typing import List, Optional, Union

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
        return self.db.query(HealthCheckResult).filter(HealthCheckResult.id == result_id).first()
    
    def find_by_endpoint_id(self, endpoint_id: Union[uuid.UUID, str]) -> List[HealthCheckResult]:
        """根据端点ID查找健康检查结果"""
        return (
            self.db.query(HealthCheckResult)
            .filter(HealthCheckResult.endpoint_id == endpoint_id)
            .order_by(desc(HealthCheckResult.checked_at))
            .all()
        )
    
    def find_by_endpoint_id_ordered_by_time(self, endpoint_id: Union[uuid.UUID, str]) -> List[HealthCheckResult]:
        """根据端点ID查找健康检查结果，按时间排序"""
        return self.find_by_endpoint_id(endpoint_id)
    
    def find_latest_by_endpoint_id(self, endpoint_id: Union[uuid.UUID, str]) -> Optional[HealthCheckResult]:
        """查找端点的最新健康检查结果"""
        return (
            self.db.query(HealthCheckResult)
            .filter(HealthCheckResult.endpoint_id == endpoint_id)
            .order_by(desc(HealthCheckResult.checked_at))
            .first()
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
    
    def delete(self, result_id: Union[uuid.UUID, str]) -> bool:
        """删除健康检查结果"""
        result = self.db.query(HealthCheckResult).filter(HealthCheckResult.id == result_id).first()
        if result:
            self.db.delete(result)
            self.db.commit()
            return True
        return False
