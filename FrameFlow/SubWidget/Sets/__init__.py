"""
设置窗口
"""
from qfluentwidgets import setTheme, Theme
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
        # 检查是否开机自启动
        if Tools.check_is_start(self.title.name_base, 'user'):
            self.checkBox.setChecked(True)
        self.widget.embedTerminal()
        self.setStyleSheet("""SetsWin, SetsWin * {background-color: transparent;}""")

    def __bind(self):
        self.checkBox.checkedChanged.connect(self.__checkBox)
        self.checkBox_2.checkedChanged.connect(self.__checkBox_2)

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

    def closeEvent(self, event):
        self.widget.close()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication([])
    win = SetsWin()
    win.show()
    app.exec()
