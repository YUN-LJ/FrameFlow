"""全局变量"""
import os, sys, time

# PySide6库
from PySide6.QtWidgets import (
    QWidget, QAbstractItemView, QHeaderView, QCheckBox,
    QVBoxLayout, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy,
    QSplitter, QProgressBar, QTableWidgetItem
)
from PySide6.QtCore import QThread, Signal, QTimer, Qt
# 美化库
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets.components.dialog_box import MessageBoxBase, MessageBox
from qfluentwidgets.components.widgets import (
    TitleLabel, TransparentPushButton, SpinBox, LineEdit, ComboBox,  # 标签
    ProgressRing, IndeterminateProgressRing, ProgressBar,  # 进度条
    InfoBarIcon, TeachingTip, TeachingTipTailPosition  # 气泡消息
)
from qfluentwidgets.components.widgets.button import PrimaryToolButton
# UI
from pyside6_GUI.sub_ui.wallpaper.ui.wallpaper import Ui_wallpaper
from pyside6_GUI.sub_ui.wallpaper.ui.RightWidget import Ui_rightwidget
from pyside6_GUI.sub_ui.wallpaper.ui.LeftWidget import Ui_leftwidget
# 自定义库
from Fun.GUI_Qt.PySide6Mod import ImageWidget
from Fun.Norm import file
# 壁纸播放库
from wallpaper.WallPaperPlay import WallPaperPlay
