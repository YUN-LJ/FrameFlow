# 标准库
import ctypes, sys, darkdetect, os
# 图形库
from PySide6.QtWidgets import QHBoxLayout, QFrame, QWidget, QApplication
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon
# 导入资源文件
from ImportFile import FlowFrameRes
# 美化库
from qfluentwidgets import (NavigationItemPosition, MSFluentWindow,
                            setThemeColor, setTheme, Theme,
                            FluentIcon as FIF)
from qframelesswindow.utils import getSystemAccentColor
from qfluentwidgets.components.widgets import InfoBar, InfoBarPosition  # 气泡消息
# 导入子窗口
from SubWidget.Home import HomeWin
from SubWidget.WallPaper import WallPaperWin
from SubWidget.Sets import SetsWin
from BaseClass import DataManage, GlobalValue, AppCore, ImageInfo, KeyWord
# 自定义库
from Fun.GUI_Qt.PySide6Mod import TrayIcon
from Fun.Norm import general, get, file

ICO_PATH = {
    '主页': FIF.HOME,
    '壁纸播放': FIF.PHOTO,
    '设置': FIF.SETTING,
}
