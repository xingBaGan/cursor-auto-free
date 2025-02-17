import logging
import json
import go_cursor_help
import patch_cursor_get_machine_id
from reset_machine import MachineIDResetter

def check_cursor_version():
    """检查cursor版本"""
    pkg_path, main_path = patch_cursor_get_machine_id.get_cursor_paths()
    with open(pkg_path, "r", encoding="utf-8") as f:
        version = json.load(f)["version"]
    return patch_cursor_get_machine_id.version_check(version, min_version="0.45.0")

def reset_machine_id(greater_than_0_45: bool) -> None:
    """
    Reset the machine ID for Cursor application
    
    Args:
        greater_than_0_45 (bool): Flag indicating if Cursor version is greater than 0.45.0
    """
    if greater_than_0_45:
        # For versions > 0.45.0, guide users to manually execute the patch script
        go_cursor_help.go_cursor_help()
    else:
        # For older versions, reset machine IDs directly
        MachineIDResetter().reset_machine_ids() 
        
def main():
    greater_than_0_45 = check_cursor_version()
    reset_machine_id(greater_than_0_45)

if __name__ == "__main__":
    main()

