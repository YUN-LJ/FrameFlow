"""设置界面"""
import os

from PySide6.QtWidgets import QWidget, QSpacerItem, QSizePolicy

from .ui.sets import Ui_sets

from Fun.GUI_Qt import PySide6Mod
from Fun.Norm import get, file, general

# 导入全局变量
from pyside6_GUI.globals_values import *


class SetsWin(QWidget, Ui_sets):

    def __init__(self, parent=None):
        self.__parent = parent
        super().__init__(parent)
        self.setupUi(self)

        self.__init_ui()

        self.__bind()

    def __init_ui(self):
        self.checkBox.setOffText("关闭")
        self.checkBox.setOnText("开启")
        self.checkBox_2.setOffText('浅色')
        self.checkBox_2.setOnText('深色')
        self.title = os.path.basename(get.run_file())
        ext = file.get_file_extension(self.title)
        if ext == 'exe':
            title = file.get_file_root(self.title)
        else:
            title = self.title
        self.hwnd = PySide6Mod.embed_qt(title, self.widget_cmd, accurate=False)
        # 找不到时添加一个弹簧控件
        # if not self.hwnd:
        #     self.verticalLayout_cmd.addItem(
        #         QSpacerItem(
        #             40, 20,
        #             QSizePolicy.Policy.Expanding,
        #             QSizePolicy.Policy.Minimum))

    def __bind(self):
        self.checkBox.checkedChanged.connect(self.__checkBox)
        self.checkBox_2.checkedChanged.connect(self.__checkBox_2)

    def __checkBox(self, checked):
        """开启/关闭开机自启动"""
        program_text = file.get_file_root(self.title)
        if checked:
            general.add_start_user(program_text, get.run_file())
        else:
            if general.check_is_start(program_text, 'user'):
                general.remove_start_user(program_text)

    def __checkBox_2(self, checked):
        """切换浅色/深色"""
        if checked:
            self.__parent.setStyleSheet(LIGHT)

    def kill_cmd(self):
        # 发送关闭消息给外部窗口（Windows API）
        if self.hwnd:
            import win32gui, win32con
            # WM_CLOSE 消息：通知窗口关闭
            win32gui.SendMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)
