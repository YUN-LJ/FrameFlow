"""WallHaven的外部依赖库"""
# 基本库
from io import BytesIO
from queue import Queue, Empty
from threading import Lock, Thread
from typing import Callable, Optional
import pandas as pd, os, time, requests, gc, asyncio
# 功能库
from Fun.BaseTools import File, Get, FileBase, AsyncJson, AsyncManage, AsyncChunkDownloader
from Fun.BaseTools import Time, ReuseTimer, ImageProcess, ImageLoad, ImageEnum
from Fun.BaseTools import Task, TaskManageBase, TaskProgress, TaskSignal, TaskManage
from BaseClass import GlobalValue, ImageInfo, KeyWord, SearchData, ConfigData
