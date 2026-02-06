class ResourceNotFoundException(Exception):
    """资源未找到异常"""
    def __init__(self, resource_type: str, resource_id):
        super().__init__(f"{resource_type} with id {resource_id} not found")


class DuplicateResourceException(Exception):
    """资源重复异常"""
    def __init__(self, resource_type: str, field: str, value):
        super().__init__(f"{resource_type} with {field} '{value}' already exists")


class ValidationException(Exception):
    """验证异常"""
    def __init__(self, message: str):
        super().__init__(message)


class SystemException(Exception):
    """系统异常"""
    def __init__(self, message: str):
        super().__init__(message)
