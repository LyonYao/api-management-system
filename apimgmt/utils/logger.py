import logging
import os
from logging.handlers import RotatingFileHandler

# 创建日志目录
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 配置根日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=10485760,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)

# 创建不同模块的日志记录器
def get_logger(name):
    """获取指定名称的日志记录器"""
    return logging.getLogger(name)

# 常用的日志记录器
app_logger = get_logger('app')
audit_logger = get_logger('audit')
auth_logger = get_logger('auth')
db_logger = get_logger('db')
api_logger = get_logger('api')
