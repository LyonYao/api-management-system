# 设计文档

## 概述

API管理系统是一个基于Python的微服务应用，使用FastAPI框架，使用PostgreSQL作为数据存储。系统提供RESTful API用于管理API元数据、调用关系，支持拓扑图可视化和健康检查功能，并集成了认证和审计日志功能。

### 技术栈

- **运行时**: Python 11+
- **框架**: FastAPI (高性能Python Web框架，自动生成OpenAPI文档)
- **数据库**: PostgreSQL
- **API文档**: OpenAPI 3.0 (由FastAPI自动生成)
- **构建工具**: pip
- **数据访问**: SQLAlchemy ORM
- **异步支持**: asyncio 和 httpx
- **认证**: JWT (JSON Web Token)
- **数据库迁移**: Alembic
- **密码加密**: bcrypt

## 架构

### 整体架构

系统采用分层架构设计：

```
┌─────────────────────────────────────┐
│         API Gateway (REST)          │
│           (FastAPI Router)          │
└─────────────────────────────────────┘
                 │
┌─────────────────────────────────────┐
│        Router Layer                 │
│  - api_router                       │
│  - system_router                    │
│  - endpoint_router                  │
│  - relationship_router              │
│  - health_check_router              │
│  - auth_router                      │
│  - audit_router                      │
└─────────────────────────────────────┘
                 │
┌─────────────────────────────────────┐
│         Service Layer               │
│  - ApiService                       │
│  - SystemService                    │
│  - EndpointService                  │
│  - RelationshipService              │
│  - HealthCheckService               │
│  - AuthService                      │
│  - AuditLogService                  │
└─────────────────────────────────────┘
                 │
┌─────────────────────────────────────┐
│       Repository Layer              │
│  - ApiRepository                    │
│  - SystemRepository                 │
│  - EndpointRepository               │
│  - RelationshipRepository           │
│  - TagRepository                    │
│  - HealthCheckResultRepository      │
│  - UserRepository                   │
│  - AuditLogRepository               │
└─────────────────────────────────────┘
                 │
┌─────────────────────────────────────┐
│      PostgreSQL Database            │
│         (Local or Cloud)            │
└─────────────────────────────────────┘
```

### 部署架构

- 使用FastAPI内置的开发服务器或生产级服务器（如Gunicorn + Uvicorn）
- SQLAlchemy ORM用于数据库访问，支持同步和异步操作
- 环境变量配置数据库连接信息和JWT密钥
- 支持容器化部署（如Docker）
- 支持数据库迁移管理（使用Alembic）

## 组件和接口

### 1. Router层

#### api_router
负责API实体的CRUD操作

**端点**:
- `POST /api/v1/apis` - 创建API
- `GET /api/v1/apis/{api_id}` - 获取API详情
- `PUT /api/v1/apis/{api_id}` - 更新API
- `DELETE /api/v1/apis/{api_id}` - 删除API
- `GET /api/v1/apis` - 查询API列表（支持标签筛选和系统ID筛选）

#### endpoint_router
负责Endpoint的CRUD操作

**端点**:
- `POST /api/v1/endpoints` - 创建Endpoint
- `GET /api/v1/endpoints/{endpoint_id}` - 获取Endpoint详情
- `PUT /api/v1/endpoints/{endpoint_id}` - 更新Endpoint
- `DELETE /api/v1/endpoints/{endpoint_id}` - 删除Endpoint
- `GET /api/v1/endpoints` - 查询Endpoint列表
- `GET /api/v1/endpoints/api/{api_id}` - 获取指定API的所有Endpoint

#### system_router
负责系统的CRUD操作

**端点**:
- `POST /api/v1/systems` - 创建系统
- `GET /api/v1/systems/{system_id}` - 获取系统详情
- `PUT /api/v1/systems/{system_id}` - 更新系统
- `DELETE /api/v1/systems/{system_id}` - 删除系统
- `GET /api/v1/systems` - 查询系统列表

#### relationship_router
负责调用关系的管理

**端点**:
- `POST /api/v1/relationships` - 创建调用关系
- `GET /api/v1/relationships/{relationship_id}` - 获取调用关系详情
- `PUT /api/v1/relationships/{relationship_id}` - 更新调用关系
- `DELETE /api/v1/relationships/{relationship_id}` - 删除调用关系
- `GET /api/v1/relationships` - 查询调用关系列表（支持调用方和被调用方筛选）

#### health_check_router
负责API健康检查

**端点**:
- `POST /api/v1/health/check/{endpoint_id}` - 检查单个端点健康状态
- `POST /api/v1/health/batch` - 批量健康检查
- `GET /api/v1/health/results/{endpoint_id}` - 获取端点的健康检查结果
- `GET /api/v1/health/results` - 获取最近的健康检查结果

#### auth_router
负责用户认证

**端点**:
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新访问令牌
- `GET /api/v1/auth/me` - 获取当前用户信息

#### audit_router
负责审计日志管理

**端点**:
- `GET /api/v1/audit` - 获取审计日志列表（支持按操作类型、资源类型、用户名、时间范围等筛选）
- `GET /api/v1/audit/{audit_id}` - 获取单个审计日志详情
- `GET /api/v1/audit/resource/{resource_type}/{resource_id}` - 获取指定资源的审计日志

#### OpenAPI文档
FastAPI自动生成OpenAPI 3.0规格文档

**端点**:
- `GET /docs` - Swagger UI文档
- `GET /redoc` - ReDoc文档
- `GET /openapi.json` - OpenAPI 3.0规格文档

### 2. Service层

#### ApiService
- 业务逻辑：API实体的创建、更新、删除、查询
- 标签管理
- 邮箱格式验证
- 与系统服务的集成

#### SystemService
- 业务逻辑：系统的创建、更新、删除、查询
- 系统关联的API查询
- 系统名称唯一性验证

#### EndpointService
- 业务逻辑：端点的创建、更新、删除、查询
- 与API服务的集成
- 端点路径和方法的验证

#### RelationshipService
- 业务逻辑：调用关系的创建、更新、删除、查询
- 验证调用方和被调用方的存在性
- 支持多态关系（系统或API）
- 与端点服务的集成

#### HealthCheckService
- 执行HTTP健康检查请求
- 异步批量检查
- 结果聚合和存储
- 支持超时处理
- 支持按环境执行健康检查

#### AuthService
- 用户认证和授权
- JWT token生成和验证
- 密码哈希和验证
- 用户信息管理

#### AuditLogService
- 审计日志的创建和查询
- 操作类型和资源类型管理
- 支持按条件筛选审计日志
- 与服务层其他组件的集成

### 3. Repository层

使用SQLAlchemy ORM进行数据访问

#### ApiRepository
```python
class ApiRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, api: Api) -> Api:
        """创建API"""
        self.db.add(api)
        self.db.commit()
        self.db.refresh(api)
        return api
    
    def find_by_id(self, api_id: Union[uuid.UUID, str]) -> Optional[Api]:
        """根据ID查找API"""
        return self.db.query(Api).filter(Api.id == api_id).first()
    
    def find_all(self) -> List[Api]:
        """查找所有API"""
        return self.db.query(Api).order_by(Api.name).all()
    
    def find_by_system_id(self, system_id: Union[uuid.UUID, str]) -> List[Api]:
        """根据系统ID查找API"""
        return self.db.query(Api).filter(Api.system_id == system_id).order_by(Api.name).all()
    
    def find_by_tags(self, tags: Set[str]) -> List[Api]:
        """根据标签查找API"""
        # 实现标签筛选逻辑
        pass
    
    def update(self, api: Api) -> Optional[Api]:
        """更新API"""
        existing_api = self.find_by_id(api.id)
        if existing_api:
            for key, value in api.__dict__.items():
                if key != '_sa_instance_state':
                    setattr(existing_api, key, value)
            self.db.commit()
            self.db.refresh(existing_api)
            return existing_api
        return None
    
    def delete(self, api_id: Union[uuid.UUID, str]) -> bool:
        """删除API"""
        api = self.find_by_id(api_id)
        if api:
            self.db.delete(api)
            self.db.commit()
            return True
        return False
```

#### SystemRepository
```python
class SystemRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, system: System) -> System:
        """创建系统"""
        self.db.add(system)
        self.db.commit()
        self.db.refresh(system)
        return system
    
    def find_by_id(self, system_id: Union[uuid.UUID, str]) -> Optional[System]:
        """根据ID查找系统"""
        return self.db.query(System).filter(System.id == system_id).first()
    
    def find_by_name(self, name: str) -> Optional[System]:
        """根据名称查找系统"""
        return self.db.query(System).filter(System.name == name).first()
    
    def find_all(self) -> List[System]:
        """查找所有系统"""
        return self.db.query(System).order_by(System.name).all()
    
    def update(self, system: System) -> Optional[System]:
        """更新系统"""
        existing_system = self.find_by_id(system.id)
        if existing_system:
            for key, value in system.__dict__.items():
                if key != '_sa_instance_state':
                    setattr(existing_system, key, value)
            self.db.commit()
            self.db.refresh(existing_system)
            return existing_system
        return None
    
    def delete(self, system_id: Union[uuid.UUID, str]) -> bool:
        """删除系统"""
        system = self.find_by_id(system_id)
        if system:
            self.db.delete(system)
            self.db.commit()
            return True
        return False
```

#### EndpointRepository
```python
class EndpointRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, endpoint: Endpoint) -> Endpoint:
        """创建端点"""
        self.db.add(endpoint)
        self.db.commit()
        self.db.refresh(endpoint)
        return endpoint
    
    def find_by_id(self, endpoint_id: Union[uuid.UUID, str]) -> Optional[Endpoint]:
        """根据ID查找端点"""
        return self.db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
    
    def find_by_api_id(self, api_id: Union[uuid.UUID, str]) -> List[Endpoint]:
        """根据API ID查找端点"""
        return self.db.query(Endpoint).filter(Endpoint.api_id == api_id).order_by(Endpoint.path, Endpoint.method).all()
    
    def find_all(self) -> List[Endpoint]:
        """查找所有端点"""
        return self.db.query(Endpoint).order_by(Endpoint.path, Endpoint.method).all()
    
    def update(self, endpoint: Endpoint) -> Optional[Endpoint]:
        """更新端点"""
        existing_endpoint = self.find_by_id(endpoint.id)
        if existing_endpoint:
            for key, value in endpoint.__dict__.items():
                if key != '_sa_instance_state':
                    setattr(existing_endpoint, key, value)
            self.db.commit()
            self.db.refresh(existing_endpoint)
            return existing_endpoint
        return None
    
    def delete(self, endpoint_id: Union[uuid.UUID, str]) -> bool:
        """删除端点"""
        endpoint = self.find_by_id(endpoint_id)
        if endpoint:
            self.db.delete(endpoint)
            self.db.commit()
            return True
        return False
```

#### RelationshipRepository
```python
class RelationshipRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, relationship: Relationship) -> Relationship:
        """创建调用关系"""
        self.db.add(relationship)
        self.db.commit()
        self.db.refresh(relationship)
        return relationship
    
    def find_by_id(self, relationship_id: Union[uuid.UUID, str]) -> Optional[Relationship]:
        """根据ID查找调用关系"""
        return self.db.query(Relationship).filter(Relationship.id == relationship_id).first()
    
    def find_all(self) -> List[Relationship]:
        """查找所有调用关系"""
        return self.db.query(Relationship).all()
    
    def find_by_caller(self, caller_type: str, caller_id: Union[uuid.UUID, str]) -> List[Relationship]:
        """根据调用方查找调用关系"""
        return self.db.query(Relationship).filter(
            Relationship.caller_type == caller_type,
            Relationship.caller_id == caller_id
        ).all()
    
    def find_by_callee(self, callee_type: str, callee_id: Union[uuid.UUID, str]) -> List[Relationship]:
        """根据被调用方查找调用关系"""
        return self.db.query(Relationship).filter(
            Relationship.callee_type == callee_type,
            Relationship.callee_id == callee_id
        ).all()
    
    def update(self, relationship: Relationship) -> Optional[Relationship]:
        """更新调用关系"""
        existing_relationship = self.find_by_id(relationship.id)
        if existing_relationship:
            for key, value in relationship.__dict__.items():
                if key != '_sa_instance_state':
                    setattr(existing_relationship, key, value)
            self.db.commit()
            self.db.refresh(existing_relationship)
            return existing_relationship
        return None
    
    def delete(self, relationship_id: Union[uuid.UUID, str]) -> bool:
        """删除调用关系"""
        relationship = self.find_by_id(relationship_id)
        if relationship:
            self.db.delete(relationship)
            self.db.commit()
            return True
        return False
```

#### TagRepository
```python
class TagRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, name: str) -> Tag:
        """创建标签"""
        # 检查标签是否已存在
        existing_tag = self.find_by_name(name)
        if existing_tag:
            return existing_tag
        
        # 创建新标签
        tag = Tag(name=name)
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag
    
    def find_by_name(self, name: str) -> Optional[Tag]:
        """根据名称查找标签"""
        return self.db.query(Tag).filter(Tag.name == name).first()
    
    def find_by_id(self, tag_id: Union[uuid.UUID, str]) -> Optional[Tag]:
        """根据ID查找标签"""
        return self.db.query(Tag).filter(Tag.id == tag_id).first()
    
    def find_all(self) -> List[Tag]:
        """查找所有标签"""
        return self.db.query(Tag).order_by(Tag.name).all()
    
    def delete(self, tag_id: Union[uuid.UUID, str]) -> bool:
        """删除标签"""
        tag = self.find_by_id(tag_id)
        if tag:
            self.db.delete(tag)
            self.db.commit()
            return True
        return False
```

#### HealthCheckResultRepository
```python
class HealthCheckResultRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, health_check_result: HealthCheckResult) -> HealthCheckResult:
        """创建健康检查结果"""
        self.db.add(health_check_result)
        self.db.commit()
        self.db.refresh(health_check_result)
        return health_check_result
    
    def find_by_id(self, result_id: Union[uuid.UUID, str]) -> Optional[HealthCheckResult]:
        """根据ID查找健康检查结果"""
        return self.db.query(HealthCheckResult).filter(HealthCheckResult.id == result_id).first()
    
    def find_by_endpoint_id(self, endpoint_id: Union[uuid.UUID, str]) -> List[HealthCheckResult]:
        """根据端点ID查找健康检查结果"""
        return self.db.query(HealthCheckResult).filter(
            HealthCheckResult.endpoint_id == endpoint_id
        ).order_by(desc(HealthCheckResult.checked_at)).all()
    
    def find_latest_by_endpoint_id(self, endpoint_id: Union[uuid.UUID, str]) -> Optional[HealthCheckResult]:
        """查找端点的最新健康检查结果"""
        return self.db.query(HealthCheckResult).filter(
            HealthCheckResult.endpoint_id == endpoint_id
        ).order_by(desc(HealthCheckResult.checked_at)).first()
    
    def delete(self, result_id: Union[uuid.UUID, str]) -> bool:
        """删除健康检查结果"""
        result = self.find_by_id(result_id)
        if result:
            self.db.delete(result)
            self.db.commit()
            return True
        return False
```

#### UserRepository
```python
class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user: User) -> User:
        """创建用户"""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def find_by_id(self, user_id: Union[uuid.UUID, str]) -> Optional[User]:
        """根据ID查找用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def find_by_username(self, username: str) -> Optional[User]:
        """根据用户名查找用户"""
        return self.db.query(User).filter(User.username == username).first()
    
    def find_all(self) -> List[User]:
        """查找所有用户"""
        return self.db.query(User).all()
    
    def update(self, user: User) -> Optional[User]:
        """更新用户"""
        existing_user = self.find_by_id(user.id)
        if existing_user:
            for key, value in user.__dict__.items():
                if key != '_sa_instance_state':
                    setattr(existing_user, key, value)
            self.db.commit()
            self.db.refresh(existing_user)
            return existing_user
        return None
    
    def delete(self, user_id: Union[uuid.UUID, str]) -> bool:
        """删除用户"""
        user = self.find_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
```

#### AuditLogRepository
```python
class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, audit_log: AuditLog) -> AuditLog:
        """创建审计日志"""
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        return audit_log
    
    def find_by_id(self, audit_id: Union[uuid.UUID, str]) -> Optional[AuditLog]:
        """根据ID查找审计日志"""
        return self.db.query(AuditLog).filter(AuditLog.id == audit_id).first()
    
    def find_all(self, operation_type: Optional[str] = None, resource_type: Optional[str] = None, 
                 username: Optional[str] = None, start_date: Optional[datetime] = None, 
                 end_date: Optional[datetime] = None, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """根据条件查找审计日志"""
        query = self.db.query(AuditLog)
        
        if operation_type:
            query = query.filter(AuditLog.operation_type == operation_type)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if username:
            query = query.filter(AuditLog.username == username)
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        return query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
    
    def find_by_resource(self, resource_type: str, resource_id: Union[uuid.UUID, str]) -> List[AuditLog]:
        """查找指定资源的审计日志"""
        return self.db.query(AuditLog).filter(
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == resource_id
        ).order_by(desc(AuditLog.timestamp)).all()
```

## 数据模型

### 实体关系图

```mermaid
erDiagram
    SYSTEM ||--o{ API : contains
    API ||--o{ ENDPOINT : has
    API ||--o{ API_TAG : has
    TAG ||--o{ API_TAG : tagged
    ENDPOINT }o--o{ RELATIONSHIP : participates
    SYSTEM }o--o{ RELATIONSHIP : participates
    RELATIONSHIP ||--o| HEALTH_CHECK_RESULT : has
    USER ||--o{ AUDIT_LOG : generates

    SYSTEM {
        string id PK
        string name
        string system_code
        text description
        timestamp created_at
        timestamp updated_at
    }

    API {
        string id PK
        string system_id FK
        string name
        text description
        string api_type
        string auth_type
        string spec_link
        string department
        string contact_name
        text contact_emails
        string dev_host
        string uat_host
        string prod_host
        string health_check_path
        json health_check_rule
        timestamp created_at
        timestamp updated_at
    }

    ENDPOINT {
        string id PK
        string api_id FK
        string path
        string http_method
        text description
        string status
        timestamp online_date
        timestamp created_at
        timestamp updated_at
    }

    TAG {
        string id PK
        string name
        timestamp created_at
    }

    API_TAG {
        string api_id FK
        string tag_id FK
    }

    RELATIONSHIP {
        string id PK
        string caller_type
        string caller_id
        string callee_type
        string callee_id
        string endpoint_id FK
        string auth_type
        json auth_config
        text description
        timestamp created_at
        timestamp updated_at
    }

    HEALTH_CHECK_RESULT {
        string id PK
        string endpoint_id FK
        string status
        int response_code
        int response_time_ms
        text error_message
        timestamp checked_at
    }

    USER {
        string id PK
        string username UK
        string password_hash
        string email
        string role
        timestamp created_at
        timestamp updated_at
    }

    AUDIT_LOG {
        string id PK
        string username
        string operation_type
        string resource_type
        string resource_id
        json before_data
        json after_data
        timestamp timestamp
    }
```

### 数据库表结构

#### systems表
```sql
CREATE TABLE systems (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    system_code VARCHAR(12) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_systems_name ON systems(name);
CREATE INDEX idx_systems_system_code ON systems(system_code);
```

#### apis表
```sql
CREATE TABLE apis (
    id VARCHAR(36) PRIMARY KEY,
    system_id VARCHAR(36) NOT NULL REFERENCES systems(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    api_type VARCHAR(1) NOT NULL DEFAULT 'S',
    auth_type VARCHAR(50),
    spec_link VARCHAR(500),
    department VARCHAR(255),
    contact_name VARCHAR(255),
    contact_emails TEXT, -- 逗号分隔的邮箱列表
    dev_host VARCHAR(500), -- 开发环境Host
    uat_host VARCHAR(500), -- 测试环境Host
    prod_host VARCHAR(500), -- 生产环境Host
    health_check_path VARCHAR(500), -- 健康检查路径
    health_check_rule TEXT, -- JSON格式的健康检查规则
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_api_type CHECK (api_type IN ('P', 'S', 'E'))
);

CREATE INDEX idx_apis_system_id ON apis(system_id);
CREATE INDEX idx_apis_name ON apis(name);
```

#### endpoints表
```sql
CREATE TABLE endpoints (
    id VARCHAR(36) PRIMARY KEY,
    api_id VARCHAR(36) NOT NULL REFERENCES apis(id) ON DELETE CASCADE,
    path VARCHAR(500) NOT NULL,
    http_method VARCHAR(20) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'DEVELOPING',
    online_date TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_endpoint_status CHECK (status IN ('DEVELOPING', 'TESTING', 'ONLINE'))
);

CREATE INDEX idx_endpoints_api_id ON endpoints(api_id);
CREATE INDEX idx_endpoints_path ON endpoints(path);
```

#### tags表
```sql
CREATE TABLE tags (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tags_name ON tags(name);
```

#### api_tags表
```sql
CREATE TABLE api_tags (
    api_id VARCHAR(36) NOT NULL REFERENCES apis(id) ON DELETE CASCADE,
    tag_id VARCHAR(36) NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (api_id, tag_id)
);

CREATE INDEX idx_api_tags_tag_id ON api_tags(tag_id);
```

#### relationships表
```sql
CREATE TABLE relationships (
    id VARCHAR(36) PRIMARY KEY,
    caller_type VARCHAR(50) NOT NULL,
    caller_id VARCHAR(36) NOT NULL,
    callee_type VARCHAR(50) NOT NULL,
    callee_id VARCHAR(36) NOT NULL,
    endpoint_id VARCHAR(36) REFERENCES endpoints(id) ON DELETE CASCADE,
    auth_type VARCHAR(50),
    auth_config JSON,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_relationships_caller ON relationships(caller_type, caller_id);
CREATE INDEX idx_relationships_callee ON relationships(callee_type, callee_id);
CREATE INDEX idx_relationships_endpoint ON relationships(endpoint_id);
```

#### health_check_results表
```sql
CREATE TABLE health_check_results (
    id VARCHAR(36) PRIMARY KEY,
    endpoint_id VARCHAR(36) NOT NULL REFERENCES endpoints(id) ON DELETE CASCADE,
    api_id VARCHAR(36),
    system_id VARCHAR(36),
    status VARCHAR(50) NOT NULL,
    response_code INT,
    response_time_ms INT,
    error_message TEXT,
    checked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_health_check_results_api_id ON health_check_results(api_id);
CREATE INDEX idx_health_check_results_system_id ON health_check_results(system_id);
CREATE INDEX idx_health_check_results_checked_at ON health_check_results(checked_at);
CREATE INDEX idx_health_check_results_endpoint_id ON health_check_results(endpoint_id);
```

#### users表
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL DEFAULT 'USER',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

#### audit_logs表
```sql
CREATE TABLE audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    operation_type VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(36),
    before_data JSONB,
    after_data JSONB,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_username ON audit_logs(username);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_operation ON audit_logs(operation_type);
```

### Python实体类（SQLAlchemy模型）

#### System
```python
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class System(Base):
    __tablename__ = "systems"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    system_code = Column(String(12), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    apis = relationship("Api", back_populates="system", cascade="all, delete-orphan")
```

#### Api
```python
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..database import Base

class Api(Base):
    __tablename__ = "apis"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    system_id = Column(String(36), ForeignKey("systems.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    api_type = Column(String(1), nullable=False, default="S")
    auth_type = Column(String(50), nullable=True)
    spec_link = Column(String(500), nullable=True)
    department = Column(String(255), nullable=True)
    contact_name = Column(String(255), nullable=True)
    contact_emails = Column(Text, nullable=True)
    dev_host = Column(String(500), nullable=True)
    uat_host = Column(String(500), nullable=True)
    prod_host = Column(String(500), nullable=True)
    health_check_path = Column(String(500), nullable=True)
    health_check_rule = Column(Text, nullable=True)  # JSON格式存储健康检查规则
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("api_type IN ('P', 'S', 'E')", name="chk_api_type"),
    )
    
    # Relationships
    system = relationship("System", back_populates="apis")
    endpoints = relationship("Endpoint", back_populates="api", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="api_tags", back_populates="apis")
```

#### Endpoint
```python
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..database import Base

class Endpoint(Base):
    __tablename__ = "endpoints"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    api_id = Column(String(36), ForeignKey("apis.id"), nullable=False)
    path = Column(String(500), nullable=False)
    http_method = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="DEVELOPING")
    online_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('DEVELOPING', 'TESTING', 'ONLINE')", name="chk_endpoint_status"),
    )
    
    # Relationships
    api = relationship("Api", back_populates="endpoints")
    relationships = relationship("Relationship", back_populates="endpoint")
    health_check_results = relationship("HealthCheckResult", back_populates="endpoint", cascade="all, delete-orphan")
```

#### Tag
```python
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..database import Base

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    apis = relationship("Api", secondary="api_tags", back_populates="tags")
```

#### Relationship
```python
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..database import Base

class Relationship(Base):
    __tablename__ = "relationships"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    caller_type = Column(String(50), nullable=False)
    caller_id = Column(String(36), nullable=False)
    callee_type = Column(String(50), nullable=False)
    callee_id = Column(String(36), nullable=False)
    endpoint_id = Column(String(36), ForeignKey("endpoints.id"), nullable=True)
    auth_type = Column(String(50), nullable=True)
    auth_config = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    endpoint = relationship("Endpoint", back_populates="relationships")
```

#### HealthCheckResult
```python
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..database import Base

class HealthCheckResult(Base):
    __tablename__ = "health_check_results"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id = Column(String(36), ForeignKey("endpoints.id"), nullable=False)
    api_id = Column(String(36), nullable=True)
    system_id = Column(String(36), nullable=True)
    status = Column(String(50), nullable=False)
    response_code = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 索引
    __table_args__ = (
        Index('idx_health_check_results_api_id', 'api_id'),
        Index('idx_health_check_results_system_id', 'system_id'),
        Index('idx_health_check_results_checked_at', 'checked_at'),
    )
    
    # Relationships
    endpoint = relationship("Endpoint", back_populates="health_check_results")
```

#### User
```python
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
import uuid
from ..database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    role = Column(String(50), nullable=False, default="USER")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

#### AuditLog
```python
from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.sql import func
import uuid
from ..database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), nullable=False)
    operation_type = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(36), nullable=True)
    before_data = Column(JSON, nullable=True)
    after_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
```

### 枚举类型

```python
from enum import Enum

class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class AuthType(str, Enum):
    API_KEY = "API_KEY"
    OAUTH2 = "OAUTH2"
    BASIC_AUTH = "BASIC_AUTH"
    JWT = "JWT"
    NONE = "NONE"

class EntityType(str, Enum):
    SYSTEM = "SYSTEM"
    API = "API"

class HealthCheckStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    TIMEOUT = "TIMEOUT"

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class OperationType(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    READ = "READ"

class ResourceType(str, Enum):
    SYSTEM = "SYSTEM"
    API = "API"
    ENDPOINT = "ENDPOINT"
    RELATIONSHIP = "RELATIONSHIP"
    USER = "USER"
```

## API规格 (OpenAPI 3.0)

### 核心DTO定义

#### ApiDTO
```python
from pydantic import BaseModel, Field
from typing import List, Set, Optional, Dict, Any
from datetime import datetime
from .enums import AuthType

class ApiDTO(BaseModel):
    id: Optional[str] = None
    system_id: Optional[str] = None
    system_name: Optional[str] = None
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    auth_type: Optional[AuthType] = None
    spec_link: Optional[str] = Field(None, max_length=1000)
    department: Optional[str] = Field(None, max_length=255)
    contact_name: Optional[str] = Field(None, max_length=255)
    contact_emails: List[str] = []  # 邮箱列表
    tags: Set[str] = set()
    uat_host: Optional[str] = Field(None, max_length=500)  # 测试环境Host
    prod_host: Optional[str] = Field(None, max_length=500)  # 生产环境Host
    health_check_path: Optional[str] = Field(None, max_length=1000)  # 健康检查路径
    health_check_rule: Optional[Dict[str, Any]] = None  # 健康检查规则
    endpoints: List['EndpointDTO'] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

#### CreateApiRequest
```python
from pydantic import BaseModel, Field, EmailStr
from typing import List, Set, Optional, Dict, Any
from .enums import AuthType

class CreateApiRequest(BaseModel):
    system_id: str
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    auth_type: Optional[AuthType] = None
    spec_link: Optional[str] = Field(None, max_length=1000)
    department: Optional[str] = Field(None, max_length=255)
    contact_name: Optional[str] = Field(None, max_length=255)
    contact_emails: List[EmailStr] = []  # 邮箱列表，每个邮箱都需要验证格式
    tags: Optional[Set[str]] = set()
    uat_host: Optional[str] = Field(None, max_length=500)  # 测试环境Host
    prod_host: Optional[str] = Field(None, max_length=500)  # 生产环境Host
    health_check_path: Optional[str] = Field(None, max_length=1000)  # 健康检查路径
    health_check_rule: Optional[Dict[str, Any]] = None  # 健康检查规则
```

#### EndpointDTO
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .enums import HttpMethod

class EndpointDTO(BaseModel):
    id: Optional[str] = None
    api_id: Optional[str] = None
    path: str = Field(..., max_length=1000)
    method: HttpMethod
    description: Optional[str] = Field(None, max_length=2000)
    dev_host: Optional[str] = Field(None, max_length=500)  # 开发环境Host
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

#### CreateEndpointRequest
```python
from pydantic import BaseModel, Field
from typing import Optional
from .enums import HttpMethod

class CreateEndpointRequest(BaseModel):
    api_id: str
    path: str = Field(..., max_length=1000)
    method: HttpMethod
    description: Optional[str] = Field(None, max_length=2000)
    dev_host: Optional[str] = Field(None, max_length=500)  # 开发环境Host
```

#### RelationshipDTO
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from .enums import EntityType, AuthType, HttpMethod

class RelationshipDTO(BaseModel):
    id: Optional[str] = None
    caller_type: EntityType
    caller_id: str
    caller_name: Optional[str] = None
    callee_type: EntityType
    callee_id: str
    callee_name: Optional[str] = None
    endpoint_id: str
    endpoint_path: Optional[str] = None
    endpoint_method: Optional[HttpMethod] = None
    auth_type: Optional[AuthType] = None
    auth_config: Optional[Dict[str, Any]] = None
    description: Optional[str] = Field(None, max_length=2000)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

#### CreateRelationshipRequest
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from .enums import EntityType, AuthType

class CreateRelationshipRequest(BaseModel):
    caller_type: EntityType
    caller_id: str
    callee_type: EntityType
    callee_id: str
    endpoint_id: str  # 必须指定调用的endpoint
    auth_type: Optional[AuthType] = None
    auth_config: Optional[Dict[str, Any]] = None
    description: Optional[str] = Field(None, max_length=2000)
```

#### TopologyDTO
```python
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from .enums import EntityType, AuthType

class NodeDTO(BaseModel):
    id: str
    name: str
    type: EntityType
    metadata: Optional[Dict[str, Any]] = None

class EdgeDTO(BaseModel):
    id: str
    source_id: str
    target_id: str
    auth_type: Optional[AuthType] = None
    metadata: Optional[Dict[str, Any]] = None

class TopologyDTO(BaseModel):
    nodes: List[NodeDTO]
    edges: List[EdgeDTO]
```

#### HealthCheckResultDTO
```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .enums import HttpMethod, HealthCheckStatus

class HealthCheckResultDTO(BaseModel):
    endpoint_id: str
    endpoint_path: Optional[str] = None
    http_method: Optional[HttpMethod] = None
    status: HealthCheckStatus
    response_code: Optional[int] = None
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    checked_at: datetime
    
    class Config:
        from_attributes = True

class BatchHealthCheckRequest(BaseModel):
    endpoint_ids: List[str]

class BatchHealthCheckResponse(BaseModel):
    batch_id: str
    results: List[HealthCheckResultDTO]
    total_count: int
    success_count: int
    failure_count: int

#### Auth DTOs

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: str
    username: str
    role: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserInfoDTO(BaseModel):
    id: str
    username: str
    email: str
    role: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

#### Audit Log DTOs

class AuditLogDTO(BaseModel):
    id: str
    username: str
    operation_type: str
    resource_type: str
    resource_id: Optional[str] = None
    before_data: Optional[Dict[str, Any]] = None
    after_data: Optional[Dict[str, Any]] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True

class AuditLogQueryParams(BaseModel):
    operation_type: Optional[str] = None
    resource_type: Optional[str] = None
    username: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = 0
    limit: int = 100
```

### OpenAPI规格文档结构

系统将生成完整的OpenAPI 3.0规格文档，包含：

1. **基本信息**
   - 标题：API Management System
   - 版本：1.0.0
   - 描述：微服务API管理和拓扑可视化系统

2. **服务器配置**
   - 开发环境URL
   - 生产环境URL

3. **认证方案**
   - Bearer Token (JWT)

4. **所有端点定义**
   - 路径、方法、参数
   - 请求体schema
   - 响应schema
   - 错误响应

5. **数据模型schemas**
   - 所有DTO的JSON Schema定义
   - 枚举类型定义

## 错误处理

### 错误响应格式

```python
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class ErrorResponse(BaseModel):
    error: str
    message: str
    path: str
    timestamp: datetime
    details: Optional[Dict[str, str]] = None
```

### HTTP状态码使用

- `200 OK` - 成功的GET/PUT请求
- `201 Created` - 成功的POST请求
- `204 No Content` - 成功的DELETE请求
- `400 Bad Request` - 请求参数验证失败
- `404 Not Found` - 资源不存在
- `409 Conflict` - 资源冲突（如重复创建）
- `500 Internal Server Error` - 服务器内部错误

### 异常处理器

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Optional
from datetime import datetime

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "path": request.url.path,
            "timestamp": datetime.utcnow(),
            "details": None
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """请求参数验证异常处理器"""
    details = {}
    for error in exc.errors():
        field = error.get("loc")[-1] if error.get("loc") else "unknown"
        details[field] = error.get("msg")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation Error",
            "message": "请求参数验证失败",
            "path": request.url.path,
            "timestamp": datetime.utcnow(),
            "details": details
        }
    )
```

## 测试策略

### 单元测试

- 使用pytest和unittest.mock
- 测试Service层业务逻辑
- 测试Repository层SQL查询逻辑
- 目标覆盖率：80%以上

### 集成测试

- 使用pytest和SQLAlchemy的测试工具
- 使用SQLite内存数据库进行快速测试
- 测试完整的API端点
- 测试异步数据库操作

### 性能测试

- API响应时间测试（目标<500ms）
- 批量健康检查性能测试
- 数据库查询性能测试

### 测试数据

- 使用SQLAlchemy的create_all()方法创建测试数据库schema
- 使用fixture和factory_boy生成测试数据

## 部署配置

### FastAPI配置 (.env)

```env
# 数据库配置
DATABASE_URL=postgresql://localhost:5432/apimgmt
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=postgres

# 应用配置
APP_NAME=API Management System
APP_VERSION=1.0.0
DEBUG=False

# CORS配置
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# 健康检查配置
HEALTH_CHECK_TIMEOUT=30

# JWT配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=480  # 8小时
REFRESH_TOKEN_EXPIRE_MINUTES=1440  # 24小时
ALGORITHM=HS256

# 认证配置
AUTH_REQUIRED=True
```

### 应用配置 (config.py)

```python
import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """应用配置"""
    # 应用配置
    app_name: str = "API Management System"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 数据库配置
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost:5432/apimgmt")
    
    # CORS配置
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # 健康检查配置
    health_check_timeout: int = int(os.getenv("HEALTH_CHECK_TIMEOUT", "30"))
    
    # JWT配置
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
    refresh_token_expire_minutes: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "1440"))
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    
    # 认证配置
    auth_required: bool = os.getenv("AUTH_REQUIRED", "True").lower() == "true"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### AWS Lambda配置

- 内存：1024 MB
- 超时：30秒
- 环境变量：
  - `DATABASE_URL`
  - `DATABASE_USERNAME`
  - `DATABASE_PASSWORD`
  - `APP_NAME`
  - `APP_VERSION`
  - `SECRET_KEY`
  - `ACCESS_TOKEN_EXPIRE_MINUTES`
  - `REFRESH_TOKEN_EXPIRE_MINUTES`
  - `ALGORITHM`
  - `AUTH_REQUIRED`
- VPC配置：连接到RDS所在VPC

### 数据库迁移

使用SQLAlchemy的自动迁移或Alembic进行数据库版本管理：

```python
# 使用SQLAlchemy自动创建表结构
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apimgmt.database import Base
from apimgmt.models import System, Api, Endpoint, Tag, Relationship, HealthCheckResult, User, AuditLog

# 创建引擎
engine = create_engine(settings.database_url)

# 创建所有表
Base.metadata.create_all(bind=engine)
```

### 启动脚本

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apimgmt.config import settings
from apimgmt.routers import api_router, system_router, endpoint_router, relationship_router, health_check_router, auth_router, audit_router
from apimgmt.database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="微服务API管理和拓扑可视化系统"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")
app.include_router(endpoint_router, prefix="/api/v1")
app.include_router(relationship_router, prefix="/api/v1")
app.include_router(health_check_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")

# 根路径
@app.get("/")
async def root():
    return {"message": "API Management System", "version": settings.app_version}

# 启动应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 安全考虑

1. **API认证**：使用JWT token验证请求
2. **SQL注入防护**：使用SQLAlchemy ORM的参数化查询
3. **输入验证**：使用Pydantic验证所有输入
4. **敏感信息**：auth_config使用加密存储
5. **CORS配置**：使用FastAPI的CORSMiddleware配置允许的前端域名

## 性能优化

1. **数据库索引**：在常用查询字段上创建索引
2. **连接池**：使用SQLAlchemy的连接池管理数据库连接
3. **缓存**：考虑使用Redis缓存拓扑图数据
4. **异步处理**：健康检查使用异步执行
5. **分页**：列表查询支持分页
6. **异步API**：使用FastAPI的异步支持提高并发性能
