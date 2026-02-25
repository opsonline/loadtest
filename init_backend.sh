#!/bin/bash
# 压测系统后端开发环境配置脚本

echo "正在配置 Python 环境..."

# 检查 Python 版本
python3 --version

# 创建虚拟环境
echo "创建虚拟环境..."
cd backend
python3 -m venv venv

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级 pip
echo "升级 pip..."
pip install --upgrade pip

# 安装 Django
echo "安装 Django..."
pip install django==4.2.9

# 初始化 Django 项目
echo "初始化 Django 项目..."
django-admin startproject config .

echo "Django 项目初始化完成！"
echo "请执行以下命令启动开发服务器："
echo "cd backend && source venv/bin/activate && python manage.py runserver"
