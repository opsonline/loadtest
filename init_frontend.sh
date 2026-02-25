#!/bin/bash
# 压测系统前端开发环境配置脚本

echo "正在检查 Node.js 环境..."

# 检查 Node.js 版本
node --version
npm --version

# 检查是否安装 pnpm，如果没有则使用 npm
if ! command -v pnpm &> /dev/null
then
    echo "未检测到 pnpm，将使用 npm"
    PKG_MGR="npm"
else
    echo "检测到 pnpm"
    PKG_MGR="pnpm"
fi

# 进入前端目录
cd frontend

# 使用 Vite 创建 Vue 3 项目
echo "创建 Vue 3 + Vite 项目..."
echo "项目名称: loadtest-ui"
echo "框架: Vue"
echo "变体: JavaScript"

# 创建项目（使用 create-vite）
echo "正在初始化项目..."
# 注意：这会交互式询问项目配置
echo "请选择以下选项："
echo "- Project name: loadtest-ui"
echo "- Select a framework: Vue"
echo "- Select a variant: JavaScript"

$PKG_MGR create vite@latest loadtest-ui -- --template vue

# 进入项目目录
cd loadtest-ui

# 安装依赖
echo "安装基础依赖..."
$PKG_MGR install

# 安装 Element Plus
echo "安装 Element Plus..."
$PKG_MGR install element-plus

# 安装 Vue Router
echo "安装 Vue Router..."
$PKG_MGR install vue-router@4

# 安装 Pinia
echo "安装 Pinia..."
$PKG_MGR install pinia

# 安装 Axios
echo "安装 Axios..."
$PKG_MGR install axios

# 安装 ECharts
echo "安装 ECharts..."
$PKG_MGR install echarts

# 安装 dayjs
echo "安装 dayjs..."
$PKG_MGR install dayjs

echo "前端项目初始化完成！"
echo "请执行以下命令启动开发服务器："
echo "cd frontend/loadtest-ui && $PKG_MGR run dev"
