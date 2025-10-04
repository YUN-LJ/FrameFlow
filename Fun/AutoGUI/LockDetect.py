import win32gui
import win32process
import win32con
import win32ts
import time

def is_locked_win32():
    """
    使用pywin32检测锁屏状态
    """
    try:
        # 方法1: 检查当前会话状态
        session_id = win32ts.WTSGetActiveConsoleSessionId()
        session_info = win32ts.WTSQuerySessionInformation(
            win32ts.WTS_CURRENT_SERVER_HANDLE, 
            session_id, 
            win32ts.WTSConnectState
        )
        
        # 如果会话状态是断开或锁定
        if session_info in [win32ts.WTSDisconnected, win32ts.WTSShadow]:
            return True
            
        # 方法2: 检查前台窗口
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            return True
            
        # 检查窗口是否可见
        if not win32gui.IsWindowVisible(hwnd):
            return True
            
        return False
        
    except Exception as e:
        print(f"检测错误: {e}")
        return True

def get_session_state_win32():
    """
    获取详细的会话状态
    """
    try:
        session_id = win32ts.WTSGetActiveConsoleSessionId()
        session_info = win32ts.WTSQuerySessionInformation(
            win32ts.WTS_CURRENT_SERVER_HANDLE, 
            session_id, 
            win32ts.WTSConnectState
        )
        
        states = {
            win32ts.WTSActive: "活动",
            win32ts.WTSConnected: "已连接", 
            win32ts.WTSConnectQuery: "连接查询",
            win32ts.WTSShadow: "影子模式",
            win32ts.WTSDisconnected: "已断开",
            win32ts.WTSIdle: "空闲",
            win32ts.WTSListen: "监听",
            win32ts.WTSReset: "重置",
            win32ts.WTSDown: "下线",
            win32ts.WTSInit: "初始化"
        }
        
        return states.get(session_info, "未知状态")
    except Exception as e:
        return f"错误: {e}"