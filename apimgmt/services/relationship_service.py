from typing import List
import uuid
from datetime import datetime

from apimgmt.repositories.relationship_repository import RelationshipRepository
from apimgmt.repositories.api_repository import ApiRepository
from apimgmt.repositories.endpoint_repository import EndpointRepository
from apimgmt.models.relationship import Relationship
from apimgmt.schemas.relationship import CreateRelationshipRequest, UpdateRelationshipRequest, RelationshipDTO
from apimgmt.exceptions import ResourceNotFoundException


class RelationshipService:
    def __init__(self, relationship_repository: RelationshipRepository, api_repository: ApiRepository, endpoint_repository: EndpointRepository):
        self.relationship_repository = relationship_repository
        self.api_repository = api_repository
        self.endpoint_repository = endpoint_repository
    
    def create_relationship(self, request: CreateRelationshipRequest) -> RelationshipDTO:
        """创建调用关系"""
        # 验证端点是否存在
        if request.endpoint_id:
            endpoint = self.endpoint_repository.find_by_id(request.endpoint_id)
            if not endpoint:
                raise ResourceNotFoundException("Endpoint", request.endpoint_id)
        
        # 创建调用关系
        relationship = Relationship(
            id=uuid.uuid4(),
            caller_type=request.caller_type,
            caller_id=request.caller_id,
            callee_type=request.callee_type,
            callee_id=request.callee_id,
            endpoint_id=request.endpoint_id,
            auth_type=request.auth_type,
            auth_config=request.auth_config,
            description=request.description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        created_relationship = self.relationship_repository.create(relationship)
        return RelationshipDTO.model_validate(created_relationship)
    
    def get_relationship_by_id(self, relationship_id: uuid.UUID) -> RelationshipDTO:
        """根据ID获取调用关系"""
        relationship = self.relationship_repository.find_by_id(relationship_id)
        if not relationship:
            raise ResourceNotFoundException("Relationship", relationship_id)
        return RelationshipDTO.model_validate(relationship)
    
    def get_all_relationships(self) -> List[RelationshipDTO]:
        """获取所有调用关系"""
        relationships = self.relationship_repository.find_all()
        return [RelationshipDTO.model_validate(relationship) for relationship in relationships]
    
    def get_relationships_by_caller(self, caller_type: str, caller_id: uuid.UUID) -> List[RelationshipDTO]:
        """根据调用方获取调用关系"""
        relationships = self.relationship_repository.find_by_caller(caller_type, caller_id)
        return [RelationshipDTO.model_validate(relationship) for relationship in relationships]
    
    def get_relationships_by_callee(self, callee_type: str, callee_id: uuid.UUID) -> List[RelationshipDTO]:
        """根据被调用方获取调用关系"""
        relationships = self.relationship_repository.find_by_callee(callee_type, callee_id)
        return [RelationshipDTO.model_validate(relationship) for relationship in relationships]
    
    def update_relationship(self, relationship_id: uuid.UUID, request: UpdateRelationshipRequest) -> RelationshipDTO:
        """更新调用关系"""
        # 查找调用关系
        relationship = self.relationship_repository.find_by_id(relationship_id)
        if not relationship:
            raise ResourceNotFoundException("Relationship", relationship_id)
        
        # 更新字段
        if request.caller_type:
            relationship.caller_type = request.caller_type
        if request.caller_id:
            relationship.caller_id = request.caller_id
        if request.callee_type:
            relationship.callee_type = request.callee_type
        if request.callee_id:
            relationship.callee_id = request.callee_id
        if request.endpoint_id:
            # 验证端点是否存在
            endpoint = self.endpoint_repository.find_by_id(request.endpoint_id)
            if not endpoint:
                raise ResourceNotFoundException("Endpoint", request.endpoint_id)
            relationship.endpoint_id = request.endpoint_id
        if request.auth_type is not None:
            relationship.auth_type = request.auth_type
        if request.auth_config is not None:
            relationship.auth_config = request.auth_config
        if request.description is not None:
            relationship.description = request.description
        relationship.updated_at = datetime.utcnow()
        
        updated_relationship = self.relationship_repository.update(relationship)
        return RelationshipDTO.model_validate(updated_relationship)
    
    def delete_relationship(self, relationship_id: uuid.UUID) -> None:
        """删除调用关系"""
        # 验证调用关系是否存在
        relationship = self.relationship_repository.find_by_id(relationship_id)
        if not relationship:
            raise ResourceNotFoundException("Relationship", relationship_id)
        
        # 删除调用关系
        self.relationship_repository.delete(relationship_id)
