"""终端相关"""
# 基本库
import re
import win32con
import win32gui
# PySide6库
from PySide6.QtCore import Signal, QThread, QTimer
from PySide6.QtGui import QWindow, QFont, QColor, QTextCursor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextEdit
# 风格组件
from qfluentwidgets import TextEdit, LineEdit
# 自定义库
from Fun.BaseTools import CreateTerminal, Get


class AnsiTextEdit(TextEdit):
    """
    支持ANSI转义序列的文本编辑器
    自动解析ANSI颜色码并渲染为富文本
    """
    # ANSI颜色映射表
    ANSI_COLORS = {
        '30': '#000000',  # Black
        '31': '#FF0000',  # Red
        '32': '#00FF00',  # Green
        '33': '#FFFF00',  # Yellow
        '34': '#0000FF',  # Blue
        '35': '#FF00FF',  # Magenta
        '36': '#00FFFF',  # Cyan
        '37': '#FFFFFF',  # White
        '90': '#808080',  # Bright Black
        '91': '#FF5555',  # Bright Red
        '92': '#55FF55',  # Bright Green
        '93': '#FFFF55',  # Bright Yellow
        '94': '#5555FF',  # Bright Blue
        '95': '#FF55FF',  # Bright Magenta
        '96': '#55FFFF',  # Bright Cyan
        '97': '#FFFFFF',  # Bright White
    }
    ANSI_BG_COLORS = {
        '40': '#000000',  # Black
        '41': '#FF0000',  # Red
        '42': '#00FF00',  # Green
        '43': '#FFFF00',  # Yellow
        '44': '#0000FF',  # Blue
        '45': '#FF00FF',  # Magenta
        '46': '#00FFFF',  # Cyan
        '47': '#FFFFFF',  # White
        '100': '#808080',  # Bright Black
        '101': '#FF5555',  # Bright Red
        '102': '#55FF55',  # Bright Green
        '103': '#FFFF55',  # Bright Yellow
        '104': '#5555FF',  # Bright Blue
        '105': '#FF55FF',  # Bright Magenta
        '106': '#55FFFF',  # Bright Cyan
        '107': '#FFFFFF',  # Bright White
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        # 设置等宽字体以更好地显示终端输出
        self.font_size = 10
        font = QFont("Consolas", self.font_size)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        # 当前样式状态
        self.current_color = None
        self.current_bg_color = None
        self.current_bold = False
        self.current_italic = False
        self.current_underline = False
        # ANSI解析正则表达式
        self.ansi_pattern = re.compile(r'\x1b\[([0-9;]*)m')

    def set_font_size(self, size: int):
        """
        设置字体大小

        :param size: 字体大小(磅值)
        """
        if size <= 0:
            return

        self.font_size = size
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)

    def get_font_size(self) -> int:
        """
        获取当前字体大小

        :return: 字体大小(磅值)
        """
        return self.font_size

    def increase_font_size(self, step=1):
        """
        增大字体

        :param step: 增大的步长
        """
        new_size = self.font_size + step
        self.set_font_size(new_size)

    def decrease_font_size(self, step=1):
        """
        减小字体

        :param step: 减小的步长
        """
        new_size = self.font_size - step
        if new_size > 0:
            self.set_font_size(new_size)

    def append_ansi_text(self, text: str):
        """
        追加包含ANSI转义序列的文本
        :param text: 包含ANSI码的原始文本
        """
        if not text:
            return
        cursor = self.textCursor()
        # 按 \r\n 分割文本(保留空字符串以检测连续的\r)
        segments = text.split('\r\n')
        for seg_idx, segment in enumerate(segments):
            if seg_idx > 0:
                # \r\n 表示换行,插入新块
                cursor.insertBlock()
            if not segment:
                continue
            # 在segment内部,按 \r 分割处理覆盖逻辑
            parts = segment.split('\r')
            for part_idx, part in enumerate(parts):
                if part_idx > 0:
                    # \r 表示回到行首并覆盖
                    # 移动到当前行开头
                    cursor.movePosition(QTextCursor.StartOfLine)
                    # 选中到行尾
                    cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                    # 删除旧内容
                    cursor.removeSelectedText()
                if not part:
                    continue
                # 解析ANSI码并插入文本
                ansi_parts = self.ansi_pattern.split(part)
                i = 0
                while i < len(ansi_parts):
                    if i % 2 == 0:
                        # 普通文本部分
                        if ansi_parts[i]:
                            self._insert_formatted_text(cursor, ansi_parts[i])
                    else:
                        # ANSI控制序列部分
                        if ansi_parts[i]:
                            self._parse_ansi_codes(ansi_parts[i])
                    i += 1
        self.setTextCursor(cursor)
        self._scroll_to_bottom()

    def _insert_formatted_text(self, cursor: QTextCursor, text: str):
        """插入格式化文本"""
        # 将换行符转换为块分隔
        lines = text.split('\n')
        for idx, line in enumerate(lines):
            if idx > 0:
                cursor.insertBlock()

            if line:
                # 应用当前样式
                format = cursor.charFormat()

                if self.current_color:
                    format.setForeground(QColor(self.current_color))
                else:
                    format.setForeground(QColor('#AAAAAA'))  # 默认前景色

                if self.current_bg_color:
                    format.setBackground(QColor(self.current_bg_color))

                font = QFont(format.font())
                font.setBold(self.current_bold)
                font.setItalic(self.current_italic)
                font.setUnderline(self.current_underline)
                format.setFont(font)

                cursor.setCharFormat(format)
                cursor.insertText(line)

    def _parse_ansi_codes(self, codes_str: str):
        """解析ANSI控制码"""
        if not codes_str:
            return

        codes = codes_str.split(';')

        for code in codes:
            code = code.strip()
            if not code:
                continue

            # 重置所有属性
            if code == '0':
                self.current_color = None
                self.current_bg_color = None
                self.current_bold = False
                self.current_italic = False
                self.current_underline = False

            # 前景色
            elif code in self.ANSI_COLORS:
                self.current_color = self.ANSI_COLORS[code]

            # 背景色
            elif code in self.ANSI_BG_COLORS:
                self.current_bg_color = self.ANSI_BG_COLORS[code]

            # 粗体
            elif code == '1':
                self.current_bold = True

            # 斜体
            elif code == '3':
                self.current_italic = True

            # 下划线
            elif code == '4':
                self.current_underline = True

            # 默认前景色
            elif code == '39':
                self.current_color = None

            # 默认背景色
            elif code == '49':
                self.current_bg_color = None

    def _scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_ansi(self):
        """清空文本并重置样式"""
        self.clear()
        self.current_color = None
        self.current_bg_color = None
        self.current_bold = False
        self.current_italic = False
        self.current_underline = False


class EmbeddedWindows(QWidget):
    """将窗口嵌入到PySide6窗口中"""

    def __init__(self, hwnd: int, parent=None):
        """
        :param hwnd:窗口句柄
        """
        super().__init__(parent)
        self.hwnd = hwnd

    def embedWindows(self) -> bool:
        """将窗口嵌入到Pyside6窗口中"""
        if self.hwnd:
            self.layout = QVBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            # 根据窗口句柄嵌入到pyside6界面中
            self.window = QWindow.fromWinId(self.hwnd)
            # 创建一个QWidget用于容纳terminal_window
            self.terminal_widget = QWidget.createWindowContainer(self.window)
            # 将widget_window添加到布局中
            self.layout.addWidget(self.terminal_widget)
            return True
        return False


class EmbeddedPythonTerminal(QWidget):
    """嵌入python启动器终端"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hwnd = None  # 已嵌入的启动器窗口句柄
        self.terminal_window = None  # 已嵌入的窗口

    def embedTerminal(self):
        """将窗口嵌入到Pyside6窗口中"""
        if self.terminal_window is None:
            self.layout = QHBoxLayout(self)
            hwnd = Get.python_cmd_hwnd()
            terminal_window = EmbeddedWindows(hwnd)
            if terminal_window.embedWindows():
                self.hwnd = hwnd
                self.terminal_window = terminal_window
                self.layout.addWidget(terminal_window)

    def show(self):
        super().show()
        self.embedTerminal()

    def closeEvent(self, event):
        super().closeEvent(event)  # 继续执行 Qt 窗口的关闭逻辑
        # 发送关闭消息给外部窗口（Windows API）
        if self.hwnd:
            # WM_CLOSE 消息：通知窗口关闭
            win32gui.SendMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)


class TerminalWidget(QWidget):
    """
    终端显示组件（基于 ConPTY + ansi2html）
    提供 UI 界面展示和交互，通过 HTML 渲染 ANSI 转义序列
    """
    loadFinished = Signal()  # 加载完成

    class TerminalOutputReader(QThread):
        """后台线程读取终端进程输出"""
        output_ready = Signal(str)

        def __init__(self, terminal_process: CreateTerminal, parent=None):
            super().__init__(parent)
            self.terminal_process = terminal_process
            self.running = True

        def run(self):
            """在线程中持续读取输出"""
            while self.running and self.terminal_process.is_running:
                output = self.terminal_process.get_output(False)
                if output:
                    self.output_ready.emit(output)
                self.msleep(5)

        def stop(self):
            """停止读取"""
            self.running = False
            self.wait(3000)

    def __init__(self, auto_start=True, parent=None, terminal_type="cmd", python_path=None):
        """
        初始化终端

        :param parent: 父窗口
        :param terminal_type: 终端类型，"python" 或 "cmd",默认为cmd类型
        :param python_path: Python 解释器路径（仅在 terminal_type="python" 时有效）
        """
        super().__init__(parent)
        self.parent = parent
        self.terminal = CreateTerminal(terminal_type, python_path)
        self.reader_thread: TerminalWidget.TerminalOutputReader = None
        self.__uiInit()
        if auto_start:
            self.startTerminal()

    def __uiInit(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.output_edit = AnsiTextEdit(self.parent)
        layout.addWidget(self.output_edit)

        self.input_line = LineEdit()

        if self.terminal.type == CreateTerminal.TERMINAL_TYPE_PYTHON:
            self.input_line.setPlaceholderText("输入 Python 命令...")
        else:
            self.input_line.setPlaceholderText("输入 CMD 命令...")

        self.input_line.returnPressed.connect(self.sendCommand)
        layout.addWidget(self.input_line)

    def startTerminal(self):
        """启动终端"""
        success, message = self.terminal.start()
        if success:
            # CMD和Python都使用char模式以获得实时输出
            self.reader_thread = self.TerminalOutputReader(self.terminal, self.parent)
            self.reader_thread.output_ready.connect(self.__appendOutput)
            self.reader_thread.start()

    def sendCommand(self, text=None):
        """发送命令到终端"""
        if self.terminal.is_running:
            command = self.input_line.text() if text is None else text
            if command:
                success = self.terminal.send_command(command)
                if success:
                    self.input_line.clear()
                else:
                    self.__appendOutput("发送命令失败\n")

    def __appendOutput(self, text):
        """添加输出文本-增量更新"""
        if not text:
            return
        self.output_edit.append_ansi_text(text)

    def closeEvent(self, event):
        """关闭时清理进程"""
        if self.reader_thread:
            self.reader_thread.stop()
        self.terminal.stop()
        super().closeEvent(event)


class AcondaWidget(TerminalWidget):
    """aconda终端显示"""

    def __init__(self, conda_path, activate_name=None, parent=None):
        """
        :param conda_path:activate路径
        :param activate_name:需要激活的环境
        """
        self.conda_path = conda_path
        self.activate_name = activate_name  # 当前激活的环境,为None时处于继承状态
        super().__init__(False, parent, "cmd")
        self.startTerminal()
        self.finished_init = False
        if self.activate_name is not None:
            self.__init_timer = QTimer()
            self.__init_timer.timeout.connect(self.__init_activate)
            self.__init_timer.start(5)

    def __init_activate(self):
        if self.terminal.wait_command:
            self.activateName(self.activate_name)
            self.finished_init = True
            self.__init_timer.stop()

    def activateName(self, name):
        self.sendCommand(f'{self.conda_path} {name}')
        self.activate_name = name
