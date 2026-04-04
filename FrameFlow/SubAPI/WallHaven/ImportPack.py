"""WallHaven的外部依赖库"""
# 基本库
import pandas as pd, os, time, requests
from queue import Queue, Empty
from io import BytesIO
from typing import Callable
from threading import Lock, Thread
# 功能库
from Fun.Norm.image import Image_PIL
from Fun.GUI_Qt.PySide6Mod import ImageWidget
from Fun.Norm import general, ThreadSafe, file, get
from BaseClass import (GlobalValue, TaskManage,
                       Task, TaskProgress, TaskSignal,
                       ImageInfo, KeyWord, SearchData, ConfigData)
