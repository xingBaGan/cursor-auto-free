@echo off
chcp 65001 > nul
title Cursor Machine ID Reset Tool

:: 切换到脚本所在目录
cd /d "%~dp0"

:: 检查 Python 是否安装
python --version > nul 2>&1
if errorlevel 1 (
    echo [31m错误: 未检测到 Python，请确保已安装 Python 并添加到系统环境变量中[0m
    pause
    exit /b 1
)

:: 检查是否以管理员权限运行
net session >nul 2>&1
if errorlevel 1 (
    echo [33m警告: 建议以管理员权限运行此脚本[0m
    echo [33m请右键点击此脚本，选择"以管理员身份运行"[0m
    pause
    exit /b 1
)

echo [36m==================================================[0m
echo [36m            Cursor Machine ID Reset Tool           [0m
echo [36m==================================================[0m
echo.

:: 创建并激活虚拟环境
echo [36m正在创建虚拟环境...[0m
if not exist "venv" (
    python -m venv venv
)

:: 激活虚拟环境
call venv\Scripts\activate.bat

:: 安装依赖
echo [36m正在安装依赖...[0m
python -m pip install -r requirements.txt

:: 执行 Python 脚本
echo [36m正在执行重置脚本...[0m
python reset_machine_id.py

:: 退出虚拟环境
deactivate

echo.
echo [36m==================================================[0m
pause 