"""全局变量"""
import os, sys, time, random, pandas as pd
from queue import Empty
from threading import Thread
from multiprocessing import Process, cpu_count, Queue
from concurrent.futures import ThreadPoolExecutor  # 线程池
# PySide6库
from PySide6.QtWidgets import (
    QWidget, QAbstractItemView, QHeaderView, QCheckBox,
    QVBoxLayout, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy,
    QSplitter, QProgressBar, QTableWidgetItem, QTableWidget, QGroupBox
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
from pyside6_GUI.PublicWidget import GroupBoxCell
# 自定义库
from Fun.GUI_Qt.PySide6Mod import ImageWidget, get_exist_dir, LeftandRightSplitter
from Fun.Norm import file, general
from Fun.Norm.image import Image_PIL, Image_Enum
from Fun.Norm.ThreadSafe import Dict, List
# 壁纸播放库
import wallpaper
from wallpaper.WallPaperPlay import WallPaperPlay
from wallhaven.WallHavenAPI import WallHavenAPI

# 常量
THUMB_SIZE = (300, 400)  # 略缩图尺寸宽,高
