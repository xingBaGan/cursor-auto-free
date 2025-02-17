import logging
import json
import go_cursor_help
import patch_cursor_get_machine_id
from reset_machine import MachineIDResetter
from colorama import init, Fore, Style

# 初始化colorama
init()

def check_cursor_version():
    """检查cursor版本"""
    try:
        pkg_path, main_path = patch_cursor_get_machine_id.get_cursor_paths()
        with open(pkg_path, "r", encoding="utf-8") as f:
            version = json.load(f)["version"]
        return patch_cursor_get_machine_id.version_check(version, min_version="0.45.0")
    except Exception as e:
        print(f"{Fore.RED}检查Cursor版本时出错: {e}{Style.RESET_ALL}")
        return False

def reset_machine_id(greater_than_0_45: bool) -> None:
    """
    Reset the machine ID for Cursor application
    """
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Cursor Machine ID Reset Tool{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}\n{Style.RESET_ALL}")
    
    if greater_than_0_45:
        print(f"{Fore.YELLOW}检测到Cursor版本 > 0.45.0, 正在执行补丁脚本...{Style.RESET_ALL}")
        go_cursor_help.go_cursor_help()
    else:
        print(f"{Fore.CYAN}正在重置Machine ID...{Style.RESET_ALL}")
        MachineIDResetter().reset_machine_ids()
        
def main():
    try:
        greater_than_0_45 = check_cursor_version()
        reset_machine_id(greater_than_0_45)
    except Exception as e:
        print(f"{Fore.RED}程序执行出错: {e}{Style.RESET_ALL}")
    finally:
        print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()

