# 标准库
import ctypes, sys, darkdetect, os
# 图形库
from PySide6.QtWidgets import QHBoxLayout, QFrame, QWidget, QApplication
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QIcon
# 导入资源文件
from ImportFile import FlowFrameRes
# 美化库
from qfluentwidgets import (NavigationItemPosition, MSFluentWindow,
                            setThemeColor, setTheme, Theme,
                            FluentIcon as FIF)
from qframelesswindow.utils import getSystemAccentColor
from qfluentwidgets.components.widgets import InfoBar, InfoBarPosition  # 气泡消息
# 自定义库
from Fun.QtWidget import LazyLoadMS
from Fun.QtWidget import TrayIcon
from Fun.Norm import general, get, file
from BaseClass import DataManage, GlobalValue, AppCore, ImageInfo, KeyWord
