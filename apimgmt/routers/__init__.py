from apimgmt.routers.api_router import router as api_router
from apimgmt.routers.system_router import router as system_router
from apimgmt.routers.endpoint_router import router as endpoint_router
from apimgmt.routers.relationship_router import router as relationship_router
from apimgmt.routers.health_check_router import router as health_check_router

__all__ = [
    "api_router",
    "system_router",
    "endpoint_router",
    "relationship_router",
    "health_check_router"
]
