# 标准库
import os, pandas as pd, numpy as np, time, random
from threading import Thread, Timer, Lock  # 定时器
from queue import Empty
from multiprocessing import Process, Queue  # 进程
from screeninfo import get_monitors
# PySide6
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QThread
# 自定义库
from Fun.Norm import file, get, general
from Fun.Norm.image import Image_PIL, Image_Enum, set_wallpaper_API
from Fun.GUI_Qt.PySide6Mod import WindowDesktop, ImageWidget
# 基本库
from BaseClass import (KeyWord, ImageInfo, ImageHistory, ConfigData, GlobalValue,
                       Task, TaskManage, TaskSignal)
import SubAPI.WallHaven as WH
from SubAPI.WallHaven import WallHavenAPI as WHAPI
