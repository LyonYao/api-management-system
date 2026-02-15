from sqlalchemy import Column, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
import uuid
import enum

from apimgmt.db.database import Base


class OperationType(str, enum.Enum):
    """操作类型枚举"""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class ResourceType(str, enum.Enum):
    """资源类型枚举"""
    API = "API"
    SYSTEM = "SYSTEM"
    ENDPOINT = "ENDPOINT"
    RELATIONSHIP = "RELATIONSHIP"
    USER = "USER"


class AuditLog(Base):
    """审计日志模型"""
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    operation_type = Column(SQLEnum(OperationType), nullable=False)
    resource_type = Column(SQLEnum(ResourceType), nullable=False)
    resource_id = Column(String(500), nullable=False)  # 增加长度限制
    before_data = Column(Text, nullable=True)  # 操作前的数据，JSON格式
    after_data = Column(Text, nullable=True)   # 操作后的数据，JSON格式
    user_id = Column(String(36), nullable=True)
    username = Column(String(100), nullable=True)
    ip_address = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
