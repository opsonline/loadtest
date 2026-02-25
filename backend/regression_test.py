#!/usr/bin/env python
"""
回归测试脚本 - 手动检查 API 端点
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

class RegressionTest:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.test_results = []
    
    def log(self, test_name, status, message=""):
        result = {
            'test': test_name,
            'status': status,
            'message': message
        }
        self.test_results.append(result)
        icon = "✅" if status == "PASS" else "❌"
        print(f"{icon} {test_name}: {status}")
        if message:
            print(f"   {message}")
    
    def test_user_registration(self):
        """测试用户注册"""
        try:
            response = requests.post(f"{BASE_URL}/users/register/", json={
                "username": "regression_test_user",
                "email": "regression@test.com",
                "password": "testpass123"
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    self.token = data["data"]["tokens"]["access_token"]
                    self.log("用户注册", "PASS", "注册成功并获取 token")
                else:
                    self.log("用户注册", "FAIL", f"返回码错误: {data.get('code')}")
            else:
                self.log("用户注册", "FAIL", f"状态码: {response.status_code}")
        except Exception as e:
            self.log("用户注册", "FAIL", str(e))
    
    def test_user_login(self):
        """测试用户登录"""
        try:
            response = requests.post(f"{BASE_URL}/users/login/", json={
                "username": "admin",
                "password": "admin123"
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    self.token = data["data"]["tokens"]["access_token"]
                    self.log("用户登录", "PASS", "登录成功")
                else:
                    self.log("用户登录", "FAIL", f"返回码错误: {data.get('code')}")
            else:
                self.log("用户登录", "FAIL", f"状态码: {response.status_code}")
        except Exception as e:
            self.log("用户登录", "FAIL", str(e))
    
    def test_unauthorized_access(self):
        """测试未授权访问"""
        try:
            response = requests.get(f"{BASE_URL}/scenarios/", timeout=5)
            
            if response.status_code == 401:
                self.log("未授权访问检查", "PASS", "正确返回 401")
            else:
                self.log("未授权访问检查", "FAIL", f"期望 401，实际 {response.status_code}")
        except Exception as e:
            self.log("未授权访问检查", "FAIL", str(e))
    
    def test_get_scenarios(self):
        """测试获取场景列表"""
        if not self.token:
            self.log("获取场景列表", "SKIP", "未获取到 token")
            return
        
        try:
            response = requests.get(
                f"{BASE_URL}/scenarios/",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    count = len(data.get("data", {}).get("results", []))
                    self.log("获取场景列表", "PASS", f"获取到 {count} 个场景")
                else:
                    self.log("获取场景列表", "FAIL", f"返回码错误: {data.get('code')}")
            else:
                self.log("获取场景列表", "FAIL", f"状态码: {response.status_code}")
        except Exception as e:
            self.log("获取场景列表", "FAIL", str(e))
    
    def test_get_environments(self):
        """测试获取环境列表"""
        if not self.token:
            self.log("获取环境列表", "SKIP", "未获取到 token")
            return
        
        try:
            response = requests.get(
                f"{BASE_URL}/environments/",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            
            if response.status_code == 200:
                self.log("获取环境列表", "PASS")
            else:
                self.log("获取环境列表", "FAIL", f"状态码: {response.status_code}")
        except Exception as e:
            self.log("获取环境列表", "FAIL", str(e))
    
    def test_get_datasources(self):
        """测试获取数据源列表"""
        if not self.token:
            self.log("获取数据源列表", "SKIP", "未获取到 token")
            return
        
        try:
            response = requests.get(
                f"{BASE_URL}/datasources/",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            
            if response.status_code == 200:
                self.log("获取数据源列表", "PASS")
            else:
                self.log("获取数据源列表", "FAIL", f"状态码: {response.status_code}")
        except Exception as e:
            self.log("获取数据源列表", "FAIL", str(e))
    
    def test_get_reports(self):
        """测试获取报告列表"""
        if not self.token:
            self.log("获取报告列表", "SKIP", "未获取到 token")
            return
        
        try:
            response = requests.get(
                f"{BASE_URL}/reports/",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            
            if response.status_code == 200:
                self.log("获取报告列表", "PASS")
            else:
                self.log("获取报告列表", "FAIL", f"状态码: {response.status_code}")
        except Exception as e:
            self.log("获取报告列表", "FAIL", str(e))
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print("压测管理平台 - 回归测试")
        print("="*60 + "\n")
        
        # 测试顺序很重要
        self.test_user_login()
        self.test_unauthorized_access()
        self.test_get_scenarios()
        self.test_get_environments()
        self.test_get_datasources()
        self.test_get_reports()
        
        # 打印报告
        self.print_report()
    
    def print_report(self):
        """打印测试报告"""
        print("\n" + "="*60)
        print("测试报告")
        print("="*60)
        
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        skipped = sum(1 for r in self.test_results if r["status"] == "SKIP")
        total = len(self.test_results)
        
        print(f"\n总测试数: {total}")
        print(f"通过: {passed} ✅")
        print(f"失败: {failed} ❌")
        print(f"跳过: {skipped} ⏭️")
        print(f"\n通过率: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    test = RegressionTest()
    test.run_all_tests()
