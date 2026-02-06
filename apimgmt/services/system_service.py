from typing import List
import uuid
from datetime import datetime

from apimgmt.repositories.system_repository import SystemRepository
from apimgmt.models.system import System
from apimgmt.schemas.system import CreateSystemRequest, UpdateSystemRequest, SystemDTO
from apimgmt.exceptions import ResourceNotFoundException, DuplicateResourceException, ValidationException


class SystemService:
    def __init__(self, system_repository: SystemRepository):
        self.system_repository = system_repository
    
    def create_system(self, request: CreateSystemRequest) -> SystemDTO:
        """创建系统"""
        # 检查系统名称是否已存在
        existing_system = self.system_repository.find_by_name(request.name)
        if existing_system:
            raise DuplicateResourceException("System", "name", request.name)
        
        # 创建新系统
        system = System(
            id=uuid.uuid4(),
            name=request.name,
            description=request.description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        created_system = self.system_repository.create(system)
        return SystemDTO.model_validate(created_system)
    
    def get_system_by_id(self, system_id: uuid.UUID) -> SystemDTO:
        """根据ID获取系统"""
        system = self.system_repository.find_by_id(system_id)
        if not system:
            raise ResourceNotFoundException("System", system_id)
        return SystemDTO.model_validate(system)
    
    def get_all_systems(self) -> List[SystemDTO]:
        """获取所有系统"""
        systems = self.system_repository.find_all()
        return [SystemDTO.model_validate(system) for system in systems]
    
    def update_system(self, system_id: uuid.UUID, request: UpdateSystemRequest) -> SystemDTO:
        """更新系统"""
        # 查找系统
        system = self.system_repository.find_by_id(system_id)
        if not system:
            raise ResourceNotFoundException("System", system_id)
        
        # 检查名称唯一性（如果更新名称）
        if request.name and request.name != system.name:
            existing_system = self.system_repository.find_by_name(request.name)
            if existing_system:
                raise DuplicateResourceException("System", "name", request.name)
        
        # 更新系统
        if request.name:
            system.name = request.name
        if request.description is not None:
            system.description = request.description
        system.updated_at = datetime.utcnow()
        
        updated_system = self.system_repository.update(system)
        return SystemDTO.model_validate(updated_system)
    
    def delete_system(self, system_id: uuid.UUID) -> None:
        """删除系统"""
        # 查找系统
        system = self.system_repository.find_by_id(system_id)
        if not system:
            raise ResourceNotFoundException("System", system_id)
        
        # 检查是否有关联的API
        api_count = self.system_repository.count_apis_by_system_id(system_id)
        if api_count > 0:
            raise ValidationException(
                f"Cannot delete system. {api_count} API(s) are still associated with this system"
            )
        
        # 删除系统
        self.system_repository.delete(system_id)
