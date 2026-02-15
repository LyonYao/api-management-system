from enum import Enum


class ApiType(str, Enum):
    """API类型枚举"""
    PROCESS = "P"  # Process API
    SYSTEM = "S"   # System API
    EXTERNAL = "E" # External API
