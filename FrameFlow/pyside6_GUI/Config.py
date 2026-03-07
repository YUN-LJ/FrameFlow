# 标准库
import ctypes, sys, darkdetect
# 图形库
from PySide6.QtWidgets import QHBoxLayout, QFrame, QWidget
from PySide6.QtGui import QIcon
# 导入资源文件
from pyside6_GUI import res
# 美化库
from qfluentwidgets import (NavigationItemPosition, MSFluentWindow,
                            setThemeColor, setTheme, Theme,
                            FluentIcon as FIF)
from qframelesswindow.utils import getSystemAccentColor
# 导入子窗口
from pyside6_GUI.sub_ui.home.wallhaven_win import WallHavenWin
# from pyside6_GUI.sub_ui.sets.sets_win import SetsWin
# from pyside6_GUI.sub_ui.wallpaper.wallpaper_win import WallPaperWin
# 自定义库
from Fun.GUI_Qt.PySide6Mod import TrayIcon
from Fun.Norm import general, get

LIGHT = """QWidget {
            background-color: rgb(245,245,245);
            color: black;}"""
DARK = """QWidget {
            background-color: rgb(45,45,45);
            color: black;}"""

ICO_PATH = {
    '主页': FIF.HOME,
    '壁纸播放': FIF.PHOTO,
    '设置': FIF.SETTING,
}
