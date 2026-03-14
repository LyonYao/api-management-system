import requests
import json

def login():
    """Login to the API and return the authentication token."""
    url = "https://api.ilyon.cn/v1/api/blog/auth/login"
    payload = {
        "username": "admin",
        "password": "GHSG6RsC9FF2OIop"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data.get("token")
    else:
        raise Exception(f"Login failed: {response.status_code} {response.text}")

def publish_blog(title, content, categories, tags=None, published=True):
    """Publish a blog post to the API."""
    # Get authentication token
    token = login()
    
    # Default tags if not provided
    if tags is None:
        tags = ["ai", "skill", "trae"]
    
    # Prepare the blog post data
    url = "https://api.ilyon.cn/v1/api/blog/posts"
    payload = {
        "title": title,
        "content": content,
        "published": published,
        "categories": categories,
        "tags": tags
    }
    
    # Set headers with authentication token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Send the request
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Publishing failed: {response.status_code} {response.text}")

if __name__ == "__main__":
    # Publish API management system blog post
    try:
        result = publish_blog(
            title="使用AI开发API管理系统：基于FastAPI和PostgreSQL的微服务管理平台",
            content="<h1>使用AI开发API管理系统：基于FastAPI和PostgreSQL的微服务管理平台</h1>\n\n<p>作为一名Python AI开发者，我最近使用Trae solo模式开发了一个API管理系统，用于管理公司微服务架构下的各系统API。这个系统不仅能够可视化展示API调用关系拓扑图，还能管理API元数据信息，执行健康检查，并提供便捷的API检索和维护通知功能。</p>\n\n<h2>项目背景</h2>\n\n<p>在现代微服务架构中，API数量激增，管理和监控这些API变得越来越复杂。传统的文档管理方式已经无法满足需求，我们需要一个集中化的平台来管理所有API信息，追踪API之间的调用关系，并确保API的健康状态。</p>\n\n<h2>技术栈选择</h2>\n\n<p>基于项目需求，我选择了以下技术栈：</p>\n\n<ul>\n  <li><strong>运行时</strong>: Python 11+</li>\n  <li><strong>框架</strong>: FastAPI（高性能Python Web框架，自动生成OpenAPI文档）</li>\n  <li><strong>数据库</strong>: PostgreSQL</li>\n  <li><strong>API文档</strong>: OpenAPI 3.0（由FastAPI自动生成）</li>\n  <li><strong>数据访问</strong>: SQLAlchemy ORM</li>\n  <li><strong>异步支持</strong>: asyncio 和 httpx</li>\n  <li><strong>认证</strong>: JWT (JSON Web Token)</li>\n  <li><strong>数据库迁移</strong>: Alembic</li>\n  <li><strong>密码加密</strong>: bcrypt</li>\n</ul>\n\n<h2>系统架构</h2>\n\n<p>系统采用分层架构设计，包括：</p>\n\n<ul>\n  <li><strong>API Gateway (REST)</strong>: 处理HTTP请求</li>\n  <li><strong>Router Layer</strong>: 路由层，负责分发请求到不同的服务</li>\n  <li><strong>Service Layer</strong>: 业务逻辑层，实现核心功能</li>\n  <li><strong>Repository Layer</strong>: 数据访问层，处理数据库操作</li>\n  <li><strong>PostgreSQL Database</strong>: 数据存储</li>\n</ul>\n\n<h2>核心功能</h2>\n\n<h3>1. API管理</h3>\n\n<p>系统允许用户注册和管理所有系统的API信息，包括endpoint URL、HTTP方法、所属系统名称、部门信息、联系人姓名和邮箱地址等。用户还可以为API实体添加多个标签，关联API规格文档链接，并存储不同环境的Host地址。</p>\n\n<h3>2. 拓扑图可视化</h3>\n\n<p>系统以拓扑图形式展示所有API调用关系，将系统和API都显示为节点，通过有向连接线表示调用关系。用户可以点击连接线查看详细信息，支持缩放和拖拽操作以便查看复杂关系。</p>\n\n<h3>3. 健康检查</h3>\n\n<p>系统支持按系统批量执行API健康检查，向每个API的endpoint发送HTTP请求，显示响应状态码和响应时间。当健康检查失败时，系统会标记失败的API，并支持按环境（开发、测试、生产）执行健康检查。</p>\n\n<h3>4. 标签筛选</h3>\n\n<p>用户可以为API实体创建和分配标签，通过标签筛选功能快速找到特定类型的API。系统支持多标签组合筛选，并在拓扑图中高亮显示匹配的API调用关系。</p>\n\n<h3>5. 测试管理</h3>\n\n<p>系统允许用户为Endpoint添加测试用例，包括请求头、请求体信息，并支持通过JSON定义的表达式来判断测试是否通过。用户可以批量执行API的所有测试用例，并查询测试执行结果，分析API的历史表现。</p>\n\n<h3>6. 认证和审计</h3>\n\n<p>系统实现基于JWT的认证机制，保护API访问安全。同时，系统记录所有操作的审计日志，包括操作类型、资源类型、操作人、操作时间等信息，支持按条件筛选审计日志。</p>\n\n<h2>数据模型</h2>\n\n<p>系统设计了详细的数据模型，包括：</p>\n\n<ul>\n  <li><strong>System</strong>: 系统信息</li>\n  <li><strong>Api</strong>: API实体信息</li>\n  <li><strong>Endpoint</strong>: API端点信息</li>\n  <li><strong>Tag</strong>: API标签</li>\n  <li><strong>Relationship</strong>: API调用关系</li>\n  <li><strong>HealthCheckResult</strong>: 健康检查结果</li>\n  <li><strong>User</strong>: 系统用户</li>\n  <li><strong>AuditLog</strong>: 审计日志</li>\n  <li><strong>EndpointTest</strong>: 测试用例</li>\n  <li><strong>TestBatch</strong>: 测试批次</li>\n  <li><strong>TestResult</strong>: 测试执行结果</li>\n</ul>\n\n<h2>开发体验</h2>\n\n<p>使用Trae solo模式开发这个项目非常高效，AI辅助工具帮助我快速生成代码结构和实现细节。FastAPI框架的自动文档生成功能大大减少了文档编写工作，而SQLAlchemy ORM则简化了数据库操作。</p>\n\n<p>系统的异步处理能力确保了健康检查和测试执行的高效性，即使在处理大量API时也能保持良好的响应速度。</p>\n\n<h2>部署方案</h2>\n\n<p>系统支持多种部署方式：</p>\n\n<ul>\n  <li>使用FastAPI内置的开发服务器进行开发</li>\n  <li>使用生产级服务器（如Gunicorn + Uvicorn）进行部署</li>\n  <li>支持容器化部署（如Docker）</li>\n  <li>支持数据库迁移管理（使用Alembic）</li>\n</ul>\n\n<h2>总结</h2>\n\n<p>这个API管理系统为公司的微服务架构提供了一个集中化的管理平台，帮助团队更好地理解和管理日益复杂的微服务API调用关系。通过AI辅助开发，我能够快速实现系统的核心功能，并确保系统的可靠性和性能。</p>\n\n<p>未来，我计划进一步增强系统的功能，包括添加更多的监控指标、实现API版本管理、提供更丰富的分析报告等，以满足不断增长的API管理需求。</p>",
            categories=["AI开发", "Python", "FastAPI", "微服务"],
            tags=["api管理", "ai开发", "python", "fastapi", "postgresql", "trae"]
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")
