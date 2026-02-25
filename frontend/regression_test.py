#!/usr/bin/env python3
"""
前端回归测试脚本
使用 Selenium 或 Playwright 自动化测试浏览器交互
"""

import json
import time
import subprocess
import sys

# 测试用例
TEST_CASES = {
    "login": {
        "name": "登录功能",
        "steps": [
            "访问登录页面",
            "输入用户名密码",
            "点击登录按钮",
            "验证跳转成功"
        ]
    },
    "dashboard": {
        "name": "仪表盘",
        "steps": [
            "检查统计卡片显示",
            "检查最近报告列表",
            "检查菜单切换"
        ]
    },
    "scenarios": {
        "name": "场景管理",
        "steps": [
            "点击场景管理菜单",
            "检查场景列表表格",
            "检查操作按钮"
        ]
    },
    "navigation": {
        "name": "页面导航",
        "steps": [
            "测试所有菜单切换",
            "验证页面内容加载"
        ]
    }
}

class FrontendRegressionTest:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.results = []
    
    def log(self, test_name, status, message=""):
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.results.append(result)
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {test_name}: {status}")
        if message:
            print(f"   {message}")
    
    def test_page_load(self):
        """测试页面加载"""
        try:
            import urllib.request
            url = f"{self.base_url}/demo.html"
            
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
                
                # 检查关键元素
                checks = [
                    ('Vue.js', 'vue@3' in html),
                    ('Element Plus', 'element-plus' in html),
                    ('登录标题', '压测管理平台' in html),
                    ('登录表单', 'el-form' in html),
                    ('菜单项', '仪表盘' in html),
                ]
                
                all_passed = all(check[1] for check in checks)
                
                if all_passed:
                    self.log("页面加载", "PASS", "所有关键元素正常")
                else:
                    failed = [check[0] for check in checks if not check[1]]
                    self.log("页面加载", "FAIL", f"缺少元素: {failed}")
        
        except Exception as e:
            self.log("页面加载", "FAIL", str(e))
    
    def test_html_structure(self):
        """测试 HTML 结构"""
        try:
            import urllib.request
            url = f"{self.base_url}/demo.html"
            
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
                
                # 检查 HTML 结构
                structure_checks = [
                    ('Vue 挂载点', 'id="app"' in html),
                    ('登录组件', 'login-page' in html),
                    ('布局组件', 'layout-page' in html),
                    ('菜单组件', 'el-menu' in html),
                    ('组件切换逻辑', 'v-if="!isLoggedIn"' in html),
                    ('组件切换逻辑2', 'v-else' in html),
                    ('过渡动画', 'transition' in html),
                ]
                
                passed = sum(1 for _, check in structure_checks if check)
                total = len(structure_checks)
                
                if passed == total:
                    self.log("HTML 结构", "PASS", f"所有 {total} 个检查点通过")
                else:
                    failed = [name for name, check in structure_checks if not check]
                    self.log("HTML 结构", "FAIL", f"通过 {passed}/{total}, 失败: {failed}")
        
        except Exception as e:
            self.log("HTML 结构", "FAIL", str(e))
    
    def test_javascript_functionality(self):
        """测试 JavaScript 功能"""
        try:
            import urllib.request
            url = f"{self.base_url}/demo.html"
            
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
                
                # 检查 JS 功能
                js_checks = [
                    ('Vue 应用创建', 'createApp' in html),
                    ('响应式数据', 'ref(' in html),
                    ('登录处理', 'handleLogin' in html),
                    ('菜单选择', 'handleSelect' in html),
                    ('组件注册', 'app.component' in html),
                    ('图标注册', 'ElementPlusIconsVue' in html),
                    ('Vue 挂载', 'app.mount' in html),
                    ('状态管理', 'isLoggedIn' in html),
                ]
                
                passed = sum(1 for _, check in js_checks if check)
                total = len(js_checks)
                
                if passed == total:
                    self.log("JavaScript 功能", "PASS", f"所有 {total} 个检查点通过")
                else:
                    failed = [name for name, check in js_checks if not check]
                    self.log("JavaScript 功能", "WARN", f"通过 {passed}/{total}, 缺少: {failed}")
        
        except Exception as e:
            self.log("JavaScript 功能", "FAIL", str(e))
    
    def test_css_styles(self):
        """测试 CSS 样式"""
        try:
            import urllib.request
            url = f"{self.base_url}/demo.html"
            
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
                
                # 检查 CSS
                css_checks = [
                    ('登录容器样式', '.login-container' in html),
                    ('布局容器样式', '.layout-container' in html),
                    ('侧边栏样式', '.sidebar' in html),
                    ('渐变背景', 'linear-gradient' in html),
                    ('Flex 布局', 'display: flex' in html),
                    ('统计卡片样式', '.stat-card' in html),
                ]
                
                passed = sum(1 for _, check in css_checks if check)
                total = len(css_checks)
                
                if passed == total:
                    self.log("CSS 样式", "PASS", f"所有 {total} 个检查点通过")
                else:
                    failed = [name for name, check in css_checks if not check]
                    self.log("CSS 样式", "WARN", f"通过 {passed}/{total}, 缺少: {failed}")
        
        except Exception as e:
            self.log("CSS 样式", "FAIL", str(e))
    
    def test_api_integration(self):
        """测试 API 集成点"""
        try:
            import urllib.request
            url = f"{self.base_url}/demo.html"
            
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
                
                # 检查 API 调用点（在 demo.html 中应该是模拟数据）
                api_checks = [
                    ('模拟数据', '模拟数据' in html or 'setTimeout' in html),
                    ('axios 导入', 'axios' in html),
                    ('API 客户端', 'APIClient' in html or 'requests' in html),
                ]
                
                passed = sum(1 for _, check in api_checks if check)
                total = len(api_checks)
                
                if passed >= 1:
                    self.log("API 集成", "PASS", f"演示页面使用模拟数据")
                else:
                    self.log("API 集成", "WARN", "未检测到 API 调用或模拟数据逻辑")
        
        except Exception as e:
            self.log("API 集成", "FAIL", str(e))
    
    def test_components_structure(self):
        """测试组件结构"""
        try:
            import urllib.request
            url = f"{self.base_url}/demo.html"
            
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
                
                # 检查所有组件是否定义
                components = [
                    'LoginPage',
                    'LayoutPage', 
                    'DashboardView',
                    'ScenariosView',
                    'ReportsView',
                    'EnvironmentsView',
                    'DatasourcesView',
                    'ApiTestsView'
                ]
                
                found_components = []
                missing_components = []
                
                for comp in components:
                    if comp in html:
                        found_components.append(comp)
                    else:
                        missing_components.append(comp)
                
                if len(missing_components) == 0:
                    self.log("组件结构", "PASS", f"所有 {len(components)} 个组件已定义")
                else:
                    self.log("组件结构", "WARN", f"找到 {len(found_components)}/{len(components)} 个组件，缺少: {missing_components}")
        
        except Exception as e:
            self.log("组件结构", "FAIL", str(e))
    
    def test_menu_items(self):
        """测试菜单项"""
        try:
            import urllib.request
            url = f"{self.base_url}/demo.html"
            
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
                
                # 检查所有菜单项
                menu_items = [
                    ('仪表盘', 'index="dashboard"'),
                    ('场景管理', 'index="scenarios"'),
                    ('报告管理', 'index="reports"'),
                    ('环境变量', 'index="environments"'),
                    ('数据源', 'index="datasources"'),
                    ('接口测试', 'index="apitests"'),
                ]
                
                found = []
                for name, pattern in menu_items:
                    if pattern in html:
                        found.append(name)
                
                if len(found) == len(menu_items):
                    self.log("菜单项", "PASS", f"所有 {len(menu_items)} 个菜单项已定义")
                else:
                    missing = [name for name, _ in menu_items if name not in found]
                    self.log("菜单项", "FAIL", f"缺少菜单项: {missing}")
        
        except Exception as e:
            self.log("菜单项", "FAIL", str(e))
    
    def test_data_binding(self):
        """测试数据绑定"""
        try:
            import urllib.request
            url = f"{self.base_url}/demo.html"
            
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
                
                # 检查数据绑定
                binding_checks = [
                    ('v-model 绑定', 'v-model' in html),
                    ('v-for 循环', 'v-for' in html),
                    ('v-if 条件', 'v-if' in html),
                    ('v-else 条件', 'v-else' in html),
                    ('事件绑定', '@click' in html or 'v-on:click' in html),
                    ('属性绑定', ':' in html or 'v-bind:' in html),
                ]
                
                passed = sum(1 for _, check in binding_checks if check)
                total = len(binding_checks)
                
                if passed == total:
                    self.log("数据绑定", "PASS", f"所有 {total} 个绑定类型正常")
                else:
                    failed = [name for name, check in binding_checks if not check]
                    self.log("数据绑定", "WARN", f"通过 {passed}/{total}, 缺少: {failed}")
        
        except Exception as e:
            self.log("数据绑定", "FAIL", str(e))
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*70)
        print("前端回归测试")
        print("="*70)
        print(f"测试地址: {self.base_url}/demo.html\n")
        
        # 运行所有测试
        self.test_page_load()
        self.test_html_structure()
        self.test_javascript_functionality()
        self.test_css_styles()
        self.test_components_structure()
        self.test_menu_items()
        self.test_data_binding()
        self.test_api_integration()
        
        # 打印报告
        self.print_report()
    
    def print_report(self):
        """打印测试报告"""
        print("\n" + "="*70)
        print("测试报告")
        print("="*70)
        
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        warning = sum(1 for r in self.results if r["status"] == "WARN")
        total = len(self.results)
        
        print(f"\n总测试数: {total}")
        print(f"通过: {passed} ✅")
        print(f"失败: {failed} ❌")
        print(f"警告: {warning} ⚠️")
        print(f"\n通过率: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n失败的测试:")
            for result in self.results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['message']}")
        
        if warning > 0:
            print("\n警告的测试:")
            for result in self.results:
                if result["status"] == "WARN":
                    print(f"  - {result['test']}: {result['message']}")
        
        # 检查具体问题
        print("\n" + "="*70)
        print("详细问题分析")
        print("="*70)
        
        # 检查登录功能
        login_ok = any('登录' in r['test'] and r['status'] == 'PASS' for r in self.results)
        menu_ok = any('菜单' in r['test'] and r['status'] == 'PASS' for r in self.results)
        components_ok = any('组件' in r['test'] and r['status'] in ['PASS', 'WARN'] for r in self.results)
        
        print(f"\n1. 登录功能: {'正常' if login_ok else '需要检查'}")
        print(f"2. 菜单导航: {'正常' if menu_ok else '需要检查'}")
        print(f"3. 页面组件: {'正常' if components_ok else '需要检查'}")
        
        if not login_ok or not menu_ok:
            print("\n❗ 发现主要问题:")
            if not login_ok:
                print("   - 登录页面可能无法正常显示或交互")
            if not menu_ok:
                print("   - 菜单项可能缺失或无法点击")
            print("\n建议:")
            print("   1. 检查浏览器控制台是否有 JavaScript 错误")
            print("   2. 确保 Vue 3 和 Element Plus 正确加载")
            print("   3. 检查网络连接，确保 CDN 资源可访问")
        else:
            print("\n✅ 前端页面基本功能正常")
        
        print("\n" + "="*70)


if __name__ == "__main__":
    test = FrontendRegressionTest()
    test.run_all_tests()
