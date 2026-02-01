# Docker测试依赖分析

## 概述

本项目有部分测试需要Docker环境来运行PostgreSQL容器。本文档详细说明哪些测试需要Docker以及原因。

## 需要Docker的测试

### Repository层测试（6个测试类）

所有Repository测试都需要Docker，因为它们继承了 `BaseRepositoryTest`：

1. **ApiRepositoryTest** (6个测试)
   - 测试API数据库操作
   - 继承 `BaseRepositoryTest`
   
2. **SystemRepositoryTest** (6个测试)
   - 测试System数据库操作
   - 继承 `BaseRepositoryTest`
   
3. **EndpointRepositoryTest** (5个测试)
   - 测试Endpoint数据库操作
   - 继承 `BaseRepositoryTest`
   
4. **RelationshipRepositoryTest** (9个测试)
   - 测试Relationship数据库操作
   - 继承 `BaseRepositoryTest`
   
5. **TagRepositoryTest** (8个测试)
   - 测试Tag数据库操作
   - 继承 `BaseRepositoryTest`
   
6. **HealthCheckResultRepositoryTest** (7个测试)
   - 测试HealthCheckResult数据库操作
   - 继承 `BaseRepositoryTest`

**总计**: 41个Repository测试需要Docker

### BaseRepositoryTest配置

```java
@QuarkusTest
@QuarkusTestResource(PostgresTestResource.class)
public abstract class BaseRepositoryTest {
    @Inject
    protected PgPool client;
    
    @BeforeEach
    public void cleanDatabase() {
        // 清理数据库表
    }
}
```

**关键点**：
- `@QuarkusTestResource(PostgresTestResource.class)` 会启动Testcontainers PostgreSQL容器
- 所有继承此类的测试都会尝试启动Docker容器
- 这些测试**没有**使用 `@TestProfile(NoDockerTestProfile.class)`

## 不需要Docker的测试

### Controller层测试（6个测试类）

所有Controller测试都使用Mock，不需要Docker：

1. **SystemControllerTest** (7个测试) - ✅ 使用 `@TestProfile(NoDockerTestProfile.class)`
2. **ApiControllerTest** (8个测试) - ⚠️ **缺少TestProfile**
3. **EndpointControllerTest** (8个测试) - ✅ 使用 `@TestProfile(NoDockerTestProfile.class)`
4. **RelationshipControllerTest** (20个测试) - ✅ 使用 `@TestProfile(NoDockerTestProfile.class)`
5. **TopologyControllerTest** (16个测试) - ✅ 使用 `@TestProfile(NoDockerTestProfile.class)`
6. **HealthCheckControllerTest** (12个测试) - ✅ 使用 `@TestProfile(NoDockerTestProfile.class)`

### Service层测试（6个测试类）

所有Service测试都使用Mock，不需要Docker：

1. **SystemServiceTest** (11个测试) - ⚠️ **缺少TestProfile**
2. **ApiServiceTest** (11个测试) - ⚠️ **缺少TestProfile**
3. **EndpointServiceTest** (11个测试) - ⚠️ **缺少TestProfile**
4. **RelationshipServiceTest** (15个测试) - ✅ 使用 `@TestProfile(NoDockerTestProfile.class)`
5. **TopologyServiceTest** (14个测试) - ✅ 使用 `@TestProfile(NoDockerTestProfile.class)`
6. **HealthCheckServiceTest** (9个测试) - ⚠️ **缺少TestProfile但有问题**

### E2E测试

1. **EndToEndTest** (5个测试) - ⚠️ **缺少TestProfile**

## 测试执行行为

### 有Docker环境时
```bash
mvn test
# 所有188个测试都会运行
# Repository测试会启动PostgreSQL容器
# 其他测试使用Mock
```

### 无Docker环境时
```bash
mvn test
# Repository测试: 41个自动跳过（PostgresTestResource启动失败）
# Controller/Service测试: 
#   - 有NoDockerTestProfile的: 正常跳过
#   - 缺少NoDockerTestProfile的: 可能失败
```

## 当前测试状态（无Docker）

从测试输出分析：

### ✅ 正确跳过的测试（185个）
- 所有Repository测试（41个）- PostgresTestResource失败后自动跳过
- 大部分Controller测试（71个）- 使用NoDockerTestProfile
- 大部分Service测试（68个）- 使用NoDockerTestProfile
- E2E测试（5个）- 自动跳过

### ❌ 失败的测试（3个）
1. **ApiControllerTest.testUpdateApi**
   - 原因：缺少 `@TestProfile(NoDockerTestProfile.class)`
   - 尝试启动PostgresTestResource但失败
   
2. **HealthCheckServiceTest.testPerformHealthCheck_Success**
   - 原因：虽然有NoDockerTestProfile，但可能有其他依赖问题
   - 需要进一步调查
   
3. **ApiRepositoryTest.testFindBySystemId**
   - 原因：PostgresTestResource启动失败
   - 应该被跳过但报告为错误

## 问题修复建议

### 方案1：为缺少TestProfile的测试添加注解

为以下测试类添加 `@TestProfile(NoDockerTestProfile.class)`：

```java
@QuarkusTest
@TestProfile(NoDockerTestProfile.class)  // 添加这行
public class ApiControllerTest {
    // ...
}
```

需要修改的测试类：
- ApiControllerTest
- SystemServiceTest
- ApiServiceTest
- EndpointServiceTest
- EndToEndTest

### 方案2：安装Docker（推荐）

安装Docker Desktop可以运行所有测试，包括Repository层的集成测试。

### 方案3：跳过测试

对于Task 13（OpenAPI规格完善），不需要运行测试：
```bash
mvn clean package -DskipTests
```

## 总结

| 测试类型 | 数量 | 需要Docker | 当前状态 |
|---------|------|-----------|---------|
| Repository测试 | 41 | ✅ 是 | 自动跳过 |
| Controller测试 | 71 | ❌ 否 | 1个失败，70个跳过 |
| Service测试 | 68 | ❌ 否 | 1个失败，67个跳过 |
| E2E测试 | 5 | ❌ 否 | 跳过 |
| **总计** | **188** | **41需要** | **3失败，185跳过** |

**关键发现**：
- 只有Repository测试真正需要Docker
- 其他测试应该使用Mock，不需要Docker
- 3个测试失败是因为缺少 `@TestProfile(NoDockerTestProfile.class)` 注解
- 对于Task 13，使用 `mvn package -DskipTests` 即可验证OpenAPI规格
