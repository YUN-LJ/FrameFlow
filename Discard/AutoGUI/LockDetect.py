import ctypes
import psutil
import time
# import os
from ctypes import wintypes


def __is_lock_screen_present():
    """检查是否存在锁屏进程"""
    lock_processes = ["LogonUI.exe"]
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] in lock_processes:
            return True
    return False


def __is_desktop_accessible():
    """检查是否能访问交互式桌面"""
    user32 = ctypes.WinDLL('user32', use_last_error=True)

    # 尝试获取前景窗口
    hwnd = user32.GetForegroundWindow()
    if hwnd == 0:
        return False

    # 尝试获取窗口标题
    length = user32.GetWindowTextLengthW(hwnd)
    if length == 0:
        return False

    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)

    # 锁屏界面通常标题为空或特定值
    return len(buf.value.strip()) > 0


def __is_screen_locked():
    """综合判断是否锁屏"""
    # 如果检测到锁屏进程，直接返回已锁屏
    if __is_lock_screen_present():
        return True

    # 检查桌面可访问性
    if not __is_desktop_accessible():
        return True

    # 最后尝试检查会话状态
    try:
        wtsapi32 = ctypes.WinDLL('wtsapi32', use_last_error=True)
        WTS_CURRENT_SESSION = -1
        WTS_SESSIONSTATE_LOCK = 0x00000001

        wtsapi32.WTSQuerySessionInformationW.argtypes = [
            wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD,
            ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(wintypes.DWORD)
        ]
        wtsapi32.WTSQuerySessionInformationW.restype = wintypes.BOOL
        wtsapi32.WTSFreeMemory.argtypes = [ctypes.c_void_p]

        buffer = ctypes.c_void_p()
        bytes_returned = wintypes.DWORD()

        if wtsapi32.WTSQuerySessionInformationW(
                None, WTS_CURRENT_SESSION, WTS_SESSIONSTATE_LOCK,
                ctypes.byref(buffer), ctypes.byref(bytes_returned)
        ):
            is_locked = ctypes.c_bool.from_address(buffer.value).value
            wtsapi32.WTSFreeMemory(buffer)
            return is_locked
    except Exception as e:
        print(e)

    return False

def check_locked():
    if __is_screen_locked():
        print("电脑已锁屏")
    else:
        print("电脑未锁屏")
        # 调试信息
        print(f"锁屏进程存在: {__is_lock_screen_present()}")
        print(f"桌面可访问: {__is_desktop_accessible()}")


if __name__=='__main__':
    # 测试代码
    print("请在5秒内锁屏...")
    # os.system("")
    time.sleep(5)

    if __is_screen_locked():
        print("电脑已锁屏")
    else:
        print("电脑未锁屏")
        # 调试信息
        print(f"锁屏进程存在: {__is_lock_screen_present()}")
        print(f"桌面可访问: {__is_desktop_accessible()}")