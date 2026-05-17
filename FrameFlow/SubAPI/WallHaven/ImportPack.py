"""WallHaven的外部依赖库"""
# 基本库
from io import BytesIO
from pathlib import Path
from queue import Queue, Empty
from threading import Lock, Thread, RLock
from typing import Callable, Optional, Union
import pandas as pd, os, time, requests, gc, asyncio, re
# 桌面端Qt库
from PySide6.QtCore import QTimer, Signal, QEvent, QPoint, QThread, QObject, QSize
from PySide6.QtGui import QShortcut, QKeySequence, Qt, QGuiApplication, QPalette, QColor
from PySide6.QtWidgets import (
    QWidget, QLabel, QScrollArea, QHeaderView, QApplication,
    QApplication, QCheckBox, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QAbstractItemView, QFrame
)
# 美化库
from qfluentwidgets import (
    FluentIcon as FIF, Action, SmoothMode, MessageBoxBase, MessageBox,
    PrimaryToolButton, TransparentPushButton, ProgressRing, CheckBox, RoundMenu,
    InfoBarIcon, InfoBar, InfoBarPosition, TeachingTip, TeachingTipTailPosition,  # 气泡消息
    SimpleCardWidget, ScrollArea, CardWidget, HeaderCardWidget, CaptionLabel,
    ProgressBar,
)
# 功能库
from Fun.QtWidget.FTabelWidget import (
    TableWidgetBase, DelegateBase, DataFrameModelBase,
    DataFrameListBase, ListWidgetBase, ListDelegateBase
)
from Fun.QtWidget import (
    ImageWidget, TableCell, TableRow, get_exist_dir, get_exist_files, FluentWidgetBase, FluentWidgetFromUI,
    LoadBarDialog, LoadRingDialog, SidebarWidget, MainWidget, ImageCell, ProgressRingButton,
    info_bar_decorator, teaching_tip_decorator, debouncer_timer, TableDataCell,
    throttle_qtimer_decorator, throttle_reuse_timer_decorator
)
from Fun.BaseTools import (
    File, Get, FileBase, AsyncJson, AsyncHTTPManage, AsyncChunkDownloader,
    Time, ReuseTimer, ImageProcess, ImageLoad, ImageEnum,
    Task, TaskManageBase, TaskProgress, TaskSignal, TaskManage,
    singleton_decorator, Str, Tools, CapturePythonTerminal, Terminal,
    copy_text_to_clipboard, LogClass,
)

from SubAPI.DataManage import SEARCH_DATA, IMAGE_INFO, KEY_WORD, CONFIG_DATA
from SubAPI.Settings import (
    GlobalValue, DataConfig, WallHavenConfig as Config, SignalConfig
)
from SubAPI.Settings.GlobalValue import ImageDataBase
