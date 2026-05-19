"""Home的外部依赖库"""
# 基本库
import darkdetect
import pandas as pd, os, time, requests, re, gc, sys
from queue import Queue, Empty
from io import BytesIO
from typing import Callable
from threading import Lock, Thread
# Qt库
from PySide6.QtCore import QTimer, Signal, QEvent, QPoint, QThread, QObject
from PySide6.QtGui import QShortcut, QKeySequence, Qt, QGuiApplication, QPalette, QColor
from PySide6.QtWidgets import (QWidget, QLabel, QScrollArea, QHeaderView,
                               QApplication, QCheckBox, QProgressBar, QTableWidgetItem,
                               QVBoxLayout, QHBoxLayout, QAbstractItemView)
# 美化库
from qfluentwidgets import FluentIcon as FIF, Action, setTheme, Theme, setThemeColor
from qframelesswindow.utils import getSystemAccentColor
from qfluentwidgets.components.dialog_box import MessageBoxBase, MessageBox
from qfluentwidgets.components.widgets import (
    PrimaryToolButton, TransparentPushButton, ProgressRing, CheckBox, RoundMenu,
    InfoBarIcon, InfoBar, InfoBarPosition, TeachingTip, TeachingTipTailPosition,  # 气泡消息
    SimpleCardWidget, ScrollArea, SmoothScrollArea, HeaderCardWidget
)
# 功能库
from Fun.QtWidget import (
    ImageWidget, TableCell, TableRow, TopWidget, LazyLoadMS,
    get_exist_dir, get_exist_files, FluentWidgetBase, info_bar_decorator,
    debouncer_timer, throttle_reuse_timer_decorator
)
from Fun.BaseTools import (
    Get, File, Str, Tools, FileBase, ImageLoad, CapturePythonTerminal, Terminal
)
from Fun.BaseTools import (
    Task, TaskManageBase, TaskProgress, TaskSignal, TaskManage
)
# 后端库
from SubAPI.DataManage import IMAGE_INFO, KEY_WORD
from SubAPI.Settings import GlobalValue
from SubAPI.Settings.SignalConfig import (
    TopWindowSignal, WallHavenSignal, WallPaperSignal
)
