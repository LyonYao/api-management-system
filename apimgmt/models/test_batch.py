from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..db.database import Base


class TestBatch(Base):
    __tablename__ = "test_batches"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String(50), unique=True, nullable=False, index=True)
    system_id = Column(String(36), ForeignKey("systems.id"), nullable=False)
    api_id = Column(String(36), ForeignKey("apis.id"), nullable=True)
    environment = Column(String(50), nullable=False)
    total_count = Column(Integer, nullable=False, default=0)
    pass_count = Column(Integer, nullable=False, default=0)
    fail_count = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=False, default="RUNNING")
    
    # Relationships
    system = relationship("System", backref="test_batches")
    api = relationship("Api", backref="test_batches")
    test_results = relationship("TestResult", back_populates="batch", cascade="all, delete-orphan")
