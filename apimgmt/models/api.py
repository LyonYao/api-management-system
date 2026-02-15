from sqlalchemy import Column, String, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.sql import func
import uuid

from apimgmt.db.database import Base


class Api(Base):
    __tablename__ = "apis"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    system_id = Column(String(36), ForeignKey("systems.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    api_type = Column(String(1), nullable=False, default="S")
    auth_type = Column(String(50), nullable=True)
    spec_link = Column(String(500), nullable=True)
    department = Column(String(255), nullable=True)
    contact_name = Column(String(255), nullable=True)
    contact_emails = Column(Text, nullable=True)
    dev_host = Column(String(500), nullable=True)
    uat_host = Column(String(500), nullable=True)
    prod_host = Column(String(500), nullable=True)
    health_check_path = Column(String(500), nullable=True)
    health_check_rule = Column(Text, nullable=True)  # JSON格式存储健康检查规则
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint("api_type IN ('P', 'S', 'E')", name="chk_api_type"),
    )
