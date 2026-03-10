from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from apimgmt.db.database import engine, Base, SessionLocal
# 导入所有模型，确保表被正确创建
from apimgmt.models.api import Api
from apimgmt.models.system import System
from apimgmt.models.endpoint import Endpoint
from apimgmt.models.tag import Tag
from apimgmt.models.api_tag import ApiTag
from apimgmt.models.relationship import Relationship
from apimgmt.models.health_check_result import HealthCheckResult
from apimgmt.models.user import User
from apimgmt.models.audit import AuditLog
from apimgmt.routers import api_router, system_router, endpoint_router, relationship_router, health_check_router, test_router
from apimgmt.routers.auth_router import auth_router
from apimgmt.routers.audit_router import router as audit_router
from apimgmt.middleware.auth_middleware import AuthMiddleware
from apimgmt.middleware.context_middleware import UserContextMiddleware
from apimgmt.repositories.user_repository import UserRepository
from apimgmt.services.auth_service import AuthService
from apimgmt.utils.logger import app_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # 数据库初始化：使用Alembic迁移管理
    # 注意：在生产环境中，应该在部署时执行 `alembic upgrade head`
    # 这里保留create_all()作为备用，确保在没有执行迁移时也能创建基本结构
    try:
        Base.metadata.create_all(bind=engine)
        
        # 初始化admin用户
        db = SessionLocal()
        try:
            user_repository = UserRepository(db)
            auth_service = AuthService(user_repository)
            
            # 检查是否存在admin用户
            admin_user = user_repository.find_by_username("admin")
            if not admin_user:
                # 创建默认admin用户
                admin_user = auth_service.create_user(
                    username="admin",
                    password="admin123",
                    full_name="System Administrator",
                    email="admin@example.com"
                )
                app_logger.info("Admin user created successfully: username=admin, password=admin123")
            else:
                app_logger.info("Admin user already exists")
        except Exception as e:
            app_logger.error(f"Admin user initialization error: {e}")
        finally:
            db.close()
            
    except Exception as e:
        app_logger.error(f"Database initialization error: {e}")
    yield
    # Shutdown
    pass


app = FastAPI(
    title="API Management System",
    description="Microservice API management and topology visualization system",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",  # 保留Swagger UI
    redoc_url=None  # 禁用ReDoc，避免CDN问题
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add user context middleware
app.add_middleware(UserContextMiddleware)

# Add authentication middleware
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(api_router, prefix="/api/v1/apis", tags=["apis"])
app.include_router(system_router, prefix="/api/v1/systems", tags=["systems"])
app.include_router(endpoint_router, prefix="/api/v1/endpoints", tags=["endpoints"])
app.include_router(relationship_router, prefix="/api/v1/relationships", tags=["relationships"])
app.include_router(health_check_router, prefix="/api/v1/health", tags=["health"])
app.include_router(audit_router, prefix="/api/v1/audit", tags=["audit"])
app.include_router(test_router)


@app.get("/")
async def root():
    return {
        "message": "API Management System",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "api-management-system"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
