import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"

# 登录信息
LOGIN_DATA = {
    "username": "admin",
    "password": "admin123"
}

# 从构建脚本的输出中获取API ID
API_ID = "e7dbf1fe-d1c7-41be-bd55-b97d80a25267"

def login():
    """登录获取token"""
    response = requests.post(LOGIN_URL, json=LOGIN_DATA)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"登录失败: {response.status_code} - {response.text}")
        return None

def run_tests(token, api_id):
    """运行测试"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/tests/api/{api_id}/run?environment=dev", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"运行测试失败: {response.status_code} - {response.text}")
        return None

def main():
    """主函数"""
    print("开始运行API管理系统的测试...")
    
    # 登录获取token
    token = login()
    if not token:
        return
    print("登录成功")
    
    # 运行测试
    result = run_tests(token, API_ID)
    if result:
        print("测试运行成功！")
        print(f"运行ID: {result['run_id']}")
        print(f"总测试数: {result['total_tests']}")
        print("测试已开始在后台执行，使用运行ID查询结果")
    else:
        print("测试运行失败")


if __name__ == "__main__":
    main()
