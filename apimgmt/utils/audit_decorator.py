from functools import wraps
from typing import Optional, Any, Dict
import inspect

from apimgmt.models.audit import OperationType, ResourceType
from apimgmt.utils.context import UserContext


def audit_log(
    operation_type: OperationType,
    resource_type: ResourceType,
    resource_id_param: Optional[str] = None
):
    """审计日志装饰器
    
    用于在服务层方法执行前后记录审计日志
    
    Args:
        operation_type: 操作类型
        resource_type: 资源类型
        resource_id_param: 资源ID参数名
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # 自动获取操作前数据
            before_data = None
            if operation_type != OperationType.CREATE:
                # 对于非创建操作，尝试从参数中提取数据
                before_data = _extract_data_from_params(func, args, kwargs)
            
            # 执行原始方法
            result = func(self, *args, **kwargs)
            
            # 获取用户信息（在函数执行后获取，确保用户上下文已经被设置）
            user_id = UserContext.get_user_id()
            username = UserContext.get_username()
            ip_address = UserContext.get_ip_address()
            
            # 打印调试信息
            import logging
            logging.info(f"Audit log - User context: user_id={user_id}, username={username}, ip_address={ip_address}")
            
            # 自动获取资源ID
            resource_id = None
            if resource_id_param:
                # 从指定参数中获取资源ID
                if resource_id_param in kwargs:
                    resource_id = kwargs[resource_id_param]
                else:
                    # 尝试从位置参数中获取
                    sig = inspect.signature(func)
                    params = list(sig.parameters.keys())
                    if resource_id_param in params:
                        idx = params.index(resource_id_param)
                        # 位置参数不包含self，所以需要减1
                        if idx > 0 and (idx - 1) < len(args):
                            resource_id = args[idx - 1]
            # 如果是创建操作且资源ID为None，尝试从结果中获取
            if operation_type == OperationType.CREATE and resource_id is None and hasattr(result, "id"):
                resource_id = result.id
            
            # 自动获取操作后数据
            after_data = None
            if result:
                after_data = _extract_data_from_result(result)
            
            # 记录审计日志
            if hasattr(self, "audit_service") and self.audit_service:
                try:
                    # 构建描述
                    description = f"{operation_type.value} {resource_type.value}"
                    if resource_id:
                        description += f": {resource_id}"
                    
                    # 创建审计日志
                    self.audit_service.create_audit_log(
                        operation_type=operation_type,
                        resource_type=resource_type,
                        resource_id=str(resource_id) if resource_id else None,
                        user_id=user_id,
                        username=username,
                        ip_address=ip_address,
                        before_data=before_data,
                        after_data=after_data,
                        description=description
                    )
                    # 打印调试信息
                    import logging
                    logging.info(f"Audit log recorded: {description}")
                except Exception as e:
                    # 审计日志失败不应影响业务逻辑
                    import logging
                    logging.error(f"Failed to log audit: {str(e)}")
            else:
                # 打印调试信息
                import logging
                logging.info("No audit service available")
            
            return result
        return wrapper
    return decorator


def _extract_data_from_params(func, args, kwargs) -> Optional[Dict[str, Any]]:
    """从方法参数中提取数据"""
    try:
        sig = inspect.signature(func)
        bound_args = sig.bind_partial(*args, **kwargs)
        bound_args.apply_defaults()
        
        data = {}
        for name, value in bound_args.arguments.items():
            # 跳过self参数
            if name == "self":
                continue
            # 跳过用户相关参数
            if name in ["user_id", "username", "ip_address"]:
                continue
            # 尝试序列化参数值
            try:
                data[name] = _serialize_value(value)
            except:
                # 如果无法序列化，跳过该参数
                pass
        
        return data if data else None
    except Exception:
        return None


def _extract_data_from_result(result) -> Optional[Dict[str, Any]]:
    """从方法结果中提取数据"""
    try:
        if hasattr(result, "__dict__"):
            # 对于对象，提取其属性
            data = {}
            for attr, value in result.__dict__.items():
                # 跳过私有属性和None值
                if attr.startswith("_") or value is None:
                    continue
                # 尝试序列化属性值
                try:
                    data[attr] = _serialize_value(value)
                except:
                    pass
            return data if data else None
        elif isinstance(result, dict):
            # 对于字典，直接返回
            return result
        else:
            # 对于其他类型，返回其字符串表示
            return {"result": str(result)}
    except Exception:
        return None


def _serialize_value(value) -> Any:
    """序列化值"""
    if hasattr(value, "model_dump"):
        # 对于Pydantic模型，使用model_dump
        return value.model_dump()
    elif isinstance(value, (list, dict, str, int, float, bool, type(None))):
        # 对于基本类型，直接返回
        return value
    else:
        # 对于其他类型，返回其字符串表示
        return str(value)
