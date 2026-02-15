from typing import Optional
import contextvars

# 创建上下文变量
_user_id_var = contextvars.ContextVar('user_id', default=None)
_username_var = contextvars.ContextVar('username', default=None)
_ip_address_var = contextvars.ContextVar('ip_address', default=None)

class UserContext:
    """用户上下文管理器"""
    
    @staticmethod
    def set_user_context(user_id: Optional[str] = None, username: Optional[str] = None, ip_address: Optional[str] = None):
        """设置用户上下文"""
        _user_id_var.set(user_id)
        _username_var.set(username)
        _ip_address_var.set(ip_address)
    
    @staticmethod
    def get_user_id() -> Optional[str]:
        """获取用户ID"""
        return _user_id_var.get()
    
    @staticmethod
    def get_username() -> Optional[str]:
        """获取用户名"""
        return _username_var.get()
    
    @staticmethod
    def get_ip_address() -> Optional[str]:
        """获取IP地址"""
        return _ip_address_var.get()
    
    @staticmethod
    def reset():
        """重置用户上下文"""
        _user_id_var.set(None)
        _username_var.set(None)
        _ip_address_var.set(None)