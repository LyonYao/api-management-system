from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..db.database import Base


class EndpointTest(Base):
    __tablename__ = "endpoint_tests"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id = Column(String(36), ForeignKey("endpoints.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(300), nullable=True)
    environment = Column(String(50), nullable=False, default="dev")
    headers = Column(JSON, nullable=True)
    request_body = Column(JSON, nullable=True)
    expected_response = Column(JSON, nullable=True)
    validation_rules = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    endpoint = relationship("Endpoint", backref="endpoint_tests")
    test_results = relationship("TestResult", back_populates="test", cascade="all, delete-orphan")
