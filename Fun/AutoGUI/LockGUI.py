import sys
import subprocess
import ctypes
import platform

def lock_screen():
    """
    锁定计算机屏幕（跨平台）
    
    Returns:
        bool: 锁定操作是否成功
    """
    try:
        system_platform = platform.system().lower()
        
        if system_platform == "windows":
            return _lock_windows()
        elif system_platform == "darwin":  # macOS
            return _lock_macos()
        elif system_platform == "linux":
            return _lock_linux()
        else:
            print(f"不支持的操作系统: {system_platform}")
            return False
            
    except Exception as e:
        print(f"锁定屏幕时出错: {str(e)}")
        return False

def _lock_windows():
    """Windows 系统锁定"""
    try:
        # 方法1: 使用 Windows API (推荐)
        if ctypes.windll.user32.LockWorkStation():
            print("Windows 屏幕已锁定")
            return True
        else:
            print("Windows API 锁定失败")
            return False
    except Exception as e:
        print(f"Windows API 锁定失败: {e}")
        # 方法2: 使用命令行备用方案
        try:
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], 
                         check=True, capture_output=True)
            print("Windows 屏幕已锁定 (备用方法)")
            return True
        except subprocess.CalledProcessError:
            print("Windows 锁定备用方法也失败")
            return False

def _lock_macos():
    """macOS 系统锁定"""
    try:
        # 方法1: 使用 pmset
        subprocess.run(["pmset", "displaysleepnow"], check=True, capture_output=True)
        print("macOS 屏幕已锁定")
        return True
    except subprocess.CalledProcessError:
        try:
            # 方法2: 使用 osascript 备用方案
            applescript = 'tell application "System Events" to keystroke "q" using {control down, command down}'
            subprocess.run(["osascript", "-e", applescript], check=True, capture_output=True)
            print("macOS 屏幕已锁定 (备用方法)")
            return True
        except subprocess.CalledProcessError as e:
            print(f"macOS 锁定失败: {e}")
            return False

def _lock_linux():
    """Linux 系统锁定"""
    lock_commands = [
        ["gnome-screensaver-command", "--lock"],  # GNOME
        ["dm-tool", "lock"],                      # LightDM
        ["xdg-screensaver", "lock"],              # xdg-utils
        ["i3lock"],                               # i3 WM
        ["loginctl", "lock-session"],             # systemd logind
    ]
    
    for cmd in lock_commands:
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"Linux 屏幕已锁定 (使用: {' '.join(cmd)})")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    print("Linux: 未找到可用的锁屏工具")
    return False

def force_lock():
    """
    强制锁定屏幕，尝试多种方法
    """
    print("正在强制锁定屏幕...")
    
    # 尝试主方法
    if lock_screen():
        return True
    
    # 如果主方法失败，尝试其他跨平台方法
    print("主方法失败，尝试备用方法...")
    
    try:
        if platform.system().lower() == "windows":
            # Windows 备用：使用系统命令
            subprocess.run("tsdiscon", shell=True, check=True)
            return True
    except:
        pass
        
    return False

if __name__ == "__main__":
    # 测试代码
    print("测试屏幕锁定功能...")
    success = lock_screen()
    print(f"锁定操作结果: {'成功' if success else '失败'}")