import os
import platform
import subprocess
from colorama import init, Fore, Style

# 初始化colorama
init()

def build_exe():
    """构建exe文件"""
    print(f"{Fore.CYAN}开始构建ResetCursor.exe...{Style.RESET_ALL}")
    
    # 创建输出目录
    output_dir = "dist/windows"
    os.makedirs(output_dir, exist_ok=True)
    
    # PyInstaller命令
    cmd = [
        "pyinstaller",
        "ResetCursor.spec",
        "--distpath", output_dir,
        "--workpath", "build",
        "--noconfirm"
    ]
    
    try:
        # 执行构建
        subprocess.run(cmd, check=True)
        print(f"{Fore.GREEN}构建成功！{Style.RESET_ALL}")
        print(f"输出目录: {os.path.abspath(output_dir)}")
        
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}构建失败: {e}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}发生错误: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    if platform.system().lower() != "windows":
        print(f"{Fore.RED}此脚本仅支持在Windows系统上运行{Style.RESET_ALL}")
        exit(1)
    
    build_exe() 