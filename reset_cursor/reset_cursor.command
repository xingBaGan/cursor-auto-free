#!/bin/bash

# 设置终端颜色代码
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 切换到脚本所在目录
cd "$(dirname "$0")"

echo -e "${CYAN}=================================================="
echo -e "            Cursor Machine ID Reset Tool           "
echo -e "==================================================${NC}"
echo

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未检测到 Python，请确保已安装 Python 3${NC}"
    echo -e "${RED}建议使用 Homebrew 安装: brew install python3${NC}"
    read -p "按回车键退出..."
    exit 1
fi

# 检查是否以管理员权限运行
if [ "$(id -u)" != "0" ]; then
    echo -e "${YELLOW}警告: 建议以管理员权限运行此脚本${NC}"
    echo -e "${YELLOW}请在终端中使用 sudo 运行此脚本${NC}"
    read -p "按回车键退出..."
    exit 1
fi

# 创建并激活虚拟环境
echo -e "${CYAN}正在创建虚拟环境...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo -e "${CYAN}正在安装依赖...${NC}"
python -m pip install -r requirements.txt

# 执行 Python 脚本
echo -e "${CYAN}正在执行重置脚本...${NC}"
python reset_machine_id.py

# 退出虚拟环境
deactivate

echo
echo -e "${CYAN}=================================================${NC}"
read -p "按回车键退出..." 