"""设置界面"""
import darkdetect
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSpacerItem, QSizePolicy

from Fun.BaseTools import Tools, FileBase, Get, Terminal, CapturePythonTerminal
from Fun.QtWidget import FluentWidgetBase
from Fun.QtWidget import MainWidget, AnsiTextEdit
from SubAPI.Settings.Desktop.SetCard import CardBase, MenuCard, SwitchCard


class BaseSetWin(FluentWidgetBase):
    """设置窗口,调用addSetWidget方法添加可添加其余设置文件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.capture_python_terminal = CapturePythonTerminal()
        if Terminal.is_python_terminal_visible():
            self.capture_python_terminal.start()
        self.exe_name = FileBase(Get.run_file()).name_base
        self.slot = BaseSetSlot(self)
        self.uiInit()
        self.bind()

    def uiInit(self):
        self.main_content = QWidget(self)
        self.main_layout = QVBoxLayout(self.main_content)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.addWidget(self.main_content)

        # 添加基本设置
        self.base_set_card = MenuCard('基本设置', self)

        self.checkBox_start = SwitchCard('自启动', self)
        self.checkBox_theme = SwitchCard('主题', self)
        self.checkBox_terminal = SwitchCard('控制台', self)

        self.checkBox_theme.setOffText('浅色')
        self.checkBox_theme.setOnText('深色')
        self.checkBox_terminal.setOffText('关闭')
        self.checkBox_terminal.setOnText('显示')

        self.base_set_card.addContentWidget(self.checkBox_start)
        self.base_set_card.addContentWidget(self.checkBox_theme)
        self.base_set_card.addContentWidget(self.checkBox_terminal)

        self.addSetCard(self.base_set_card)

        # 创建命令行容器
        self.terminal_card = MenuCard('日志', self)
        self.textEdit = AnsiTextEdit()
        self.textEdit.setMinimumHeight(200)
        self.textEdit.set_font_size(12)
        self.terminal_card.addContentWidget(self.textEdit)

        self.addWidget(self.terminal_card)

        # 创建弹簧：宽度20，高度0（自动），水平方向，最小尺寸策略
        # spacer = QSpacerItem(20, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        # 垂直弹簧：填满垂直剩余空间
        spacer = QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self._content_widget.layout().addSpacerItem(spacer)

        # 检查是否开机自启动
        if Tools.check_is_start(self.exe_name, 'user'):
            self.checkBox_start.setChecked(True)
        if darkdetect.theme() == 'Dark':
            self.checkBox_theme.setChecked(True)

    def bind(self):
        # 启动命令行监控定时器
        self.cmd_timer = QTimer()
        self.cmd_timer.timeout.connect(self.__cmd_timer)
        self.cmd_timer.start(1000)

        self.checkBox_theme.checkedChanged.connect(self.slot.checkBox_theme)
        self.checkBox_start.checkedChanged.connect(self.slot.checkBox_start)
        self.checkBox_terminal.checkedChanged.connect(self.slot.checkBox_terminal)

    def addSetCard(self, card: CardBase):
        """添加设置卡片"""
        self.main_layout.addWidget(card)

    def __cmd_timer(self):
        """定时获取命令行窗口内容"""
        if not self.textEdit.isVisible():
            return
        text = ''.join(self.capture_python_terminal.get_output())
        if self.textEdit.toPlainText() != text:
            self.textEdit.clear()
            self.textEdit.append_ansi_text(text)


class BaseSetSlot:
    def __init__(self, parent: BaseSetWin):
        self.parent = parent

    def checkBox_theme(self, checked):
        """切换浅色/深色"""
        if checked:
            MainWidget.change_theme(MainWidget.THEME_DARK)
        else:
            MainWidget.change_theme(MainWidget.THEME_LIGHT)

    def checkBox_start(self, checked):
        """开启/关闭开机自启动"""
        if checked:
            Tools.add_start_user(self.parent.exe_name, f'{Get.run_file()} --hide')
        else:
            if Tools.check_is_start(self.parent.exe_name, 'user'):
                Tools.remove_start_user(self.parent.exe_name)

    def checkBox_terminal(self, checked):
        """切换显示/隐藏"""
        Terminal.show_python_terminal() if checked else Terminal.hide_python_terminal()


if __name__ == '__main__':
    app = QApplication([])
    window = BaseSetWin()
    window.show()
    app.exec()
