import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
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
    "name": "Test System 1",
    "system_code": "TESTSYS1",
    "description": "测试系统"
}

# 要创建的API信息
API_DATA = {
    "name": "Test API",
    "description": "测试API",
    "api_type": "S",
    "auth_type": "NONE",
    "contact_emails": ["test@example.com"],
    "tags": ["test", "api"],
    "dev_host": "http://localhost:8080",
    "uat_host": "http://localhost:8080",
    "prod_host": "http://localhost:8080"
}

# 要创建的Endpoint信息
ENDPOINTS_DATA = [
    {
        "path": "/test",
        "http_method": "GET",
        "description": "获取测试数据",
        "status": "ONLINE"
    },
    {
        "path": "/test",
        "http_method": "POST",
        "description": "创建测试数据",
        "status": "ONLINE"
    },
    {
        "path": "/test/{id}",
        "http_method": "PUT",
        "description": "更新测试数据",
        "status": "ONLINE"
    },
    {
        "path": "/test/{id}",
        "http_method": "DELETE",
        "description": "删除测试数据",
        "status": "ONLINE"
    }
]

# 要创建的测试用例信息
TEST_CASES_DATA = [
    {
        "name": "GET Test Case",
        "description": "测试GET接口",
        "environment": "dev",
        "headers": {},
        "request_body": None,
        "expected_response": {
            "status": "success",
            "data": []
        },
        "validation_rules": {
            "status_code": 200
        }
    },
    {
        "name": "POST Test Case",
        "description": "测试POST接口",
        "environment": "dev",
        "headers": {
            "Content-Type": "application/json"
        },
        "request_body": {
            "name": "Test",
            "value": 123
        },
        "expected_response": {
            "status": "success",
            "data": {}
        },
        "validation_rules": {
            "status_code": 201
        }
    },
    {
        "name": "PUT Test Case",
        "description": "测试PUT接口",
        "environment": "dev",
        "headers": {
            "Content-Type": "application/json"
        },
        "request_body": {
            "name": "Updated Test",
            "value": 456
        },
        "expected_response": {
            "status": "success",
            "data": {}
        },
        "validation_rules": {
            "status_code": 200
        }
    },
    {
        "name": "DELETE Test Case",
        "description": "测试DELETE接口",
        "environment": "dev",
        "headers": {},
        "request_body": None,
        "expected_response": {
            "status": "success"
        },
        "validation_rules": {
            "status_code": 200
        }
    }
]

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
        return response.json()["id"]
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
        return response.json()["id"]
    else:
        print(f"创建API失败: {response.status_code} - {response.text}")
        return None

def create_endpoint(token, api_id, endpoint_data):
    """创建Endpoint"""
    endpoint_data["api_id"] = api_id
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(ENDPOINT_URL, json=endpoint_data, headers=headers)
    if response.status_code == 201:
        return response.json()["id"]
    else:
        print(f"创建Endpoint失败: {response.status_code} - {response.text}")
        return None

def create_test_case(token, endpoint_id, test_case_data):
    """创建测试用例"""
    test_case_data["endpoint_id"] = endpoint_id
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(TEST_URL, json=test_case_data, headers=headers)
    if response.status_code == 200:
        return response.json()["id"]
    else:
        print(f"创建测试用例失败: {response.status_code} - {response.text}")
        return None

def main():
    """主函数"""
    print("开始构建API系统...")
    
    # 登录获取token
    token = login()
    if not token:
        return
    print("登录成功")
    
    # 创建系统
    system_id = create_system(token)
    if not system_id:
        return
    print(f"创建系统成功，ID: {system_id}")
    
    # 创建API
    api_id = create_api(token, system_id)
    if not api_id:
        return
    print(f"创建API成功，ID: {api_id}")
    
    # 创建Endpoint和测试用例
    for i, endpoint_data in enumerate(ENDPOINTS_DATA):
        endpoint_id = create_endpoint(token, api_id, endpoint_data)
        if not endpoint_id:
            continue
        print(f"创建Endpoint成功，ID: {endpoint_id}")
        
        # 创建对应的测试用例
        test_case_data = TEST_CASES_DATA[i]
        test_id = create_test_case(token, endpoint_id, test_case_data)
        if test_id:
            print(f"创建测试用例成功，ID: {test_id}")
    
    print("API系统构建完成！")


if __name__ == "__main__":
    main()
