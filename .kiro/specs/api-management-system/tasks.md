# 实施计划

- [x] 1. 项目初始化和基础设施搭建
  - 创建Maven项目结构，配置Quarkus依赖
  - 配置Quarkus Reactive PostgreSQL Client和Flyway
  - 配置AWS Lambda部署相关依赖
  - 创建application.properties配置文件
  - _需求: 8.1, 8.2, 8.3_

- [x] 2. 数据库Schema设计和迁移脚本
  - [x] 2.1 创建systems表迁移脚本
    - 编写V1__create_systems_table.sql
    - 包含id, name, description, created_at, updated_at字段
    - 创建name字段的唯一索引
    - _需求: 1.2, 5.1_

  - [x] 2.2 创建apis表迁移脚本
    - 编写V2__create_apis_table.sql
    - 包含id, system_id, name, description, auth_type, spec_link, department, contact_name, contact_emails字段
    - 创建system_id和name的索引
    - _需求: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 5.1, 5.2, 5.3_

  - [x] 2.3 创建endpoints表迁移脚本
    - 编写V3__create_endpoints_table.sql
    - 包含id, api_id, path, http_method, description字段
    - 创建api_id和path的索引
    - 添加(api_id, path, http_method)的唯一约束
    - _需求: 1.2, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [x] 2.4 创建tags和api_tags表迁移脚本
    - 编写V4__create_tags_table.sql和V5__create_api_tags_table.sql
    - tags表包含id, name, created_at字段
    - api_tags表为多对多关联表
    - 创建必要的索引和外键约束
    - _需求: 1.4, 6.1, 6.2, 6.3, 6.4_

  - [x] 2.5 创建relationships表迁移脚本
    - 编写V6__create_relationships_table.sql
    - 包含caller_type, caller_id, callee_type, callee_id, endpoint_id, auth_type, auth_config, description字段
    - 创建caller, callee, endpoint的索引
    - _需求: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_

  - [x] 2.6 创建health_check_results表迁移脚本
    - 编写V7__create_health_check_results_table.sql
    - 包含id, endpoint_id, status, response_code, response_time_ms, error_message, checked_at字段
    - 创建endpoint_id和checked_at的索引
    - _需求: 4.4, 4.5, 4.6_

- [x] 3. 实体类和枚举定义
  - [x] 3.1 创建枚举类型
    - 实现HttpMethod枚举(GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
    - 实现AuthType枚举(API_KEY, OAUTH2, BASIC_AUTH, JWT, NONE)
    - 实现EntityType枚举(SYSTEM, API)
    - 实现HealthCheckStatus枚举(SUCCESS, FAILURE, TIMEOUT)
    - _需求: 1.2, 1.6, 7.4_

  - [x] 3.2 创建实体类
    - 实现SystemEntity POJO
    - 实现ApiEntity POJO，包含contactEmails的helper方法
    - 实现EndpointEntity POJO
    - 实现TagEntity POJO
    - 实现RelationshipEntity POJO
    - 实现HealthCheckResultEntity POJO
    - _需求: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_

- [x] 4. Repository层实现
  - [x] 4.1 实现SystemRepository
    - 实现create, findById, findByName, findAll, update, delete方法
    - 使用PgPool执行SQL查询
    - 实现Row到SystemEntity的映射方法
    - _需求: 1.1, 1.2_

  - [x] 4.2 实现ApiRepository
    - 实现create, findById, findAll, findBySystemId, findByTags, update, delete方法
    - 实现联表查询获取tags信息
    - 实现contactEmails的存储和读取逻辑
    - _需求: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 5.3, 5.4, 6.2_

  - [x] 4.3 实现EndpointRepository
    - 实现create, findById, findByApiId, findAll, update, delete方法
    - 实现Row到EndpointEntity的映射方法
    - _需求: 1.2, 7.6_

  - [x] 4.4 实现TagRepository
    - 实现create, findByName, findAll, delete方法
    - 实现标签的创建和查询逻辑
    - _需求: 6.1, 6.4_

  - [x] 4.5 实现RelationshipRepository
    - 实现create, findById, findAll, findByCaller, findByCallee, update, delete方法
    - 实现JSONB类型的auth_config存储和读取
    - 实现多表联查获取调用方、被调用方和endpoint的详细信息
    - _需求: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_

  - [x] 4.6 实现HealthCheckResultRepository
    - 实现create, findByEndpointId, findRecent方法
    - 实现按时间排序的查询
    - _需求: 4.5, 4.6_

- [x] 5. DTO和请求/响应类定义
  - [x] 5.1 创建System相关DTO
    - 实现SystemDTO
    - 实现CreateSystemRequest和UpdateSystemRequest
    - 添加Bean Validation注解
    - _需求: 1.1, 1.2_

  - [x] 5.2 创建API相关DTO
    - 实现ApiDTO，包含endpoints列表和contactEmails列表
    - 实现CreateApiRequest和UpdateApiRequest
    - 添加邮箱列表的验证逻辑
    - _需求: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 5.3, 5.4, 5.6_

  - [x] 5.3 创建Endpoint相关DTO
    - 实现EndpointDTO
    - 实现CreateEndpointRequest和UpdateEndpointRequest
    - _需求: 1.2, 7.6_

  - [x] 5.4 创建Relationship相关DTO
    - 实现RelationshipDTO，包含endpoint详细信息
    - 实现CreateRelationshipRequest和UpdateRelationshipRequest
    - _需求: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_

  - [x] 5.5 创建Topology相关DTO
    - 实现TopologyDTO, NodeDTO, EdgeDTO
    - 设计节点和边的metadata结构
    - _需求: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [x] 5.6 创建HealthCheck相关DTO
    - 实现HealthCheckResultDTO
    - 实现BatchHealthCheckRequest和BatchHealthCheckResponse
    - _需求: 4.3, 4.4, 4.5, 4.6_

  - [x] 5.7 创建通用错误响应DTO
    - 实现ErrorResponse类
    - 包含error, message, path, timestamp, details字段
    - _需求: 所有需求的错误处理_

- [x] 6. Service层业务逻辑实现
  - [x] 6.1 实现SystemService
    - 实现系统的CRUD业务逻辑
    - 实现系统名称唯一性验证
    - 实现系统删除时的级联检查
    - _需求: 1.1, 1.2_

  - [x] 6.2 实现ApiService
    - 实现API的CRUD业务逻辑
    - 实现标签的关联和管理
    - 实现contactEmails的验证逻辑（每个邮箱格式验证）
    - 实现按标签筛选API的逻辑
    - _需求: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.1, 6.2, 6.3_

  - [x] 6.3 实现EndpointService
    - 实现Endpoint的CRUD业务逻辑
    - 实现(api_id, path, http_method)唯一性验证
    - 实现按API查询endpoints的逻辑
    - _需求: 1.2, 7.6_

  - [x] 6.4 实现RelationshipService
    - 实现调用关系的CRUD业务逻辑
    - 验证caller和callee的存在性（根据类型查询system或api）
    - 验证endpoint_id的存在性和归属关系
    - 实现调用关系的查询和筛选逻辑
    - _需求: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_

  - [x] 6.5 实现TopologyService
    - 实现拓扑图数据的构建逻辑
    - 从systems, apis, relationships表聚合数据
    - 构建nodes列表（区分系统和API节点）
    - 构建edges列表（包含endpoint信息）
    - 实现按标签筛选拓扑图的逻辑
    - _需求: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 6.5_

  - [x] 6.6 实现HealthCheckService
    - 实现单个endpoint的健康检查逻辑
    - 使用Vert.x WebClient发送HTTP请求
    - 记录响应状态码和响应时间
    - 实现批量健康检查的异步执行
    - 实现按系统批量检查的逻辑（查询系统下所有API的所有endpoints）
    - 保存健康检查结果到数据库
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [x] 7. Controller层REST API实现
  - [x] 7.1 实现SystemController
    - 实现POST /api/v1/systems创建系统
    - 实现GET /api/v1/systems/{id}获取系统详情
    - 实现PUT /api/v1/systems/{id}更新系统
    - 实现DELETE /api/v1/systems/{id}删除系统
    - 实现GET /api/v1/systems查询系统列表
    - 添加OpenAPI注解
    - _需求: 1.1, 1.2_

  - [x] 7.2 实现ApiController
    - 实现POST /api/v1/apis创建API
    - 实现GET /api/v1/apis/{id}获取API详情（包含endpoints）
    - 实现PUT /api/v1/apis/{id}更新API
    - 实现DELETE /api/v1/apis/{id}删除API
    - 实现GET /api/v1/apis查询API列表（支持标签筛选）
    - 实现GET /api/v1/apis/search按系统搜索API
    - 添加OpenAPI注解
    - _需求: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 6.2, 6.3_

  - [x] 7.3 实现EndpointController
    - 实现POST /api/v1/endpoints创建Endpoint
    - 实现GET /api/v1/endpoints/{id}获取Endpoint详情
    - 实现PUT /api/v1/endpoints/{id}更新Endpoint
    - 实现DELETE /api/v1/endpoints/{id}删除Endpoint
    - 实现GET /api/v1/endpoints查询Endpoint列表
    - 实现GET /api/v1/apis/{apiId}/endpoints获取指定API的所有Endpoint
    - 添加OpenAPI注解
    - _需求: 1.2, 7.6_

  - [x] 7.4 实现RelationshipController
    - 实现POST /api/v1/relationships创建调用关系
    - 实现GET /api/v1/relationships/{id}获取调用关系详情
    - 实现PUT /api/v1/relationships/{id}更新调用关系
    - 实现DELETE /api/v1/relationships/{id}删除调用关系
    - 实现GET /api/v1/relationships查询调用关系列表
    - 添加OpenAPI注解
    - _需求: 2.3, 3.5, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_

  - [x] 7.5 实现TopologyController
    - 实现GET /api/v1/topology获取完整拓扑图数据
    - 实现GET /api/v1/topology/filter获取筛选后的拓扑图数据（支持标签筛选）
    - 添加OpenAPI注解
    - _需求: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 6.5_

  - [x] 7.6 实现HealthCheckController
    - 实现POST /api/v1/health-check/batch批量健康检查
    - 实现POST /api/v1/health-check/system/{systemId}按系统健康检查
    - 实现GET /api/v1/health-check/results/{batchId}获取健康检查结果
    - 添加OpenAPI注解
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [x] 7.7 实现OpenApiController
    - 配置Quarkus OpenAPI生成
    - 实现GET /api/v1/openapi.json端点
    - 确保所有Controller的OpenAPI注解完整
    - _需求: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 8. 异常处理和验证
  - [x] 8.1 实现全局异常处理器
    - 创建GlobalExceptionHandler实现ExceptionMapper
    - 处理常见异常类型（NotFoundException, ValidationException等）
    - 返回统一的ErrorResponse格式
    - _需求: 所有需求的错误处理_

  - [x] 8.2 实现自定义异常类
    - 创建ResourceNotFoundException
    - 创建DuplicateResourceException
    - 创建ValidationException
    - _需求: 所有需求的错误处理_

  - [x] 8.3 实现请求验证
    - 配置Bean Validation
    - 为所有Request DTO添加验证注解
    - 实现自定义邮箱列表验证器
    - _需求: 5.4, 5.6_

- [x] 9. AWS Lambda配置和部署
  - [x] 9.1 配置Lambda Handler
    - 配置Quarkus Lambda扩展
    - 设置Lambda handler类
    - 配置环境变量映射
    - _需求: 8.2_

  - [x] 9.2 配置数据库连接
    - 配置RDS连接参数
    - 配置VPC和安全组
    - 配置连接池大小
    - _需求: 8.3_

  - [x] 9.3 创建部署脚本
    - 创建Maven打包配置
    - 创建AWS SAM CloudFormation模板
    - 配置Lambda函数参数（内存、超时等）
    - 创建部署脚本（deploy.sh和deploy.bat）
    - 创建辅助脚本（package-lambda.sh, update-function.sh, local-test.sh, benchmark-performance.sh）
    - _需求: 8.2_

  - [x] 9.4 优化冷启动性能
    - 配置Quarkus原生镜像编译
    - 优化依赖和反射配置
    - 创建reflect-config.json和resource-config.json
    - 验证冷启动时间<3秒
    - _需求: 8.1, 8.4_

- [x] 10. 测试实现
  - [x] 10.1 编写Repository层单元测试
    - 使用Testcontainers启动PostgreSQL
    - 测试所有Repository的CRUD方法
    - 测试复杂查询逻辑
    - _需求: 所有数据访问相关需求_

  - [x] 10.2 编写Service层单元测试
    - 测试SystemService, ApiService, EndpointService业务逻辑
    - 测试业务逻辑和验证规则
    - 测试异常处理
    - _需求: 所有业务逻辑相关需求_

  - [x] 10.3 编写Controller层集成测试
    - 使用Quarkus Test框架
    - 测试SystemController, ApiController, EndpointController端点
    - 测试请求验证和错误响应
    - _需求: 所有API端点相关需求_

  - [x] 10.4 编写端到端测试
    - 测试完整的业务流程
    - 测试拓扑图数据生成
    - 测试健康检查功能
    - _需求: 2.1, 2.2, 2.3, 4.1, 4.2, 4.3_

- [x] 11. 文档完善
  - [x] 11.1 编写README文档
    - 项目介绍和架构说明
    - 本地开发环境搭建指南
    - API使用示例
    - 部署指南
    - _需求: 所有需求_

  - [x] 11.2 编写部署文档
    - 创建DEPLOYMENT_GUIDE.md
    - 详细的AWS Lambda部署步骤
    - VPC和RDS配置说明
    - 故障排查指南
    - _需求: 8.2, 8.3_

  - [x] 11.3 编写性能优化文档
    - 创建PERFORMANCE_OPTIMIZATION.md
    - 冷启动优化策略
    - 数据库连接优化
    - 监控和性能测试指南
    - _需求: 8.1, 8.4, 8.5_

  - [x] 11.4 编写数据库配置文档
    - 创建DATABASE_CONFIGURATION.md
    - RDS设置指南
    - 数据库迁移说明
    - _需求: 8.3_

  - [x] 11.5 编写脚本使用文档
    - 创建scripts/README.md
    - 说明所有部署和测试脚本的用法
    - _需求: 8.2_

- [x] 12. 补充测试覆盖





  - [x] 12.1 编写RelationshipService测试


    - 测试调用关系的CRUD业务逻辑
    - 测试caller和callee验证逻辑
    - 测试endpoint归属关系验证
    - _需求: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_



  - [x] 12.2 编写TopologyService测试




    - 测试拓扑图数据构建逻辑
    - 测试节点和边的生成
    - 测试标签筛选功能


    - _需求: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [x] 12.3 编写HealthCheckService测试









    - 测试单个endpoint健康检查


    - 测试批量健康检查
    - 测试按系统健康检查
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_


-

  - [x] 12.4 编写RelationshipController测试




    - 测试所有REST API端点


    - 测试请求验证和错误响应
    - _需求: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_

  - [x] 12.5 编写TopologyController测试





    - 测试拓扑图API端点
    - 测试筛选功能
    - _需求: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [x] 12.6 编写HealthCheckController测试





    - 测试批量健康检查端点
    - 测试按系统健康检查端点
    - 测试结果查询端点
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
-

- [x] 13. OpenAPI规格完善






  - [ ] 13.1 完善OpenAPI注解
    - 为所有Controller端点添加详细的@Operation注解
    - 添加@ApiResponse注解定义所有响应状态码
    - 为所有DTO添加@Schema注解和示例
    - 添加认证方案说明
    - _需求: 9.1, 9.2, 9.3, 9.4, 9.5_



  - [ ] 13.2 验证OpenAPI规格
    - 启动应用并导出openapi.json文件
    - 使用OpenAPI验证工具验证规格
    - 确保前端可以基于规格生成客户端代码
    - 验证所有端点和数据模型定义完整
    - _需求: 9.1, 9.2, 9.3, 9.4, 9.5_
