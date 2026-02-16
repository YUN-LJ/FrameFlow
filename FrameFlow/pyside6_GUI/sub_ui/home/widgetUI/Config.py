"""全局变量"""
import pandas as pd
import numpy as np
import os, sys, io, time, random

# 导入线程库
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor  # 线程池
from threading import Lock, Thread
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
# UI文件
from pyside6_GUI.sub_ui.home.ui.LeftWidget import Ui_ImageTable
from pyside6_GUI.sub_ui.home.ui.RightWidget import Ui_RightWidget
from pyside6_GUI.sub_ui.home.ui.wallhaven import Ui_wallhaven
from pyside6_GUI.sub_ui.home.ui.ImageDialog import Ui_Image
# 导入后端文件
from wallhaven.WallHavenAPI import NUM_WORK, WallHavenAPI, TaskEnum
# 自定义功能库
from Fun.GUI_Qt.PySide6Mod import ImageWidget, get_exist_dir
from Fun.Norm.ThreadSafe import Dict, List
from Fun.Norm import file, get, ini
from Fun.Norm.image import Image_PIL

# 默认灰色图像
DEFAULT_IMAGE = np.full((224, 224, 3), fill_value=70, dtype=np.uint8)
