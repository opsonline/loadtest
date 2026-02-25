#!/usr/bin/env python
"""
测试运行脚本
用于运行项目的单元测试
"""
import os
import sys
import subprocess
from pathlib import Path


def run_tests():
    """运行所有测试"""
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    failures = test_runner.run_tests(["apps"])
    
    sys.exit(bool(failures))


def run_specific_tests(test_labels):
    """运行特定的测试"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    failures = test_runner.run_tests(test_labels)
    
    sys.exit(bool(failures))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 运行特定测试
        run_specific_tests(sys.argv[1:])
    else:
        # 运行所有测试
        run_tests()