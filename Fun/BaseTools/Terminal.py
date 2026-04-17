"""有关终端的操作文件"""
import re
import os
import sys
import time
import ctypes
import win32con
import threading
from io import StringIO
from winpty import PtyProcess
from queue import Queue, Empty
from Fun.BaseTools import Time
from ansi2html import Ansi2HTMLConverter


def admin_run(command: str):
    """调用管理员权限执行cmd命令"""
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, command, None, 1)


def hide_python_terminal():
    """隐藏python控制台"""
    python_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if python_hwnd != 0:
        ctypes.windll.user32.ShowWindow(python_hwnd, win32con.SW_HIDE)


def show_python_terminal():
    """显示python控制台"""
    python_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if python_hwnd != 0:
        ctypes.windll.user32.ShowWindow(python_hwnd, win32con.SW_SHOW)


def is_python_terminal_visible() -> int:
    """
    检查Python控制台是否可见

    :return: 1如果控制台可见,-1不可见,0没有窗口句柄未知状态
    """
    python_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if python_hwnd == 0:
        return 0

    # 获取窗口显示状态
    visibility = ctypes.windll.user32.IsWindowVisible(python_hwnd)
    if visibility:
        return 1
    else:
        return -1


class CreateTerminal:
    """
    终端进程管理器（基于 ConPTY）
    负责创建和管理 Python/CMD 终端进程，处理输入输出
    """

    TERMINAL_TYPE_PYTHON = "python"
    TERMINAL_TYPE_CMD = "cmd"

    def __init__(self, terminal_type="python", python_path=None):
        """
        初始化终端进程管理器

        :param terminal_type: 终端类型，"python" 或 "cmd"
        :param python_path: Python 解释器路径（仅在 terminal_type="python" 时有效）
        """
        self.type = terminal_type.lower()
        self.python_path = python_path or sys.executable
        self.char_queue = Queue()
        self.read_thread = threading.Thread(target=self.__read_output, daemon=True)
        self.status_thread = threading.Thread(target=self.__monitor_status, daemon=True)
        self.process: PtyProcess = None
        self.is_running = False
        self.wait_command = False  # True表示等待命令输入,False表示正在执行命令
        self.last_output_time = time.time()  # 最后一次输出的时间戳
        self.output_buffer = ""  # 输出缓冲区，用于状态判断
        self.read_buffer = ""  # 读取缓冲区，用于合并连续片段
        self.read_buffer_lock = threading.Lock()  # 缓冲区锁
        self.buffer_flush_timer = None  # 缓冲区刷新定时器
        # ANSI 转 HTML 转换器(使用inline模式确保颜色以内联样式输出)
        self.ansi_converter = Ansi2HTMLConverter(
            dark_bg=True,  # 使用深色背景（默认True）
            inline=True,  # 使用内联样式而非CSS类
            line_wrap=True,  # 启用换行
            linkify=True,  # 将URL转换为可点击链接
            title="",  # 设置文档标题
            font_size="large"  # 字体大小
        )

    def start(self) -> tuple[bool, str]:
        """启动终端进程"""
        if self.type == self.TERMINAL_TYPE_PYTHON:
            cmd, welcome_msg = self._create_python_terminal()
        elif self.type == self.TERMINAL_TYPE_CMD:
            cmd, welcome_msg = self._create_cmd_terminal()
        try:
            self.process = PtyProcess.spawn(cmd)
            self.is_running = True
            self.read_thread.start()
            self.status_thread.start()
            return True, welcome_msg
        except Exception as e:
            return False, f"启动终端失败: {str(e)}"

    def stop(self):
        """停止终端进程"""
        self.is_running = False
        # 刷新剩余的缓冲区数据
        if self.buffer_flush_timer:
            self.buffer_flush_timer.cancel()
        self.__flush_read_buffer()
        if self.process:
            try:
                self.process.close(force=True)
            except Exception:
                pass

    def __flush_read_buffer(self):
        """刷新读取缓冲区，将数据放入队列"""
        with self.read_buffer_lock:
            if self.read_buffer:
                self.char_queue.put(self.read_buffer)
                self.last_output_time = time.time()
                self.output_buffer += self.read_buffer
                self.read_buffer = ""

    def __schedule_flush(self, delay=0.1):
        """调度缓冲区刷新"""
        if self.buffer_flush_timer:
            self.buffer_flush_timer.cancel()
        self.buffer_flush_timer = threading.Timer(delay, self.__flush_read_buffer)
        self.buffer_flush_timer.daemon = True
        self.buffer_flush_timer.start()

    def __read_output(self):
        """后台线程读取输出"""
        while self.is_running and self.process:
            try:
                if self.process.isalive():
                    text = self.process.read(4096)
                    if text:
                        # 只过滤掉 CSI 控制序列中的特定序列(保留颜色码 \x1b[<数字>m)
                        # 过滤 [?1004h, [?9001h 等终端模式设置
                        text = re.sub(r'\x1b\[\?[0-9]+[hl]', '', text)
                        # 过滤 OSC 序列（如 ]0;标题\a，用于设置窗口标题）
                        text = re.sub(r'\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)', '', text)
                        # 过滤光标移动序列 (但保留颜色序列 \x1b[<数字>m)
                        text = re.sub(r'\x1b\[(\d+;\d+)*[HfABCDEFGJKST]', '', text)

                        # 将过滤后的数据加入读取缓冲区
                        with self.read_buffer_lock:
                            self.read_buffer += text

                        # 检查是否包含换行符，如果有则立即刷新
                        if '\n' in text or '\r\n' in text:
                            self.__flush_read_buffer()
                        else:
                            # 否则调度延迟刷新（100ms内无新数据则刷新）
                            self.__schedule_flush(delay=0.1)
                    else:
                        time.sleep(0.01)
                else:
                    break
            except Exception as e:
                break

    def __monitor_status(self):
        """监控线程：根据输出内容判断是否处于等待命令状态"""
        while self.is_running and self.process:
            try:
                time.sleep(0.1)  # 每100ms检查一次
                if not self.output_buffer:
                    continue
                # 根据终端类型判断提示符
                if self.type == self.TERMINAL_TYPE_PYTHON:
                    # Python 提示符：>>> 或 ...
                    if '>>>' in self.output_buffer or '...' in self.output_buffer:
                        # 检查最后几行是否有提示符
                        lines = self.output_buffer.split('\n')
                        for line in reversed(lines[-5:]):  # 检查最后5行
                            stripped = line.strip()
                            if stripped.startswith('>>>') or stripped.startswith('...'):
                                self.wait_command = True
                                self.output_buffer = ""  # 清空缓冲区
                                break
                elif self.type == self.TERMINAL_TYPE_CMD:
                    # CMD 提示符：包含路径和 > 
                    # 例如：C:\Users\Admin> 或 E:\code\Python>
                    lines = self.output_buffer.split('\n')
                    for line in reversed(lines[-3:]):  # 检查最后3行
                        stripped = line.strip()
                        # 匹配 CMD 提示符模式：盘符:\路径>
                        if re.search(r'[A-Z]:\\[^>]*>', stripped, re.IGNORECASE):
                            self.wait_command = True
                            self.output_buffer = ""  # 清空缓冲区
                            break
                # 如果超过2秒没有新输出，且缓冲区不为空，可能命令已执行完毕
                if time.time() - self.last_output_time > 2.0 and self.output_buffer:
                    self.wait_command = True
                    self.output_buffer = ""

            except Exception as e:
                time.sleep(0.5)

    def ansi_to_html(self, text):
        # 将 ANSI 文本转换为 HTML 片段(使用内联样式)
        html_fragment = self.ansi_converter.convert(text, full=False)
        # 手动将换行符转换为HTML换行标签
        html_fragment = html_fragment.replace('\r\n', '<br/>').replace('\n', '<br/>')
        return html_fragment

    def get_output(self, html=False, timeout=0.05) -> str:
        """
        获取终端输出
        :param html:是否返回html格式,默认不返回
        :param timeout: 超时时间（秒）
        :return: 输出字符串，如果没有输出则返回空字符串
        """
        if not self.process or not self.is_running:
            return ""
        if not self.process.isalive():
            self.is_running = False
            return ""
        try:
            text = self.char_queue.get(timeout=timeout)
            text = self.ansi_to_html(text) if html else text
            return text
        except Empty:
            return ""

    def send_command(self, command: str, escape_special_chars=True) -> bool:
        """
        发送命令到终端进程

        :param command: 要发送的命令
        :param escape_special_chars: 是否自动转义特殊字符（仅CMD模式有效）
        :return: 是否成功发送
        """
        if not command or not self.process or not self.is_running:
            return False

        try:
            normalized_cmd = command.replace('\n', '\r\n')
            if not normalized_cmd.endswith('\r\n'):
                normalized_cmd += '\r\n'
            self.process.write(normalized_cmd)
            return True
        except Exception:
            return False

    def _create_python_terminal(self):
        """
        创建 Python 交互式终端

        :return: (command, welcome_message)
        """
        cmd = [self.python_path, '-i']
        welcome_msg = "Python 终端已启动\n>>> "
        return cmd, welcome_msg

    def _create_cmd_terminal(self):
        """
        创建 CMD 命令行终端（支持 Conda 环境激活）

        :return: (command, welcome_message)
        """
        # 启用虚拟终端处理以支持ANSI颜色
        cmd = 'cmd.exe'
        welcome_msg = "CMD 终端已启动\nMicrosoft Windows [版本]\n(c) Microsoft Corporation。"
        return cmd, welcome_msg


class CapturePythonTerminal:
    """
    当前 Python 解释器输出捕获器
    通过重定向 sys.stdout/stderr 捕获当前进程的输出
    """

    def __init__(self):
        """初始化捕获器"""
        self.original_stdout = None
        self.original_stderr = None
        self.captured_stdout = StringIO()
        self.captured_stderr = StringIO()
        self.is_capturing = False  # 捕获状态
        self._lock = threading.Lock()

        # 自动保存相关
        self.auto_save_enabled = False
        self.auto_save_path = ""
        self.auto_save_interval = 1.0
        self.last_saved_stdout_len = 0
        self.last_saved_stderr_len = 0
        self._auto_save_timer = None
        self.include_stderr_in_auto_save = True
        self.timestamp_in_auto_save = True

    def start(self, auto_save_path=None, auto_save_interval=1.0, include_stderr=True, timestamp=True):
        """
        开始捕获输出
        
        :param auto_save_path: 自动保存文件路径,如果提供则启用自动保存
        :param auto_save_interval: 自动保存检查间隔(秒)
        :param include_stderr: 自动保存时是否包含错误输出
        :param timestamp: 自动保存时是否添加时间戳
        """
        if not self.is_capturing:
            self.original_stdout = sys.stdout
            self.original_stderr = sys.stderr
            self.captured_stdout = StringIO()
            self.captured_stderr = StringIO()
            self.last_saved_stdout_len = 0
            self.last_saved_stderr_len = 0

            sys.stdout = self.captured_stdout
            sys.stderr = self.captured_stderr
            self.is_capturing = True

            if auto_save_path:
                self.enable_auto_save(auto_save_path, auto_save_interval, include_stderr, timestamp)

    def stop(self) -> tuple[str, str]:
        """
        停止捕获并返回输出内容
        
        :return: (stdout_content, stderr_content)
        """
        with self._lock:
            self.disable_auto_save()

            if self.is_capturing:
                sys.stdout = self.original_stdout
                sys.stderr = self.original_stderr
                self.is_capturing = False

                stdout_content = self.captured_stdout.getvalue()
                stderr_content = self.captured_stderr.getvalue()

                self.captured_stdout.close()
                self.captured_stderr.close()

                return stdout_content, stderr_content
            return "", ""

    def get_output(self) -> tuple[str, str]:
        """
        获取当前已捕获的输出(不停止捕获)
        
        :return: (stdout_content, stderr_content)
        """
        with self._lock:
            if self.is_capturing:
                return self.captured_stdout.getvalue(), self.captured_stderr.getvalue()
            return "", ""

    def clear(self):
        """清空已捕获的内容"""
        with self._lock:
            if self.is_capturing:
                self.captured_stdout.truncate(0)
                self.captured_stdout.seek(0)
                self.captured_stderr.truncate(0)
                self.captured_stderr.seek(0)
                self.last_saved_stdout_len = 0
                self.last_saved_stderr_len = 0

    def enable_auto_save(self, filepath: str, interval=1.0, include_stderr=True, timestamp=True):
        """
        启用自动保存
        
        :param filepath: 保存文件路径
        :param interval: 检查间隔(秒)
        :param include_stderr: 是否包含错误输出
        :param timestamp: 是否添加时间戳
        """
        with self._lock:
            self.auto_save_path = filepath
            self.auto_save_interval = interval
            self.include_stderr_in_auto_save = include_stderr
            self.timestamp_in_auto_save = timestamp
            self.auto_save_enabled = True

            dir_path = os.path.dirname(filepath)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

            self.__start_auto_save_timer()

    def disable_auto_save(self):
        """禁用自动保存"""
        with self._lock:
            self.auto_save_enabled = False
            if self._auto_save_timer:
                self._auto_save_timer.cancel()
                self._auto_save_timer = None

    def __start_auto_save_timer(self):
        """启动自动保存定时器"""
        if self._auto_save_timer:
            self._auto_save_timer.cancel()

        self._auto_save_timer = threading.Timer(self.auto_save_interval, self.__auto_save_check)
        self._auto_save_timer.daemon = True
        self._auto_save_timer.start()

    def __auto_save_check(self):
        """检查是否有新内容并自动保存"""
        if not self.auto_save_enabled or not self.is_capturing:
            return

        with self._lock:
            current_stdout_len = len(self.captured_stdout.getvalue())
            current_stderr_len = len(self.captured_stderr.getvalue())

            has_new_content = (
                    current_stdout_len > self.last_saved_stdout_len or
                    current_stderr_len > self.last_saved_stderr_len
            )

            if has_new_content:
                self.__do_auto_save()
                self.last_saved_stdout_len = current_stdout_len
                self.last_saved_stderr_len = current_stderr_len

        if self.auto_save_enabled and self.is_capturing:
            self.__start_auto_save_timer()

    def __do_auto_save(self):
        """执行自动保存"""
        try:
            stdout_content = self.captured_stdout.getvalue()
            stderr_content = self.captured_stderr.getvalue()

            content = self._build_file_content(
                stdout_content, stderr_content,
                self.timestamp_in_auto_save,
                self.include_stderr_in_auto_save,
                "最后更新"
            )

            with open(self.auto_save_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"[AutoSave Error] {e}", file=self.original_stderr or sys.__stderr__)

    def save_to_file(self, filepath: str, include_stderr=True, timestamp=True, encoding='utf-8'):
        """
        手动保存当前捕获的内容到文件
        
        :param filepath: 保存路径(.txt文件)
        :param include_stderr: 是否包含错误输出
        :param timestamp: 是否在文件开头添加时间戳
        :param encoding: 文件编码
        :return: 是否保存成功
        """
        with self._lock:
            try:
                dir_path = os.path.dirname(filepath)
                if dir_path and not os.path.exists(dir_path):
                    os.makedirs(dir_path, exist_ok=True)

                stdout_content = self.captured_stdout.getvalue() if self.is_capturing else ""
                stderr_content = self.captured_stderr.getvalue() if self.is_capturing else ""

                content = self._build_file_content(
                    stdout_content, stderr_content,
                    timestamp, include_stderr,
                    "捕获时间"
                )

                with open(filepath, 'w', encoding=encoding) as f:
                    f.write(content)

                return True
            except Exception as e:
                print(f"保存文件失败: {e}", file=sys.stderr)
                return False

    @staticmethod
    def _build_file_content(stdout: str, stderr: str, timestamp: bool, include_stderr: bool, time_label: str) -> str:
        """
        构建文件内容
        
        :param stdout: 标准输出内容
        :param stderr: 错误输出内容
        :param timestamp: 是否添加时间戳
        :param include_stderr: 是否包含错误输出
        :param time_label: 时间标签文本
        :return: 格式化后的文件内容
        """
        lines = []

        if timestamp:
            from datetime import datetime
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"=== {time_label}: {now} ===\n")

        if stdout:
            lines.append("=== 标准输出 (stdout) ===")
            lines.append(stdout)
            lines.append("")

        if include_stderr and stderr:
            lines.append("=== 错误输出 (stderr) ===")
            lines.append(stderr)
            lines.append("")

        return '\n'.join(lines)

    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.stop()
        return False
