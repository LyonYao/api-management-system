# 需求文档

## 简介

API管理系统是一个用于管理公司微服务架构下各系统API的平台。该系统能够可视化展示API调用关系拓扑图，管理API元数据信息，执行健康检查，并提供便捷的API检索和维护通知功能。系统将帮助团队更好地理解和管理日益复杂的微服务API调用关系。

## 术语表

- **API管理系统 (API Management System)**: 本文档描述的核心系统，用于管理和监控公司所有API
- **API实体 (API Entity)**: 系统中注册的单个API记录，包含endpoint、认证方式等元数据
- **系统 (System)**: 一个独立的服务或应用程序，可以包含多个API
- **调用方 (Caller)**: 发起API调用的实体，可以是系统或具体的API
- **被调用方 (Callee)**: 接收API调用的实体，可以是系统或具体的API
- **调用关系 (Call Relationship)**: 调用方到被调用方的调用链路记录
- **拓扑图 (Topology Graph)**: 可视化展示系统间API调用关系的图形界面
- **健康检查 (Health Check)**: 对API endpoint的可用性验证请求
- **API标签 (API Tag)**: 用于分类API类型的标记
- **API规格链接 (API Spec Link)**: 指向API详细规格文档的URL

## 需求

### 需求 1

**用户故事:** 作为系统架构师，我希望能够注册和管理所有系统的API信息，以便集中维护API元数据

#### 验收标准

1. THE API管理系统 SHALL 允许用户创建API实体记录
2. WHEN 用户创建API实体时，THE API管理系统 SHALL 要求提供endpoint URL、HTTP方法、所属系统名称
3. THE API管理系统 SHALL 存储API实体的部门信息、联系人姓名和邮箱地址
4. THE API管理系统 SHALL 允许用户为API实体添加多个标签
5. THE API管理系统 SHALL 允许用户为API实体关联API规格文档链接
6. THE API管理系统 SHALL 为每个API实体存储认证方式类型包括API Key、OAuth2、Basic Auth、JWT或无认证

### 需求 2

**用户故事:** 作为开发人员，我希望能够查看API调用关系的拓扑图，以便理解系统间的依赖关系

#### 验收标准

1. THE API管理系统 SHALL 以拓扑图形式展示所有调用关系
2. THE 拓扑图 SHALL 将系统和API都显示为节点
3. THE 拓扑图 SHALL 显示调用方到被调用方之间的有向连接线
4. WHEN 用户点击拓扑图中的连接线时，THE API管理系统 SHALL 显示该调用关系的详细信息包括认证方式
5. THE 拓扑图 SHALL 支持缩放和拖拽操作以便查看复杂关系
6. THE 拓扑图 SHALL 以不同的视觉样式区分系统节点和API节点

### 需求 3

**用户故事:** 作为开发人员，我希望能够点击API查看详细信息，以便快速获取API的技术细节

#### 验收标准

1. WHEN 用户在拓扑图或列表中点击API实体时，THE API管理系统 SHALL 显示该API的详细信息面板
2. THE 详细信息面板 SHALL 显示endpoint URL、认证方式、所属系统、部门、联系人和邮箱
3. THE 详细信息面板 SHALL 显示该API的所有标签
4. WHEN API实体包含规格文档链接时，THE 详细信息面板 SHALL 提供可点击的链接跳转到API规格文档
5. THE 详细信息面板 SHALL 显示该API作为源或目标的所有调用关系

### 需求 4

**用户故事:** 作为运维人员，我希望能够按系统批量执行API健康检查，以便快速发现故障API

#### 验收标准

1. THE API管理系统 SHALL 允许用户按系统名称搜索该系统的所有API
2. WHEN 用户选择一个系统时，THE API管理系统 SHALL 显示该系统作为目标系统的所有API列表
3. THE API管理系统 SHALL 提供批量健康检查功能对选定系统的所有API执行健康检查
4. WHEN 执行健康检查时，THE API管理系统 SHALL 向每个API的endpoint发送HTTP请求
5. THE API管理系统 SHALL 显示每个API的健康检查结果包括响应状态码和响应时间
6. WHEN 健康检查失败时，THE API管理系统 SHALL 在结果中标记失败的API

### 需求 5

**用户故事:** 作为API负责人，我希望系统能够记录API的维护联系信息，以便在需要时快速联系相关人员

#### 验收标准

1. THE API管理系统 SHALL 为每个API实体存储部门名称
2. THE API管理系统 SHALL 为每个API实体存储联系人姓名
3. THE API管理系统 SHALL 为每个API实体存储多个联系人邮箱地址以逗号分隔
4. THE API管理系统 SHALL 验证每个邮箱地址格式的有效性
5. THE API管理系统 SHALL 允许用户更新API的联系信息
6. THE API管理系统 SHALL 支持至少10个联系人邮箱地址

### 需求 6

**用户故事:** 作为开发人员，我希望能够通过标签筛选API，以便快速找到特定类型的API

#### 验收标准

1. THE API管理系统 SHALL 允许用户为API实体创建和分配标签
2. THE API管理系统 SHALL 提供标签筛选功能显示包含指定标签的所有API
3. THE API管理系统 SHALL 支持多标签组合筛选
4. THE API管理系统 SHALL 显示系统中所有已使用的标签列表
5. WHEN 用户选择标签筛选时，THE 拓扑图 SHALL 高亮显示匹配的API调用关系

### 需求 7

**用户故事:** 作为系统管理员，我希望能够灵活记录调用关系，以便精确追踪不同粒度的API依赖

#### 验收标准

1. THE API管理系统 SHALL 允许用户创建调用关系时选择调用方类型为系统或API
2. THE API管理系统 SHALL 允许用户创建调用关系时选择被调用方类型为系统或API
3. WHEN 调用方类型为系统时，THE API管理系统 SHALL 存储系统标识符
4. WHEN 调用方类型为API时，THE API管理系统 SHALL 存储API实体引用
5. WHEN 被调用方类型为系统时，THE API管理系统 SHALL 存储系统标识符
6. WHEN 被调用方类型为API时，THE API管理系统 SHALL 存储API实体引用
7. THE API管理系统 SHALL 为每个调用关系存储该调用使用的认证方式
8. THE API管理系统 SHALL 支持系统到系统、系统到API、API到系统、API到API四种调用关系类型

### 需求 8

**用户故事:** 作为开发人员，我希望系统能够快速启动和响应，以便提高工作效率

#### 验收标准

1. THE API管理系统 SHALL 使用Java云原生框架实现快速启动
2. THE API管理系统 SHALL 在AWS Lambda环境中运行
3. THE API管理系统 SHALL 使用PostgreSQL数据库存储所有数据
4. THE API管理系统 SHALL 在Lambda冷启动时在3秒内完成初始化
5. THE API管理系统 SHALL 对单个API查询请求在500毫秒内返回响应

### 需求 9

**用户故事:** 作为前端开发人员，我希望后端提供标准的OpenAPI规格文档，以便我能够基于规格进行前端开发

#### 验收标准

1. THE API管理系统 SHALL 提供符合OpenAPI 3.0规范的API规格文档
2. THE OpenAPI规格文档 SHALL 包含所有REST API端点的定义
3. THE OpenAPI规格文档 SHALL 定义所有请求和响应的数据模型
4. THE OpenAPI规格文档 SHALL 包含每个端点的认证要求说明
5. THE API管理系统 SHALL 通过专用端点提供OpenAPI规格文档的JSON格式访问
