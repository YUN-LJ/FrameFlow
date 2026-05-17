"""设置界面"""
import darkdetect
from PySide6.QtCore import QTimer
from Fun.QtWidget import FluentWidgetBase
from PySide6.QtWidgets import QApplication, QWidget
from SubAPI.Settings.Desktop.DesignFile.SetWidget import Ui_base_sets
from SubAPI.Settings.Desktop.DesignFile.BaseSet import Ui_base_set_win
from Fun.BaseTools import Tools, FileBase, Get, Terminal, CapturePythonTerminal
from Fun.QtWidget import MainWidget, AnsiTextEdit
from qfluentwidgets import HeaderCardWidget


class BaseSetWin(FluentWidgetBase, Ui_base_sets, Ui_base_set_win):
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
        # 添加主容器
        self.main_content = QWidget()
        Ui_base_set_win.setupUi(self, self.main_content)
        self.addWidget(self.main_content)

        # 添加基本设置
        self.base_set_widget = QWidget()
        Ui_base_sets.setupUi(self, self.base_set_widget)
        self.addSetWidget(self.base_set_widget, '基本设置')

        # 创建命令行容器
        self.textEdit = AnsiTextEdit()
        self.textEdit.setMinimumHeight(200)
        self.textEdit.set_font_size(12)
        self.groupBox.viewLayout.addWidget(self.textEdit)

        self.checkBox_start.setOffText("关闭")
        self.checkBox_start.setOnText("开启")
        self.checkBox_theme.setOffText('浅色')
        self.checkBox_theme.setOnText('深色')
        self.checkBox_terminal.setOffText('关闭')
        self.checkBox_terminal.setOnText('显示')
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

    def addSetWidget(self, widget: HeaderCardWidget | QWidget, title=None) -> HeaderCardWidget:
        """
        param widget:待添加窗口
        param title:名称,如果不是HeaderCardWidget类则必须指定
        return :返回被HeaderCardWidget包装后的窗口
        """
        if isinstance(widget, HeaderCardWidget):
            header_widget = widget
        elif isinstance(widget, QWidget):
            if title is None:
                raise ValueError('请指定标题')
            header_widget = HeaderCardWidget(self)
            header_widget.setTitle(title)
            header_widget.viewLayout.addWidget(widget)
        self.verticalLayout_set_other.addWidget(header_widget)
        return header_widget

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
