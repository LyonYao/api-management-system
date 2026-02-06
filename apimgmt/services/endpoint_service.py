from typing import List
import uuid
from datetime import datetime

from apimgmt.repositories.endpoint_repository import EndpointRepository
from apimgmt.repositories.api_repository import ApiRepository
from apimgmt.models.endpoint import Endpoint
from apimgmt.schemas.endpoint import CreateEndpointRequest, UpdateEndpointRequest, EndpointDTO
from apimgmt.exceptions import ResourceNotFoundException


class EndpointService:
    def __init__(self, endpoint_repository: EndpointRepository, api_repository: ApiRepository):
        self.endpoint_repository = endpoint_repository
        self.api_repository = api_repository
    
    def create_endpoint(self, request: CreateEndpointRequest) -> EndpointDTO:
        """创建端点"""
        # 验证API是否存在
        api = self.api_repository.find_by_id(request.api_id)
        if not api:
            raise ResourceNotFoundException("API", request.api_id)
        
        # 创建端点
        endpoint = Endpoint(
            id=uuid.uuid4(),
            api_id=request.api_id,
            path=request.path,
            http_method=request.http_method.value,
            description=request.description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        created_endpoint = self.endpoint_repository.create(endpoint)
        return EndpointDTO.model_validate(created_endpoint)
    
    def get_endpoint_by_id(self, endpoint_id: uuid.UUID) -> EndpointDTO:
        """根据ID获取端点"""
        endpoint = self.endpoint_repository.find_by_id(endpoint_id)
        if not endpoint:
            raise ResourceNotFoundException("Endpoint", endpoint_id)
        return EndpointDTO.model_validate(endpoint)
    
    def get_endpoints_by_api_id(self, api_id: uuid.UUID) -> List[EndpointDTO]:
        """根据API ID获取端点"""
        # 验证API是否存在
        api = self.api_repository.find_by_id(api_id)
        if not api:
            raise ResourceNotFoundException("API", api_id)
        
        endpoints = self.endpoint_repository.find_by_api_id(api_id)
        return [EndpointDTO.model_validate(endpoint) for endpoint in endpoints]
    
    def get_all_endpoints(self) -> List[EndpointDTO]:
        """获取所有端点"""
        endpoints = self.endpoint_repository.find_all()
        return [EndpointDTO.model_validate(endpoint) for endpoint in endpoints]
    
    def update_endpoint(self, endpoint_id: uuid.UUID, request: UpdateEndpointRequest) -> EndpointDTO:
        """更新端点"""
        # 查找端点
        endpoint = self.endpoint_repository.find_by_id(endpoint_id)
        if not endpoint:
            raise ResourceNotFoundException("Endpoint", endpoint_id)
        
        # 更新字段
        if request.path:
            endpoint.path = request.path
        if request.http_method:
            endpoint.http_method = request.http_method.value
        if request.description is not None:
            endpoint.description = request.description
        endpoint.updated_at = datetime.utcnow()
        
        updated_endpoint = self.endpoint_repository.update(endpoint)
        return EndpointDTO.model_validate(updated_endpoint)
    
    def delete_endpoint(self, endpoint_id: uuid.UUID) -> None:
        """删除端点"""
        # 验证端点是否存在
        endpoint = self.endpoint_repository.find_by_id(endpoint_id)
        if not endpoint:
            raise ResourceNotFoundException("Endpoint", endpoint_id)
        
        # 删除端点
        self.endpoint_repository.delete(endpoint_id)
