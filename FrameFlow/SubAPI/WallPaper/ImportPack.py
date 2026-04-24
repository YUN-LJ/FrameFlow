# 标准库
from queue import Empty, Full, Queue as QueueThread
from screeninfo import get_monitors
from threading import Thread, Timer, Lock  # 定时器
from multiprocessing import Process, Queue as QueueMul  # 进程
from io import BytesIO
import os, pandas as pd, numpy as np, time, random, gc
# PySide6
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QThread
# 自定义库
from Fun.BaseTools import FileBase, ReuseTimer, ImageProcess, ImageEnum, ImageLoad, Image
from Fun.BaseTools.Image import set_wallpaper_API
from Fun.QtWidget import ImageWidget, WindowDesktop
# 基本库
from BaseClass import (KeyWord, ImageInfo, ImageHistory, ConfigData, GlobalValue,
                       Task, TaskManage, TaskSignal)
# 后端库
import SubAPI.WallHaven as WH
from SubAPI.WallHaven import WallHavenAPI as WHAPI
