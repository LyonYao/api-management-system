from typing import List, Optional, Set
import uuid
from datetime import datetime
import json

from apimgmt.repositories.api_repository import ApiRepository
from apimgmt.repositories.system_repository import SystemRepository
from apimgmt.repositories.tag_repository import TagRepository
from apimgmt.services.audit_service import AuditLogService
from apimgmt.models.api import Api
from apimgmt.schemas.api import CreateApiRequest, UpdateApiRequest, ApiDTO
from apimgmt.enums.api_type import ApiType
from apimgmt.exceptions import ResourceNotFoundException, ValidationException
from apimgmt.utils.audit_decorator import audit_log
from apimgmt.models.audit import OperationType, ResourceType


class ApiService:
    def __init__(self, api_repository: ApiRepository, system_repository: SystemRepository, tag_repository: TagRepository, audit_service: Optional[AuditLogService] = None):
        self.api_repository = api_repository
        self.system_repository = system_repository
        self.tag_repository = tag_repository
        self.audit_service = audit_service
    
    @audit_log(
        operation_type=OperationType.CREATE,
        resource_type=ResourceType.API
    )
    def create_api(self, request: CreateApiRequest) -> ApiDTO:
        """创建API"""
        # 验证系统是否存在
        system = self.system_repository.find_by_id(request.system_id)
        if not system:
            raise ResourceNotFoundException("System", request.system_id)
        
        # 创建API
        contact_emails_str = ",".join(request.contact_emails)
        api = Api(
            id=str(uuid.uuid4()),
            system_id=request.system_id,
            name=request.name,
            description=request.description,
            api_type=request.api_type.value,
            auth_type=request.auth_type.value if request.auth_type else None,
            spec_link=request.spec_link,
            department=request.department,
            contact_name=request.contact_name,
            contact_emails=contact_emails_str,
            dev_host=request.dev_host,
            uat_host=request.uat_host,
            prod_host=request.prod_host,
            health_check_path=request.health_check_path,
            health_check_rule=request.health_check_rule,  # 直接存储字符串值
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        created_api = self.api_repository.create(api)
        
        # 处理标签
        if request.tags:
            self.associate_tags_to_api(created_api.id, request.tags)
        
        # 获取标签
        tags = self.api_repository.get_api_tags(created_api.id)
        
        return ApiDTO(
            id=created_api.id,
            system_id=created_api.system_id,
            system_name=system.name,
            name=created_api.name,
            description=created_api.description,
            api_type=request.api_type,
            auth_type=request.auth_type,
            spec_link=created_api.spec_link,
            department=created_api.department,
            contact_name=created_api.contact_name,
            contact_emails=request.contact_emails,
            tags=tags,
            dev_host=created_api.dev_host,
            uat_host=created_api.uat_host,
            prod_host=created_api.prod_host,
            health_check_path=created_api.health_check_path,
            health_check_rule=created_api.health_check_rule,
            endpoints=[],
            created_at=created_api.created_at,
            updated_at=created_api.updated_at
        )
    
    def get_api_by_id(self, api_id: str) -> ApiDTO:
        """根据ID获取API"""
        api = self.api_repository.find_by_id(api_id)
        if not api:
            raise ResourceNotFoundException("API", api_id)
        
        # 获取系统名称
        system = self.system_repository.find_by_id(api.system_id)
        system_name = system.name if system else None
        
        # 获取标签
        tags = self.api_repository.get_api_tags(api.id)
        
        # 解析联系邮箱
        contact_emails = []
        if api.contact_emails:
            contact_emails = [email.strip() for email in api.contact_emails.split(",") if email.strip()]
        
        return ApiDTO(
            id=api.id,
            system_id=api.system_id,
            system_name=system_name,
            name=api.name,
            description=api.description,
            api_type=ApiType(api.api_type),
            auth_type=api.auth_type,
            spec_link=api.spec_link,
            department=api.department,
            contact_name=api.contact_name,
            contact_emails=contact_emails,
            tags=tags,
            dev_host=api.dev_host,
            uat_host=api.uat_host,
            prod_host=api.prod_host,
            health_check_path=api.health_check_path,
            health_check_rule=api.health_check_rule,
            endpoints=[],
            created_at=api.created_at,
            updated_at=api.updated_at
        )
    
    def get_all_apis(self) -> List[ApiDTO]:
        """获取所有API"""
        apis = self.api_repository.find_all()
        return self.enrich_apis_with_system_names(apis)
    
    def get_apis_by_system_id(self, system_id: str) -> List[ApiDTO]:
        """根据系统ID获取API"""
        # 验证系统是否存在
        system = self.system_repository.find_by_id(system_id)
        if not system:
            raise ResourceNotFoundException("System", system_id)
        
        apis = self.api_repository.find_by_system_id(system_id)
        return [self._api_to_dto(api, system.name) for api in apis]
    
    def get_apis_by_tags(self, tags: Set[str]) -> List[ApiDTO]:
        """根据标签获取API"""
        if not tags:
            return self.get_all_apis()
        
        apis = self.api_repository.find_by_tags(tags)
        return self.enrich_apis_with_system_names(apis)
    
    @audit_log(
        operation_type=OperationType.UPDATE,
        resource_type=ResourceType.API,
        resource_id_param="api_id"
    )
    def update_api(self, api_id: str, request: UpdateApiRequest) -> ApiDTO:
        """更新API"""
        # 查找API
        api = self.api_repository.find_by_id(api_id)
        if not api:
            raise ResourceNotFoundException("API", api_id)
        
        # 更新字段
        if request.name:
            api.name = request.name
        if request.description is not None:
            api.description = request.description
        if request.api_type is not None:
            api.api_type = request.api_type.value
        if request.auth_type is not None:
            api.auth_type = request.auth_type.value if request.auth_type else None
        if request.spec_link is not None:
            api.spec_link = request.spec_link
        if request.department is not None:
            api.department = request.department
        if request.contact_name is not None:
            api.contact_name = request.contact_name
        if request.contact_emails is not None:
            api.contact_emails = ",".join(request.contact_emails)
        if request.dev_host is not None:
            api.dev_host = request.dev_host
        if request.uat_host is not None:
            api.uat_host = request.uat_host
        if request.prod_host is not None:
            api.prod_host = request.prod_host
        if request.health_check_path is not None:
            api.health_check_path = request.health_check_path
        if request.health_check_rule is not None:
            api.health_check_rule = request.health_check_rule  # 直接存储字符串值
        api.updated_at = datetime.utcnow()
        
        updated_api = self.api_repository.update(api)
        
        # 处理标签更新
        if request.tags is not None:
            # 清除现有标签
            self.api_repository.clear_tags(api_id)
            # 添加新标签
            if request.tags:
                self.associate_tags_to_api(api_id, request.tags)
        
        # 获取系统名称
        system = self.system_repository.find_by_id(updated_api.system_id)
        system_name = system.name if system else None
        
        # 获取标签
        tags = self.api_repository.get_api_tags(updated_api.id)
        
        # 解析联系邮箱
        contact_emails = []
        if updated_api.contact_emails:
            contact_emails = [email.strip() for email in updated_api.contact_emails.split(",") if email.strip()]
        
        return ApiDTO(
            id=updated_api.id,
            system_id=updated_api.system_id,
            system_name=system_name,
            name=updated_api.name,
            description=updated_api.description,
            api_type=request.api_type if request.api_type else ApiType(updated_api.api_type),
            auth_type=request.auth_type if request.auth_type else updated_api.auth_type,
            spec_link=updated_api.spec_link,
            department=updated_api.department,
            contact_name=updated_api.contact_name,
            contact_emails=contact_emails,
            tags=tags,
            dev_host=updated_api.dev_host,
            uat_host=updated_api.uat_host,
            prod_host=updated_api.prod_host,
            health_check_path=updated_api.health_check_path,
            health_check_rule=updated_api.health_check_rule,
            endpoints=[],
            created_at=updated_api.created_at,
            updated_at=updated_api.updated_at
        )
    
    @audit_log(
        operation_type=OperationType.DELETE,
        resource_type=ResourceType.API,
        resource_id_param="api_id"
    )
    def delete_api(self, api_id: str) -> None:
        """删除API"""
        # 验证API是否存在
        api = self.api_repository.find_by_id(api_id)
        if not api:
            raise ResourceNotFoundException("API", api_id)
        
        # 删除API
        self.api_repository.delete(api_id)
    
    def associate_tags_to_api(self, api_id: str, tag_names: Set[str]) -> None:
        """关联标签到API"""
        if not tag_names:
            return
        
        # 查找或创建标签
        tag_ids = set()
        for tag_name in tag_names:
            tag = self.tag_repository.find_or_create(tag_name)
            tag_ids.add(tag.id)
        
        # 关联标签
        self.api_repository.associate_tags(api_id, tag_ids)
    
    def enrich_apis_with_system_names(self, apis: List[Api]) -> List[ApiDTO]:
        """为API添加系统名称"""
        if not apis:
            return []
        
        # 获取所有系统
        systems = self.system_repository.find_all()
        system_name_map = {system.id: system.name for system in systems}
        
        return [self._api_to_dto(api, system_name_map.get(api.system_id)) for api in apis]
    
    def _api_to_dto(self, api: Api, system_name: Optional[str]) -> ApiDTO:
        """将API模型转换为DTO"""
        # 获取标签
        tags = self.api_repository.get_api_tags(api.id)
        
        # 解析联系邮箱
        contact_emails = []
        if api.contact_emails:
            contact_emails = [email.strip() for email in api.contact_emails.split(",") if email.strip()]
        
        return ApiDTO(
            id=api.id,
            system_id=api.system_id,
            system_name=system_name,
            name=api.name,
            description=api.description,
            api_type=ApiType(api.api_type),
            auth_type=api.auth_type,
            spec_link=api.spec_link,
            department=api.department,
            contact_name=api.contact_name,
            contact_emails=contact_emails,
            tags=tags,
            dev_host=api.dev_host,
            uat_host=api.uat_host,
            prod_host=api.prod_host,
            health_check_path=api.health_check_path,
            health_check_rule=api.health_check_rule,
            endpoints=[],
            created_at=api.created_at,
            updated_at=api.updated_at
        )
