import os
import platform
import subprocess
import shutil
from colorama import init, Fore, Style

# 初始化colorama，设置转换所有输出
init(strip=False)

def build_exe():
    """构建Windows exe文件"""
    print(f"{Fore.CYAN}Starting to build ResetCursor.exe...{Style.RESET_ALL}")
    
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
        print(f"{Fore.GREEN}Build successful!{Style.RESET_ALL}")
        print(f"Output directory: {os.path.abspath(output_dir)}")
        
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Build failed: {e}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error occurred: {e}{Style.RESET_ALL}")

def build_unix():
    """构建Linux/Mac版本"""
    system = platform.system().lower()
    if system == "linux":
        platform_name = "linux"
        script_name = "reset_cursor.sh"
    else:
        platform_name = "mac"
        script_name = "reset_cursor.command"

    print(f"{Fore.CYAN}Starting to build {platform_name.capitalize()} version...{Style.RESET_ALL}")
    
    # 创建输出目录
    output_dir = f"dist/{platform_name}"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 复制必要文件到输出目录
        files_to_copy = [
            script_name,
            "reset_machine_id.py",
            "requirements.txt"
        ]
        
        for file in files_to_copy:
            if os.path.exists(file):
                shutil.copy2(file, output_dir)
                # 设置可执行权限
                if file.endswith(('.sh', '.command')):
                    os.chmod(os.path.join(output_dir, file), 0o755)
        
        print(f"{Fore.GREEN}Build successful!{Style.RESET_ALL}")
        print(f"Output directory: {os.path.abspath(output_dir)}")
        
    except Exception as e:
        print(f"{Fore.RED}Error occurred: {e}{Style.RESET_ALL}")

def main():
    system = platform.system().lower()
    
    if system == "windows":
        build_exe()
    elif system in ["linux", "darwin"]:  # darwin 是 Mac OS 的系统名
        build_unix()
    else:
        print(f"{Fore.RED}Unsupported operating system: {system}{Style.RESET_ALL}")
        exit(1)

if __name__ == "__main__":
    main() 