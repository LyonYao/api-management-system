from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
import uuid

from apimgmt.db.database import Base


class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
