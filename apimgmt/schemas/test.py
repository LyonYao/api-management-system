from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from ..enums import TestStatus


class EndpointTestDTO(BaseModel):
    id: Optional[str] = None
    endpoint_id: str
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=300)
    environment: str = Field(default="dev", max_length=50)
    headers: Optional[Dict[str, Any]] = None
    request_body: Optional[Dict[str, Any]] = None
    expected_response: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CreateEndpointTestRequest(BaseModel):
    endpoint_id: str
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=300)
    environment: str = Field(default="dev", max_length=50)
    headers: Optional[Dict[str, Any]] = None
    request_body: Optional[Dict[str, Any]] = None
    expected_response: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None


class UpdateEndpointTestRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=300)
    environment: Optional[str] = Field(None, max_length=50)
    headers: Optional[Dict[str, Any]] = None
    request_body: Optional[Dict[str, Any]] = None
    expected_response: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None


class TestResultDTO(BaseModel):
    id: Optional[str] = None
    test_id: str
    endpoint_id: str
    api_id: str
    system_id: str
    environment: str
    batch_id: str
    status: TestStatus
    response_code: Optional[int] = None
    response_time_ms: Optional[int] = None
    request_headers: Optional[Union[Dict[str, Any], List[Any]]] = None
    request_body: Optional[Union[Dict[str, Any], List[Any]]] = None
    response_body: Optional[Union[Dict[str, Any], List[Any]]] = None
    validation_rules: Optional[Union[Dict[str, Any], List[Any]]] = None
    error_message: Optional[str] = None
    request_url: Optional[str] = None
    api_url: Optional[str] = None
    http_method: Optional[str] = None
    executed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TestResultQueryParams(BaseModel):
    system_id: Optional[str] = None
    api_id: Optional[str] = None
    environment: Optional[str] = None
    batch_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[TestStatus] = None
    skip: int = 0
    limit: int = 100


class TestRunResponse(BaseModel):
    run_id: str
    results: List[TestResultDTO]
    total_count: int
    pass_count: int
    fail_count: int
    error_count: int


class TestRunInitiationResponse(BaseModel):
    run_id: str
    total_tests: int
    message: str = "测试已开始执行，请稍后查询结果"


class TestTrendDTO(BaseModel):
    date: datetime
    total_count: int
    pass_count: int
    fail_count: int
    error_count: int
    pass_rate: float


class TestTrendQueryParams(BaseModel):
    system_id: Optional[str] = None
    api_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    interval: str = "day"  # day, week, month


class TestTrendResponse(BaseModel):
    trends: List[TestTrendDTO]
    start_date: datetime
    end_date: datetime
    interval: str


class TestBatchDTO(BaseModel):
    """测试批次DTO"""
    batch_id: str
    executed_at: datetime
    total_count: int
    pass_count: int
    fail_count: int
    error_count: int
    system_id: Optional[str] = None
    system_name: Optional[str] = None
    api_id: Optional[str] = None
    api_name: Optional[str] = None
    environment: Optional[str] = None


class TestBatchListResponse(BaseModel):
    """测试批次列表响应"""
    items: List[TestBatchDTO]
    total: int
