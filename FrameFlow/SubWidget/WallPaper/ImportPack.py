"""WallPaper的外部依赖库"""
# 基本库
import pandas as pd, os, time
from queue import Queue, Empty
from io import BytesIO
from typing import Callable
from threading import Lock, Thread
# Qt库
from PySide6.QtCore import QTimer, Signal, QEvent, QPoint, QThread, QObject
from PySide6.QtGui import QShortcut, QKeySequence, Qt, QGuiApplication
from PySide6.QtWidgets import (QWidget, QLabel, QScrollArea, QHeaderView,
                               QApplication, QCheckBox, QProgressBar, QTableWidgetItem,
                               QVBoxLayout, QHBoxLayout, QAbstractItemView)
# 美化库
from qfluentwidgets import FluentIcon as FIF, Action
from qfluentwidgets.components.dialog_box import MessageBoxBase, MessageBox
from qfluentwidgets.components.widgets import (
    PrimaryToolButton, TransparentPushButton, ProgressRing, CheckBox, RoundMenu,
    InfoBarIcon, InfoBar, InfoBarPosition, TeachingTip, TeachingTipTailPosition  # 气泡消息
)
# 功能库
from Fun.Norm.image import Image_PIL
from Fun.GUI_Qt.PySide6Mod import ImageWidget, get_exist_dir, get_exist_files, LeftandRightSplitter
from Fun.Norm import general, ThreadSafe, file, get
from BaseClass import (GlobalValue, TaskManage,
                       Task, TaskProgress, TaskSignal,
                       ImageInfo, KeyWord, SearchData, ConfigData)
from BaseClass.WidgetMod import (GroupBoxCell, GroupBoxCellBase, AppCore,
                                 LoadDialog, TopWidget, GroupBoxTable)
# 后端库
from SubAPI import WallPaper as WP
from SubAPI.WallPaper import WallPaperAPI as WPAPI
from SubAPI import WallHaven as WH
from SubAPI.WallHaven import WallHavenAPI as WHAPI

# 常量
THUMB_SIZE = (300, 400)  # 略缩图尺寸宽,高
