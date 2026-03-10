import requests
import json

BASE_URL = "http://localhost:8080/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"
SYSTEM_URL = f"{BASE_URL}/systems"
API_URL = f"{BASE_URL}/apis"
ENDPOINT_URL = f"{BASE_URL}/endpoints"
TEST_URL = f"{BASE_URL}/tests"

# 登录信息
LOGIN_DATA = {
    "username": "admin",
    "password": "admin123"
}

# 要创建的系统信息
SYSTEM_DATA = {
    "name": "Api 管理系统",
    "system_code": "APIMGMT",
    "description": "API管理系统本身的API"
}

# 要创建的API信息
API_DATA = {
    "name": "API Management API",
    "description": "API管理系统的内部API",
    "api_type": "S",
    "auth_type": "NONE",
    "contact_emails": ["admin@example.com"],
    "tags": ["api-management", "internal"],
    "dev_host": "http://localhost:8080",
    "uat_host": "http://localhost:8080",
    "prod_host": "http://localhost:8080"
}

# 要创建的Endpoint信息
ENDPOINTS_DATA = [
    # 认证相关
    {
        "path": "/auth/login",
        "http_method": "POST",
        "description": "用户登录",
        "status": "ONLINE"
    },
    {
        "path": "/auth/me",
        "http_method": "GET",
        "description": "获取当前用户信息",
        "status": "ONLINE"
    },
    {
        "path": "/auth/register",
        "http_method": "POST",
        "description": "注册新用户",
        "status": "ONLINE"
    },
    # 系统相关
    {
        "path": "/systems",
        "http_method": "POST",
        "description": "创建系统",
        "status": "ONLINE"
    },
    {
        "path": "/systems",
        "http_method": "GET",
        "description": "获取所有系统",
        "status": "ONLINE"
    },
    {
        "path": "/systems/{system_id}",
        "http_method": "GET",
        "description": "根据ID获取系统",
        "status": "ONLINE"
    },
    {
        "path": "/systems/{system_id}",
        "http_method": "PUT",
        "description": "更新系统",
        "status": "ONLINE"
    },
    {
        "path": "/systems/{system_id}",
        "http_method": "DELETE",
        "description": "删除系统",
        "status": "ONLINE"
    },
    # API相关
    {
        "path": "/apis",
        "http_method": "POST",
        "description": "创建API",
        "status": "ONLINE"
    },
    {
        "path": "/apis",
        "http_method": "GET",
        "description": "获取API列表",
        "status": "ONLINE"
    },
    {
        "path": "/apis/search",
        "http_method": "GET",
        "description": "搜索API",
        "status": "ONLINE"
    },
    {
        "path": "/apis/{api_id}",
        "http_method": "GET",
        "description": "根据ID获取API",
        "status": "ONLINE"
    },
    {
        "path": "/apis/{api_id}",
        "http_method": "PUT",
        "description": "更新API",
        "status": "ONLINE"
    },
    {
        "path": "/apis/{api_id}",
        "http_method": "DELETE",
        "description": "删除API",
        "status": "ONLINE"
    },
    # Endpoint相关
    {
        "path": "/endpoints",
        "http_method": "POST",
        "description": "创建端点",
        "status": "ONLINE"
    },
    {
        "path": "/endpoints",
        "http_method": "GET",
        "description": "获取所有端点",
        "status": "ONLINE"
    },
    {
        "path": "/endpoints/api/{api_id}",
        "http_method": "GET",
        "description": "根据API ID获取端点",
        "status": "ONLINE"
    },
    {
        "path": "/endpoints/{endpoint_id}",
        "http_method": "GET",
        "description": "根据ID获取端点",
        "status": "ONLINE"
    },
    {
        "path": "/endpoints/{endpoint_id}",
        "http_method": "PUT",
        "description": "更新端点",
        "status": "ONLINE"
    },
    {
        "path": "/endpoints/{endpoint_id}",
        "http_method": "DELETE",
        "description": "删除端点",
        "status": "ONLINE"
    },
    # 关系相关
    {
        "path": "/relationships",
        "http_method": "POST",
        "description": "创建调用关系",
        "status": "ONLINE"
    },
    {
        "path": "/relationships",
        "http_method": "GET",
        "description": "获取调用关系列表",
        "status": "ONLINE"
    },
    {
        "path": "/relationships/{relationship_id}",
        "http_method": "GET",
        "description": "根据ID获取调用关系",
        "status": "ONLINE"
    },
    {
        "path": "/relationships/{relationship_id}",
        "http_method": "PUT",
        "description": "更新调用关系",
        "status": "ONLINE"
    },
    {
        "path": "/relationships/{relationship_id}",
        "http_method": "DELETE",
        "description": "删除调用关系",
        "status": "ONLINE"
    },
    # 健康检查相关
    {
        "path": "/health/system/environment",
        "http_method": "POST",
        "description": "带环境参数的系统健康检查",
        "status": "ONLINE"
    },
    {
        "path": "/health/results/system/{system_id}",
        "http_method": "GET",
        "description": "获取系统的健康检查结果",
        "status": "ONLINE"
    },
    {
        "path": "/health/batches",
        "http_method": "GET",
        "description": "获取健康检查批次列表",
        "status": "ONLINE"
    },
    {
        "path": "/health/results/batch/{batch_id}",
        "http_method": "GET",
        "description": "获取批次的健康检查结果",
        "status": "ONLINE"
    },
    # 审计相关
    {
        "path": "/audit",
        "http_method": "GET",
        "description": "获取审计日志列表",
        "status": "ONLINE"
    },
    {
        "path": "/audit/{audit_id}",
        "http_method": "GET",
        "description": "获取单个审计日志",
        "status": "ONLINE"
    },
    # 测试相关
    {
        "path": "/tests",
        "http_method": "POST",
        "description": "创建测试用例",
        "status": "ONLINE"
    },
    {
        "path": "/tests/endpoint/{endpoint_id}",
        "http_method": "GET",
        "description": "获取指定Endpoint的所有测试用例",
        "status": "ONLINE"
    },
    {
        "path": "/tests/{test_id}",
        "http_method": "GET",
        "description": "获取测试用例详情",
        "status": "ONLINE"
    },
    {
        "path": "/tests/{test_id}",
        "http_method": "PUT",
        "description": "更新测试用例",
        "status": "ONLINE"
    },
    {
        "path": "/tests/{test_id}",
        "http_method": "DELETE",
        "description": "删除测试用例",
        "status": "ONLINE"
    },
    {
        "path": "/tests/api/{api_id}/run",
        "http_method": "POST",
        "description": "运行API的所有测试用例",
        "status": "ONLINE"
    },
    {
        "path": "/tests/results/system/{system_id}",
        "http_method": "GET",
        "description": "根据系统ID查询测试结果",
        "status": "ONLINE"
    },
    {
        "path": "/tests/results/api/{api_id}",
        "http_method": "GET",
        "description": "根据API ID查询测试结果",
        "status": "ONLINE"
    },
    {
        "path": "/tests/trends",
        "http_method": "POST",
        "description": "获取测试趋势分析",
        "status": "ONLINE"
    },
    # 根路径
    {
        "path": "/",
        "http_method": "GET",
        "description": "根路径",
        "status": "ONLINE"
    },
    # 健康检查
    {
        "path": "/health",
        "http_method": "GET",
        "description": "服务健康检查",
        "status": "ONLINE"
    }
]

# 测试用例模板
def create_test_case_data(endpoint):
    """根据Endpoint创建测试用例数据"""
    test_case = {
        "name": f"{endpoint['http_method']} {endpoint['path']} Test",
        "description": f"测试{endpoint['description']}",
        "environment": "dev",
        "headers": {
            "Content-Type": "application/json"
        },
        "request_body": None,
        "expected_response": {
            "status": "success"
        },
        "validation_rules": {
            "status_code": 200
        }
    }
    
    # 根据HTTP方法设置不同的测试数据
    if endpoint['http_method'] == "POST":
        if "/auth/login" in endpoint['path']:
            test_case['request_body'] = {
                "username": "admin",
                "password": "admin123"
            }
            test_case['validation_rules']['status_code'] = 200
        elif "/auth/register" in endpoint['path']:
            test_case['request_body'] = {
                "username": "testuser",
                "password": "test123",
                "full_name": "Test User",
                "email": "test@example.com"
            }
            test_case['validation_rules']['status_code'] = 200
        elif "/systems" in endpoint['path']:
            test_case['request_body'] = {
                "name": "Test System",
                "system_code": "TESTSYS",
                "description": "Test System"
            }
            test_case['validation_rules']['status_code'] = 201
        elif "/apis" in endpoint['path']:
            test_case['request_body'] = {
                "system_id": "",  # 稍后会替换
                "name": "Test API",
                "description": "Test API",
                "api_type": "S",
                "auth_type": "NONE",
                "contact_emails": ["test@example.com"],
                "tags": ["test"]
            }
            test_case['validation_rules']['status_code'] = 201
        elif "/endpoints" in endpoint['path']:
            test_case['request_body'] = {
                "api_id": "",  # 稍后会替换
                "path": "/test",
                "http_method": "GET",
                "description": "Test Endpoint",
                "status": "ONLINE"
            }
            test_case['validation_rules']['status_code'] = 201
        elif "/relationships" in endpoint['path']:
            test_case['request_body'] = {
                "caller_type": "API",
                "caller_id": "",  # 稍后会替换
                "callee_type": "API",
                "callee_id": "",  # 稍后会替换
                "description": "Test Relationship"
            }
            test_case['validation_rules']['status_code'] = 201
        elif "/health/system/environment" in endpoint['path']:
            test_case['request_body'] = {
                "system_id": "",  # 稍后会替换
                "environment": "dev"
            }
            test_case['validation_rules']['status_code'] = 200
        elif "/tests" in endpoint['path']:
            test_case['request_body'] = {
                "endpoint_id": "",  # 稍后会替换
                "name": "Test Test Case",
                "description": "Test Test Case",
                "environment": "dev"
            }
            test_case['validation_rules']['status_code'] = 200
        elif "/tests/trends" in endpoint['path']:
            test_case['request_body'] = {
                "system_id": "",  # 稍后会替换
                "interval": "day"
            }
            test_case['validation_rules']['status_code'] = 200
    elif endpoint['http_method'] == "PUT":
        test_case['request_body'] = {
            "name": "Updated Test"
        }
        test_case['validation_rules']['status_code'] = 200
    
    return test_case

def login():
    """登录获取token"""
    response = requests.post(LOGIN_URL, json=LOGIN_DATA)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"登录失败: {response.status_code} - {response.text}")
        return None

def create_system(token):
    """创建系统"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(SYSTEM_URL, json=SYSTEM_DATA, headers=headers)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"创建系统失败: {response.status_code} - {response.text}")
        return None

def create_api(token, system_id):
    """创建API"""
    api_data = API_DATA.copy()
    api_data["system_id"] = system_id
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(API_URL, json=api_data, headers=headers)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"创建API失败: {response.status_code} - {response.text}")
        return None

def create_endpoint(token, api_id, endpoint_data):
    """创建Endpoint"""
    endpoint_data["api_id"] = api_id
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(ENDPOINT_URL, json=endpoint_data, headers=headers)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"创建Endpoint失败: {response.status_code} - {response.text}")
        return None

def create_test_case(token, endpoint_id, test_case_data):
    """创建测试用例"""
    test_case_data["endpoint_id"] = endpoint_id
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(TEST_URL, json=test_case_data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"创建测试用例失败: {response.status_code} - {response.text}")
        return None

def main():
    """主函数"""
    print("开始构建API管理系统...")
    
    # 登录获取token
    token = login()
    if not token:
        return
    print("登录成功")
    
    # 创建系统
    system = create_system(token)
    if not system:
        return
    print(f"创建系统成功，ID: {system['id']}, 名称: {system['name']}")
    
    # 创建API
    api = create_api(token, system['id'])
    if not api:
        return
    print(f"创建API成功，ID: {api['id']}, 名称: {api['name']}")
    
    # 创建Endpoint和测试用例
    for i, endpoint_data in enumerate(ENDPOINTS_DATA):
        endpoint = create_endpoint(token, api['id'], endpoint_data)
        if not endpoint:
            continue
        print(f"创建Endpoint成功，ID: {endpoint['id']}, 路径: {endpoint['http_method']} {endpoint['path']}")
        
        # 创建对应的测试用例
        test_case_data = create_test_case_data(endpoint_data)
        # 替换系统ID和API ID
        if test_case_data['request_body']:
            if 'system_id' in test_case_data['request_body']:
                test_case_data['request_body']['system_id'] = system['id']
            if 'api_id' in test_case_data['request_body']:
                test_case_data['request_body']['api_id'] = api['id']
            if 'endpoint_id' in test_case_data['request_body']:
                test_case_data['request_body']['endpoint_id'] = endpoint['id']
        
        test_case = create_test_case(token, endpoint['id'], test_case_data)
        if test_case:
            print(f"创建测试用例成功，ID: {test_case['id']}, 名称: {test_case['name']}")
    
    print("API管理系统构建完成！")


if __name__ == "__main__":
    main()
