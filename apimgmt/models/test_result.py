from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..db.database import Base


class TestResult(Base):
    __tablename__ = "test_results"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_id = Column(String(36), ForeignKey("endpoint_tests.id"), nullable=False)
    endpoint_id = Column(String(36), ForeignKey("endpoints.id"), nullable=False)
    api_id = Column(String(36), ForeignKey("apis.id"), nullable=False)
    system_id = Column(String(36), ForeignKey("systems.id"), nullable=False)
    batch_id = Column(String(50), ForeignKey("test_batches.batch_id"), nullable=False)
    environment = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    response_code = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    request_headers = Column(JSON, nullable=True)
    request_body = Column(JSON, nullable=True)
    response_body = Column(JSON, nullable=True)
    validation_rules = Column(JSON, nullable=True)
    error_message = Column(String(500), nullable=True)
    request_url = Column(String(500), nullable=True)
    api_url = Column(String(500), nullable=True)
    http_method = Column(String(20), nullable=True)
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    test = relationship("EndpointTest", back_populates="test_results")
    endpoint = relationship("Endpoint", backref="test_results")
    api = relationship("Api", backref="test_results")
    system = relationship("System", backref="test_results")
    batch = relationship("TestBatch", back_populates="test_results")
