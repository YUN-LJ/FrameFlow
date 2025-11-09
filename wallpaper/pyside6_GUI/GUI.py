"""PySide6GUI界面"""
# 图形库
from PySide6.QtWidgets import QHBoxLayout, QFrame, QWidget
from PySide6.QtGui import QIcon

# 美化库
from qfluentwidgets import (NavigationItemPosition, MSFluentWindow,
                            setThemeColor, setTheme, Theme,
                            FluentIcon as FIF)
from qframelesswindow.utils import getSystemAccentColor

from Fun.GUI_Qt.PySide6Mod import TrayIcon
from Fun.Norm import general, get

import ctypes, sys

# 导入资源文件
from . import res

# 导入全局变量
from pyside6_GUI.globals_values import *

ICO_PATH = {
    '主页': FIF.HOME,
    '壁纸播放': FIF.PHOTO,
    '设置': FIF.SETTING,
}


class PySide6GUI(MSFluentWindow):
    """ 主界面 """

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(f":/icons/ico_main.png"))
        self.setWindowTitle('FrameFlow-画框')

        # 设置任务栏图标
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("FrameFlow-画框")

        # 快速启动:只加载必要窗口
        self.fast_run = False

        # 列出全部子窗口
        self.sub_widget()

        # 添加窗口
        self.initNavigation()

        # 切换至主页
        # self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget.currentChanged.connect(lambda index: AddPage(self.stackedWidget.currentWidget(), index))

    def sub_widget(self):
        self.subwidget = {
            '主页': Widget('主页', self),
            '壁纸播放': Widget('壁纸播放', self),
            '设置': Widget('设置', self),
        }

    def initNavigation(self):
        # 子窗口
        for text, widget in self.subwidget.items():
            if text == '设置':
                continue
            self.addSubInterface(widget, ICO_PATH[text], text, position=NavigationItemPosition.SCROLL)

        # 设置
        self.addSubInterface(self.subwidget['设置'], ICO_PATH['设置'], '设置', position=NavigationItemPosition.BOTTOM)

    def closeEvent(self, event):
        # 重写关闭函数,只隐藏窗口不退出
        self.hide()
        event.ignore()

    def exit_(self):
        """退出"""
        AddPage.page_object[2].kill_cmd()
        general.kill_program(get.main_pid())

    def restart(self, *argv):
        general.cmd_admin_run(f'{get.run_file()} --show {' '.join(argv)}')
        self.exit_()

    def show(self):
        self.resize(1000, 600)
        # 设置窗口居中
        rect = app.primaryScreen().availableGeometry()
        w, h = rect.width(), rect.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        # 设置主题色
        # setThemeColor('#7da3d3')
        super().show()


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)

        # 必须给子界面设置全局唯一的对象名
        self.setObjectName(text.replace(' ', '-'))


# 导入子窗口
from .sub_ui.wallpaper.wallpaper_win import WallPaperWin
from .sub_ui.home.home_win import HomeWin
from .sub_ui.sets.sets_win import SetsWin


class AddPage:
    page_dict = {
        0: HomeWin,
        1: WallPaperWin,
        2: SetsWin,
    }

    page_object = {}  # 实例化对象

    def __init__(self, widget: QWidget, index: int):
        self.widget = widget
        self.page_change(index)

    def page_change(self, index: int) -> bool:
        """页面改变时"""
        global GUI
        function_name = AddPage.page_dict.get(index, False)
        if function_name:
            if not self.widget.hBoxLayout.count():
                window = function_name(GUI)
                self.widget.hBoxLayout.addWidget(window)
                AddPage.page_object[index] = window
                print(f'已添加子窗口{str(function_name)}')
                # AddPage.page_object.update({function_name: window})
            return True
        else:
            return False


def start_GUI():
    from PySide6.QtWidgets import QApplication
    global app, GUI
    app = QApplication([])
    GUI = PySide6GUI()
    # 设置所有QWidget类背景色为浅色
    GUI.setStyleSheet(LIGHT)
    setTheme(Theme.LIGHT)
    # 全局主题
    # 只能获取 Windows 和 macOS 的主题色
    if sys.platform in ["win32", "darwin"]:
        # save=True时对后续创建的对象也会生效,否则只对当前存在的对象生效
        setThemeColor(getSystemAccentColor(), save=False, lazy=True)
    # 创建系统托盘
    tray = TrayIcon(GUI, GUI.exit_)
    # 加载子窗口
    if GUI.fast_run:
        AddPage(GUI.stackedWidget.widget(2), 2)  # 对应设置
        AddPage(GUI.stackedWidget.widget(0), 0)  # 对应主页
    else:
        for index in AddPage.page_dict.keys():
            AddPage(GUI.stackedWidget.widget(index), index)

    # 参数映射字典
    argv_dict = {
        '--show': GUI.show,
        '--ohm': AddPage.page_object.get(0).start
    }

    # 启动时的参数
    for key in sys.argv[1:]:
        key_func = argv_dict.get(key, False)
        if key_func:
            key_func()

    tray.show()
    app.exec()


if __name__ == '__main__':
    start_GUI()
