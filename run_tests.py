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
API_ID = "ec8932df-0526-46de-bc01-ca996d1491c5"

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
    response = requests.post(f"{BASE_URL}/tests/api/{api_id}/run", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"运行测试失败: {response.status_code} - {response.text}")
        return None

def main():
    """主函数"""
    print("开始运行测试...")
    
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
        print(f"总测试数: {result['total_count']}")
        print(f"通过数: {result['pass_count']}")
        print(f"失败数: {result['fail_count']}")
        print(f"错误数: {result['error_count']}")
        
        # 打印测试结果详情
        print("\n测试结果详情:")
        for test_result in result['results']:
            print(f"测试ID: {test_result['test_id']}")
            print(f"状态: {test_result['status']}")
            print(f"响应码: {test_result['response_code']}")
            print(f"响应时间: {test_result['response_time_ms']}ms")
            if test_result['error_message']:
                print(f"错误信息: {test_result['error_message']}")
            print("---")
    else:
        print("测试运行失败")


if __name__ == "__main__":
    main()
