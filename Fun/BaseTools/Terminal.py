"""有关终端的操作文件"""
import sys
import ctypes, time, subprocess
import win32con, win32gui
from Fun.BaseTools import Get, Tools


def admin_run(command: str):
    """调用管理员权限执行cmd命令"""
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, command, None, 1)


def hide_python_terminal():
    """隐藏python控制台"""
    # 获取python控制台句柄
    python_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if python_hwnd != 0:
        ctypes.windll.user32.ShowWindow(python_hwnd, win32con.SW_HIDE)


def show_python_terminal():
    """显示python控制台"""
    # 获取python控制台句柄
    python_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if python_hwnd != 0:
        ctypes.windll.user32.ShowWindow(python_hwnd, win32con.SW_SHOW)


class CreateTerminal:
    """创建一个终端"""

    def __init__(self, hide=True):
        """
        :param hide:是否隐藏,默认隐藏,输出在主程序中
        """
        self.hide = hide
        # 创建标志：仅保留这两个（确保生成窗口句柄）
        if hide:
            self.creationflags = (subprocess.CREATE_NEW_PROCESS_GROUP  # 方便后续终止进程
                                  | subprocess.CREATE_NO_WINDOW)  # 创建无窗口的cmd
        else:
            self.creationflags = (subprocess.CREATE_NEW_PROCESS_GROUP  # 方便后续终止进程
                                  | subprocess.CREATE_NEW_CONSOLE)  # 强制创建窗口（获取句柄的前提）
        self.create()

    def __create_hidden_cmd(self):
        """创建隐藏的cmd进程,返回subprocess.Popen,和窗口句柄"""
        self.process = subprocess.Popen(
            ["cmd.exe", "/k", "chcp 65001 >nul"],
            creationflags=self.creationflags,
            shell=False,
            stdin=subprocess.PIPE,
            # stdout=subprocess.PIPE,  # 可选：重定向标准输出（如需捕获输出）
            # stderr=subprocess.PIPE,  # 可选：重定向标准错误（如需捕获错误）
            text=False,  # 保持字节流模式（write 需传 bytes，避免编码问题）
            bufsize=0,  # 禁用缓冲（立即发送命令，避免卡顿）
        )

    def __create_hwnd(self):
        """获取窗口句柄"""
        for i in range(10):
            self.hwnd = Get.find_hwnd(self.process.pid)
            if not self.hwnd:
                time.sleep(0)
            else:
                break
        if not self.hide:
            win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)

    def input(self, text: str):
        """输入指令"""
        self.process.stdin.write((text + '\n').encode(encoding='utf-8'))
        self.process.stdin.flush()

    def create(self):
        """创建子cmd进程"""
        # 创建cmd进程
        self.__create_hidden_cmd()
        # 获取句柄,如果有的话
        self.__create_hwnd()

    def kill_process(self):
        """终止进程"""
        Tools.kill_program(self.process.pid)
