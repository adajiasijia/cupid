#!/bin/bash
# 启动后端服务脚本

echo "正在启动理财助手后端服务..."

# 检查 Python 是否安装
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null
then
    echo "错误：未找到 Python，请先安装 Python 3.x"
    exit 1
fi

# 确定 Python 命令
if command -v python3 &> /dev/null
then
    PYTHON_CMD=python3
else
    PYTHON_CMD=python
fi

# 进入 backend 目录
cd "$(dirname "$0")"

# 检查依赖是否安装
if [ ! -d "venv" ]; then
    echo "正在创建虚拟环境..."
    $PYTHON_CMD -m venv venv
fi

# 激活虚拟环境
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# 安装依赖
echo "正在安装依赖..."
pip install -r requirements.txt

# 启动服务
echo "启动服务..."
echo "服务地址：http://localhost:5000"
echo "API 文档：http://localhost:5000/api"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

$PYTHON_CMD app.py
