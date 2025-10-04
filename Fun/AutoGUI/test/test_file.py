import ctypes
import ctypes.wintypes
import time
import threading
import os
from ctypes import wintypes

# 导入 Windows API 所需的库
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# 定义常量
SPI_GETSCREENSAVERRUNNING = 114

class SystemStateDetector:
    def __init__(self):
        self.monitoring = False
        self.thread = None
        self.callback = None
        
    # 检测显示器是否关闭
    def is_display_off(self):
        try:
            # 方法1: 使用 GetDevicePowerState
            display_on = ctypes.c_bool(True)
            if kernel32.GetDevicePowerState(None, ctypes.byref(display_on)):
                return not display_on.value
            
            # 方法2: 备用方法 - 检查显示器状态
            # 通过检查屏幕是否响应来判断
            hdc = user32.GetDC(0)
            if hdc:
                user32.ReleaseDC(0, hdc)
        except Exception as e:
            print(f"检测显示器状态时出错: {e}")
        return False
    
    # 检测屏幕保护程序是否运行
    def is_screen_saver_running(self):
        try:
            running = ctypes.c_int(0)
            if user32.SystemParametersInfoW(SPI_GETSCREENSAVERRUNNING, 0, ctypes.byref(running), 0):
                return running.value != 0
        except Exception as e:
            print(f"检测屏保状态时出错: {e}")
        return False
    
    # 检测会话是否锁定 - 使用更可靠的方法
    def is_session_locked(self):
        try:
            # 方法1: 检查工作站是否锁定
            hwnd = user32.GetForegroundWindow()
            if hwnd == 0:
                return True
                
            # 方法2: 检查特定系统窗口
            # 锁定状态下，通常会有特定的窗口类
            desktop_window = user32.FindWindowW("Progman", None)
            if desktop_window == 0:
                return True
                
            # 方法3: 检查窗口可见性和标题
            if not user32.IsWindowVisible(hwnd):
                return True
                
            # 方法4: 检查是否有登录UI进程
            import subprocess
            result = subprocess.run(
                ['tasklist', '/fi', 'imagename eq logonui.exe', '/fo', 'csv', '/nh'],
                capture_output=True, text=True
            )
            if 'logonui.exe' in result.stdout:
                return True
                
        except Exception as e:
            print(f"检测会话状态时出错: {e}")
            
        return False
    
    # 单次检测所有状态
    def check_all_states(self):
        display_off = self.is_display_off()
        screen_saver = self.is_screen_saver_running()
        session_locked = self.is_session_locked()
        
        return {
            "display_off": display_off,
            "screen_saver": screen_saver,
            "session_locked": session_locked,
            "timestamp": time.time()
        }
    
    # 格式化状态输出
    def format_state(self, state):
        status_str = f"[{time.strftime('%H:%M:%S', time.localtime(state['timestamp']))}] "
        status_str += f"显示器: {'关闭' if state['display_off'] else '开启'}, "
        status_str += f"屏保: {'运行' if state['screen_saver'] else '未运行'}, "
        status_str += f"会话: {'锁定' if state['session_locked'] else '未锁定'}"
        return status_str
    
    # 开始持续监测
    def start_monitoring(self, interval=0.25, callback=None):
        if self.monitoring:
            print("已经在监控中")
            return
            
        self.monitoring = True
        self.callback = callback
        
        def monitor():
            last_state = None
            while self.monitoring:
                try:
                    current_state = self.check_all_states()
                    
                    # 只在状态变化时输出
                    if last_state is None or any(
                        current_state[key] != last_state[key] 
                        for key in ['display_off', 'screen_saver', 'session_locked']
                    ):
                        status_str = self.format_state(current_state)
                        print(status_str)
                        
                        if self.callback:
                            self.callback(current_state)
                    
                    last_state = current_state
                except Exception as e:
                    print(f"监控过程中出错: {e}")
                
                time.sleep(interval)
        
        self.thread = threading.Thread(target=monitor)
        self.thread.daemon = True
        self.thread.start()
        print(f"开始监控系统状态，间隔 {interval} 秒")
    
    # 停止监测
    def stop_monitoring(self):
        self.monitoring = False
        if self.thread:
            self.thread.join(timeout=1.0)
        print("停止监控系统状态")


class SystemStateTester:
    def __init__(self, detector):
        self.detector = detector
        self.original_states = None
    
    # 锁定工作站
    def lock_workstation(self):
        try:
            print("锁定工作站...")
            # 使用 LockWorkStation 函数
            if hasattr(user32, 'LockWorkStation'):
                user32.LockWorkStation()
            else:
                print("LockWorkStation 函数不可用")
        except Exception as e:
            print(f"锁定工作站时出错: {e}")
    
    # 关闭显示器
    def turn_off_display(self):
        try:
            print("关闭显示器...")
            # 使用 SendMessage 发送关闭显示器命令
            HWND_BROADCAST = 0xFFFF
            WM_SYSCOMMAND = 0x0112
            SC_MONITORPOWER = 0xF170
            MONITOR_OFF = 2
            
            user32.SendMessageW(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, MONITOR_OFF)
        except Exception as e:
            print(f"关闭显示器时出错: {e}")
    
    # 恢复显示器
    def turn_on_display(self):
        try:
            print("恢复显示器...")
            # 使用 SendMessage 发送打开显示器命令
            HWND_BROADCAST = 0xFFFF
            WM_SYSCOMMAND = 0x0112
            SC_MONITORPOWER = 0xF170
            MONITOR_ON = -1
            
            user32.SendMessageW(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, MONITOR_ON)
        except Exception as e:
            print(f"恢复显示器时出错: {e}")
    
    # 单次测试函数
    def single_test(self):
        print("=== 开始单次测试 ===")
        
        try:
            # 记录原始状态
            self.original_states = self.detector.check_all_states()
            print("初始状态:", self.detector.format_state(self.original_states))
            
            # 锁定电脑和息屏
            self.lock_workstation()
            time.sleep(2)  # 等待锁定完成
            self.turn_off_display()
            
            print("已锁定电脑并关闭显示器，等待 5 秒后开始后台测试...")
            time.sleep(0)
            
            # 开始后台测试
            print("开始后台测试...")
            test_results = []
            
            for i in range(600):  # 测试 10 次，每次间隔 0.5 秒
                state = self.detector.check_all_states()
                test_results.append(state)
                print(f"测试 {i+1}: {self.detector.format_state(state)}")
                time.sleep(0.25)
            
            # 恢复原始状态
            print("等待 10 秒后恢复原始状态...")
            time.sleep(10)
            
            # 恢复显示器
            self.turn_on_display()
            print("已恢复显示器")
            
            # 分析测试结果
            self.analyze_test_results(test_results)
            
            print("=== 单次测试完成 ===")
        except Exception as e:
            print(f"单次测试过程中出错: {e}")
    
    # 分析测试结果
    def analyze_test_results(self, test_results):
        print("\n=== 测试结果分析 ===")
        
        try:
            # 计算各种状态的检测次数
            display_off_count = sum(1 for state in test_results if state['display_off'])
            screen_saver_count = sum(1 for state in test_results if state['screen_saver'])
            session_locked_count = sum(1 for state in test_results if state['session_locked'])
            
            total_tests = len(test_results)
            
            print(f"显示器关闭检测: {display_off_count}/{total_tests} 次")
            print(f"屏保运行检测: {screen_saver_count}/{total_tests} 次")
            print(f"会话锁定检测: {session_locked_count}/{total_tests} 次")
            
            # 检测成功率
            success_rate = (display_off_count + session_locked_count) / (total_tests * 2)
            print(f"综合检测成功率: {success_rate:.1%}")
        except Exception as e:
            print(f"分析测试结果时出错: {e}")


# 使用示例
if __name__ == "__main__":
    detector = SystemStateDetector()
    tester = SystemStateTester(detector)
    
    # 示例回调函数
    def state_change_callback(state):
        # 这里可以添加自定义逻辑，如记录到文件、发送通知等
        pass
    
    try:
        # 先进行一次测试确保功能正常
        print("进行初始测试...")
        initial_state = detector.check_all_states()
        print("初始状态:", detector.format_state(initial_state))
        
        # 开始持续监控
        detector.start_monitoring(interval=0.25, callback=state_change_callback)
        
        # 等待一段时间后执行单次测试
        time.sleep(0)
        
        # 执行单次测试
        tester.single_test()
        
        # 继续监控一段时间
        time.sleep(60)
        
    except KeyboardInterrupt:
        print("\n用户中断程序")
    except Exception as e:
        print(f"程序运行出错: {e}")
    finally:
        # 停止监控
        detector.stop_monitoring()