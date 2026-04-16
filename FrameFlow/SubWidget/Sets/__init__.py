"""
设置窗口
"""
from qfluentwidgets import setTheme, Theme
from ImportFile import Config
from SubWidget.ImportPack import *
from SubWidget.Sets.DesignFile.MainWidget import Ui_sets


class SetsWin(QWidget, Ui_sets):
    def __init__(self, parent=None):
        self.__parent = parent
        super().__init__(self.__parent)
        self.setupUi(self)
        self.title = File.FileBase(Get.run_file())
        self.__initUI()
        self.__bind()

    def __initUI(self):
        self.checkBox.setOffText("关闭")
        self.checkBox.setOnText("开启")
        self.checkBox_2.setOffText('浅色')
        self.checkBox_2.setOnText('深色')
        self.checkBox_show.setOffText('关闭')
        self.checkBox_show.setOnText('显示')
        # 检查是否开机自启动
        if Tools.check_is_start(self.title.name_base, 'user'):
            self.checkBox.setChecked(True)
        self.setStyleSheet("""SetsWin, SetsWin * {background-color: transparent;}""")

    def __bind(self):
        self.checkBox.checkedChanged.connect(self.__checkBox)
        self.checkBox_2.checkedChanged.connect(self.__checkBox_2)
        self.checkBox_show.checkedChanged.connect(self.__checkBox_show)
        self.cmd_timer = QTimer()
        self.cmd_timer.timeout.connect(self.__cmd_timer)
        self.cmd_timer.start(1000)

    def __cmd_timer(self):
        """定时检查命令行窗口"""
        capture_python_terminal: CapturePythonTerminal = Config.CAPTURE_PYTHON_TERMINAL
        text = ''.join(capture_python_terminal.get_output())
        if self.textEdit.toPlainText() != text:
            self.textEdit.clear()
            self.textEdit.append_ansi_text(text)

    def __checkBox(self, checked):
        """开启/关闭开机自启动"""
        program_text = self.title.name_base
        if checked:
            Tools.add_start_user(program_text, f'{Get.run_file()} --hide')
        else:
            if Tools.check_is_start(program_text, 'user'):
                Tools.remove_start_user(program_text)

    def __checkBox_2(self, checked):
        """切换浅色/深色"""
        if checked:
            setTheme(Theme.LIGHT)
        else:
            setTheme(Theme.DARK)

    def __checkBox_show(self, checked):
        """切换显示/隐藏"""
        if checked:
            Terminal.show_python_terminal()
        else:
            Terminal.hide_python_terminal()


if __name__ == '__main__':
    app = QApplication([])
    win = SetsWin()
    win.show()
    app.exec()
