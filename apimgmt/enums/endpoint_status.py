from enum import Enum


class EndpointStatus(str, Enum):
    """Endpoint状态枚举"""
    DEVELOPING = "DEVELOPING"  # 在开发
    TESTING = "TESTING"        # 在测试
    ONLINE = "ONLINE"          # 已上线
