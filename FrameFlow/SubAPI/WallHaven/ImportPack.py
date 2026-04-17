"""WallHaven的外部依赖库"""
# 基本库
from io import BytesIO
from typing import Callable
from queue import Queue, Empty
from threading import Lock, Thread
import pandas as pd, os, time, requests
# 功能库
from Fun.BaseTools import File, Get, FileBase
from Fun.BaseTools import Time, ReuseTimer, ImageProcess, ImageLoad, ImageEnum
from BaseClass import (GlobalValue, TaskManage,
                       Task, TaskProgress, TaskSignal,
                       ImageInfo, KeyWord, SearchData, ConfigData)
