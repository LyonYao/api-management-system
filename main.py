from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from apimgmt.db.database import engine, Base
# 导入所有模型，确保表被正确创建
from apimgmt.models.api import Api
from apimgmt.models.system import System
from apimgmt.models.endpoint import Endpoint
from apimgmt.models.tag import Tag
from apimgmt.models.api_tag import ApiTag
from apimgmt.models.relationship import Relationship
from apimgmt.models.health_check_result import HealthCheckResult
from apimgmt.routers import api_router, system_router, endpoint_router, relationship_router, health_check_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # 数据库初始化：使用Alembic迁移管理
    # 注意：在生产环境中，应该在部署时执行 `alembic upgrade head`
    # 这里保留create_all()作为备用，确保在没有执行迁移时也能创建基本结构
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Database initialization error: {e}")
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

# Include routers
app.include_router(api_router, prefix="/api/v1/apis", tags=["apis"])
app.include_router(system_router, prefix="/api/v1/systems", tags=["systems"])
app.include_router(endpoint_router, prefix="/api/v1/endpoints", tags=["endpoints"])
app.include_router(relationship_router, prefix="/api/v1/relationships", tags=["relationships"])
app.include_router(health_check_router, prefix="/api/v1/health", tags=["health"])


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
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
