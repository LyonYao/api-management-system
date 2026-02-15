from typing import List, Optional
import uuid
from datetime import datetime
import json

from apimgmt.repositories.endpoint_repository import EndpointRepository
from apimgmt.repositories.api_repository import ApiRepository
from apimgmt.services.audit_service import AuditLogService
from apimgmt.models.endpoint import Endpoint
from apimgmt.schemas.endpoint import CreateEndpointRequest, UpdateEndpointRequest, EndpointDTO
from apimgmt.enums.endpoint_status import EndpointStatus
from apimgmt.exceptions import ResourceNotFoundException
from apimgmt.utils.audit_decorator import audit_log
from apimgmt.models.audit import OperationType, ResourceType


class EndpointService:
    def __init__(self, endpoint_repository: EndpointRepository, api_repository: ApiRepository, audit_service: Optional[AuditLogService] = None):
        self.endpoint_repository = endpoint_repository
        self.api_repository = api_repository
        self.audit_service = audit_service
    
    @audit_log(
        operation_type=OperationType.CREATE,
        resource_type=ResourceType.ENDPOINT
    )
    def create_endpoint(self, request: CreateEndpointRequest) -> EndpointDTO:
        """创建端点"""
        # 验证API是否存在
        api = self.api_repository.find_by_id(request.api_id)
        if not api:
            raise ResourceNotFoundException("API", request.api_id)
        
        # 创建端点
        endpoint = Endpoint(
            id=str(uuid.uuid4()),
            api_id=request.api_id,
            path=request.path,
            http_method=request.http_method,
            description=request.description,
            status=request.status.value,
            online_date=request.online_date,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        created_endpoint = self.endpoint_repository.create(endpoint)
        
        # 转换为DTO
        dto = EndpointDTO(
            id=created_endpoint.id,
            api_id=created_endpoint.api_id,
            path=created_endpoint.path,
            http_method=created_endpoint.http_method,
            description=created_endpoint.description,
            status=EndpointStatus(created_endpoint.status),
            online_date=created_endpoint.online_date,
            created_at=created_endpoint.created_at,
            updated_at=created_endpoint.updated_at
        )
        
        return dto
    
    def get_endpoint_by_id(self, endpoint_id: str) -> EndpointDTO:
        """根据ID获取端点"""
        endpoint = self.endpoint_repository.find_by_id(endpoint_id)
        if not endpoint:
            raise ResourceNotFoundException("Endpoint", endpoint_id)
        
        # 转换为DTO
        dto = EndpointDTO(
            id=endpoint.id,
            api_id=endpoint.api_id,
            path=endpoint.path,
            http_method=endpoint.http_method,
            description=endpoint.description,
            status=EndpointStatus(endpoint.status),
            online_date=endpoint.online_date,
            created_at=endpoint.created_at,
            updated_at=endpoint.updated_at
        )
        return dto
    
    def get_endpoints_by_api_id(self, api_id: str) -> List[EndpointDTO]:
        """根据API ID获取端点"""
        # 验证API是否存在
        api = self.api_repository.find_by_id(api_id)
        if not api:
            raise ResourceNotFoundException("API", api_id)
        
        endpoints = self.endpoint_repository.find_by_api_id(api_id)
        
        # 转换为DTO列表
        dto_list = []
        for endpoint in endpoints:
            dto = EndpointDTO(
                id=endpoint.id,
                api_id=endpoint.api_id,
                path=endpoint.path,
                http_method=endpoint.http_method,
                description=endpoint.description,
                status=EndpointStatus(endpoint.status),
                online_date=endpoint.online_date,
                created_at=endpoint.created_at,
                updated_at=endpoint.updated_at
            )
            dto_list.append(dto)
        
        return dto_list
    
    def get_all_endpoints(self) -> List[EndpointDTO]:
        """获取所有端点"""
        endpoints = self.endpoint_repository.find_all()
        
        # 转换为DTO列表
        dto_list = []
        for endpoint in endpoints:
            dto = EndpointDTO(
                id=endpoint.id,
                api_id=endpoint.api_id,
                path=endpoint.path,
                http_method=endpoint.http_method,
                description=endpoint.description,
                status=EndpointStatus(endpoint.status),
                online_date=endpoint.online_date,
                created_at=endpoint.created_at,
                updated_at=endpoint.updated_at
            )
            dto_list.append(dto)
        
        return dto_list
    
    @audit_log(
        operation_type=OperationType.UPDATE,
        resource_type=ResourceType.ENDPOINT,
        resource_id_param="endpoint_id"
    )
    def update_endpoint(self, endpoint_id: str, request: UpdateEndpointRequest) -> EndpointDTO:
        """更新端点"""
        # 查找端点
        endpoint = self.endpoint_repository.find_by_id(endpoint_id)
        if not endpoint:
            raise ResourceNotFoundException("Endpoint", endpoint_id)
        
        # 更新字段
        if request.path:
            endpoint.path = request.path
        if request.http_method:
            endpoint.http_method = request.http_method
        if request.description is not None:
            endpoint.description = request.description
        if request.status is not None:
            endpoint.status = request.status.value
        if request.online_date is not None:
            endpoint.online_date = request.online_date
        endpoint.updated_at = datetime.utcnow()
        
        updated_endpoint = self.endpoint_repository.update(endpoint)
        
        # 转换为DTO
        dto = EndpointDTO(
            id=updated_endpoint.id,
            api_id=updated_endpoint.api_id,
            path=updated_endpoint.path,
            http_method=updated_endpoint.http_method,
            description=updated_endpoint.description,
            status=EndpointStatus(updated_endpoint.status),
            online_date=updated_endpoint.online_date,
            created_at=updated_endpoint.created_at,
            updated_at=updated_endpoint.updated_at
        )
        
        return dto
    
    @audit_log(
        operation_type=OperationType.DELETE,
        resource_type=ResourceType.ENDPOINT,
        resource_id_param="endpoint_id"
    )
    def delete_endpoint(self, endpoint_id: str) -> None:
        """删除端点"""
        # 验证端点是否存在
        endpoint = self.endpoint_repository.find_by_id(endpoint_id)
        if not endpoint:
            raise ResourceNotFoundException("Endpoint", endpoint_id)
        
        # 删除端点
        self.endpoint_repository.delete(endpoint_id)
