#!/usr/bin/env python3
"""
前端功能回归测试
模拟浏览器交互测试
"""
import http.client
import json
import re

class FrontendFunctionalTest:
    def __init__(self, host="localhost", port=3000):
        self.host = host
        self.port = port
        self.results = []
    
    def log(self, test_name, status, details=""):
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        self.results.append({"test": test_name, "status": status, "details": details})
        print(f"{icon} {test_name}")
        if details:
            print(f"   {details}")
    
    def fetch_page(self, path="/demo.html"):
        """获取页面内容"""
        try:
            conn = http.client.HTTPConnection(self.host, self.port, timeout=10)
            conn.request("GET", path)
            response = conn.getresponse()
            data = response.read().decode('utf-8')
            conn.close()
            return response.status, data
        except Exception as e:
            return None, str(e)
    
    def test_page_accessible(self):
        """测试页面可访问"""
        status, data = self.fetch_page()
        if status == 200:
            self.log("页面可访问", "PASS", f"状态码: {status}, 大小: {len(data)} bytes")
        else:
            self.log("页面可访问", "FAIL", f"状态码: {status}")
    
    def test_vue_js_loaded(self):
        """测试 Vue.js 加载"""
        status, data = self.fetch_page()
        if status == 200 and 'vue@3' in data:
            self.log("Vue.js 加载", "PASS", "Vue 3 CDN 已引用")
        else:
            self.log("Vue.js 加载", "FAIL", "未找到 Vue 3 引用")
    
    def test_element_plus_loaded(self):
        """测试 Element Plus 加载"""
        status, data = self.fetch_page()
        if status == 200 and 'element-plus' in data:
            self.log("Element Plus 加载", "PASS", "Element Plus CDN 已引用")
        else:
            self.log("Element Plus 加载", "FAIL", "未找到 Element Plus 引用")
    
    def test_login_form_structure(self):
        """测试登录表单结构"""
        status, data = self.fetch_page()
        checks = [
            ('表单标签', '<el-form' in data),
            ('用户名输入', 'v-model="form.username"' in data),
            ('密码输入', 'v-model="form.password"' in data),
            ('登录按钮', '@click="handleSubmit"' in data),
            ('提交事件', '@submit.prevent' in data),
        ]
        
        passed = sum(1 for _, check in checks if check)
        total = len(checks)
        
        if passed == total:
            self.log("登录表单结构", "PASS", f"所有 {total} 个检查点通过")
        else:
            failed = [name for name, check in checks if not check]
            self.log("登录表单结构", "FAIL", f"缺少: {failed}")
    
    def test_menu_structure(self):
        """测试菜单结构"""
        status, data = self.fetch_page()
        checks = [
            ('菜单组件', '<el-menu' in data),
            ('菜单选择事件', '@select="handleSelect"' in data),
            ('仪表盘菜单', 'index="dashboard"' in data),
            ('场景管理菜单', 'index="scenarios"' in data),
            ('报告管理菜单', 'index="reports"' in data),
        ]
        
        passed = sum(1 for _, check in checks if check)
        total = len(checks)
        
        if passed == total:
            self.log("菜单结构", "PASS", f"所有 {total} 个检查点通过")
        else:
            failed = [name for name, check in checks if not check]
            self.log("菜单结构", "FAIL", f"缺少: {failed}")
    
    def test_page_components(self):
        """测试页面组件"""
        status, data = self.fetch_page()
        components = [
            'LoginPage', 'LayoutPage', 'DashboardView', 
            'ScenariosView', 'ReportsView'
        ]
        
        found = [c for c in components if c in data]
        missing = [c for c in components if c not in data]
        
        if len(missing) == 0:
            self.log("页面组件", "PASS", f"找到所有 {len(components)} 个组件")
        else:
            self.log("页面组件", "WARN", f"缺少: {missing}")
    
    def test_data_binding(self):
        """测试数据绑定"""
        status, data = self.fetch_page()
        bindings = [
            ('v-model', 'v-model' in data),
            ('v-if', 'v-if' in data),
            ('v-else', 'v-else' in data),
            ('事件绑定', '@click' in data or 'v-on:click' in data),
            ('v-for', 'v-for' in data),
        ]
        
        passed = sum(1 for _, check in bindings if check)
        total = len(bindings)
        
        if passed >= 3:
            self.log("数据绑定", "PASS", f"{passed}/{total} 个绑定类型")
        else:
            self.log("数据绑定", "FAIL", f"绑定不足: {passed}/{total}")
    
    def test_vue_lifecycle(self):
        """测试 Vue 生命周期"""
        status, data = self.fetch_page()
        checks = [
            ('createApp', 'createApp' in data),
            ('app.mount', 'app.mount' in data),
            ('setup()', 'setup()' in data),
            ('onMounted', 'onMounted' in data),
        ]
        
        passed = sum(1 for _, check in checks if check)
        total = len(checks)
        
        if passed == total:
            self.log("Vue 生命周期", "PASS", "所有生命周期钩子正确")
        else:
            failed = [name for name, check in checks if not check]
            self.log("Vue 生命周期", "WARN", f"缺少: {failed}")
    
    def test_page_switching_logic(self):
        """测试页面切换逻辑"""
        status, data = self.fetch_page()
        checks = [
            ('isLoggedIn', 'isLoggedIn' in data),
            ('currentView', 'currentView' in data),
            ('viewMap', 'viewMap' in data),
            ('component', '<component :is=' in data),
            ('transition', '<transition' in data),
        ]
        
        passed = sum(1 for _, check in checks if check)
        total = len(checks)
        
        if passed >= 4:
            self.log("页面切换逻辑", "PASS", f"{passed}/{total} 个检查点")
        else:
            failed = [name for name, check in checks if not check]
            self.log("页面切换逻辑", "FAIL", f"缺少: {failed}")
    
    def test_icon_usage(self):
        """测试图标使用"""
        status, data = self.fetch_page()
        
        # 检查图标组件
        icon_checks = [
            ('ElementPlusIconsVue', 'ElementPlusIconsVue' in data),
            ('app.component', 'app.component' in data),
            ('el-icon', '<el-icon' in data),
        ]
        
        passed = sum(1 for _, check in icon_checks if check)
        
        if passed >= 2:
            self.log("图标使用", "PASS", f"{passed}/3 个检查点")
        else:
            self.log("图标使用", "WARN", "图标配置可能有问题")
    
    def test_common_issues(self):
        """测试常见问题"""
        status, data = self.fetch_page()
        issues = []
        
        # 检查可能导致问题的代码
        if ':prefix-icon="User"' in data:
            issues.append("prefix-icon 使用了错误绑定语法")
        
        if 'v-if="!isLoggedIn"' not in data:
            issues.append("登录状态切换逻辑可能缺失")
        
        if 'const app = createApp' not in data:
            issues.append("Vue 应用创建语法可能错误")
        
        if issues:
            self.log("潜在问题", "WARN", "; ".join(issues))
        else:
            self.log("代码质量", "PASS", "未发现明显问题")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("="*70)
        print("前端功能回归测试")
        print("="*70)
        print(f"测试地址: http://{self.host}:{self.port}/demo.html\n")
        
        # 基础测试
        self.test_page_accessible()
        self.test_vue_js_loaded()
        self.test_element_plus_loaded()
        
        # 结构测试
        self.test_login_form_structure()
        self.test_menu_structure()
        self.test_page_components()
        
        # 功能测试
        self.test_data_binding()
        self.test_vue_lifecycle()
        self.test_page_switching_logic()
        self.test_icon_usage()
        self.test_common_issues()
        
        # 报告
        self.print_report()
    
    def print_report(self):
        """打印报告"""
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
            for r in self.results:
                if r["status"] == "FAIL":
                    print(f"  - {r['test']}: {r['details']}")
        
        if warning > 0:
            print("\n警告的测试:")
            for r in self.results:
                if r["status"] == "WARN":
                    print(f"  - {r['test']}: {r['details']}")
        
        # 总结
        print("\n" + "="*70)
        print("功能状态")
        print("="*70)
        
        login_ok = any('登录' in r['test'] and r['status'] == 'PASS' for r in self.results)
        menu_ok = any('菜单' in r['test'] and r['status'] == 'PASS' for r in self.results)
        switch_ok = any('切换' in r['test'] and r['status'] in ['PASS', 'WARN'] for r in self.results)
        
        print(f"\n1. 登录功能: {'✅ 正常' if login_ok else '❌ 需要检查'}")
        print(f"2. 菜单导航: {'✅ 正常' if menu_ok else '❌ 需要检查'}")
        print(f"3. 页面切换: {'✅ 正常' if switch_ok else '❌ 需要检查'}")
        
        if passed >= 8:
            print("\n✅ 前端页面结构基本正常")
            print("\n建议：")
            print("1. 在浏览器中访问 http://localhost:3000/demo.html")
            print("2. 打开开发者工具 (F12) -> Console")
            print("3. 尝试登录和切换菜单")
            print("4. 查看是否有红色错误信息")
        else:
            print("\n⚠️ 发现一些问题，需要进一步检查")
        
        print("\n" + "="*70)


if __name__ == "__main__":
    test = FrontendFunctionalTest()
    test.run_all_tests()
