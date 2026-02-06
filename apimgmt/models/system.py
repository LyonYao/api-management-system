from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
import uuid

from apimgmt.db.database import Base


class System(Base):
    __tablename__ = "systems"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
