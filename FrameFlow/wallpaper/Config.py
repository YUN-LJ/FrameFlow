"""壁纸播放全局变量"""
from Fun.Norm import file, get, ini, general, ThreadSafe
from Fun.Norm.image import Image_PIL, Image_Enum, set_wallpaper_API
from Fun.GUI_Qt.PySide6Mod import WindowDesktop, ImageWidget
from wallhaven.WallHavenAPI import WallHavenAPI
from threading import Thread, Timer, Lock  # 定时器
from queue import Empty
from multiprocessing import Process, Queue  # 进程
import os, pandas as pd, numpy as np, time, random
from screeninfo import get_monitors
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QThread

PACK_NAME = 'wallpaper'
CONFIG = {}  # 本地配置数据
# 默认灰色图像
DEFAULT_IMAGE = np.full((224, 224, 3), fill_value=70, dtype=np.uint8)
# 路径配置
RUN_PATH = get.run_dir()  # 获取当前程序运行路径
CONFIG_DIR = os.path.join(RUN_PATH, 'config')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.ini')
IMAGE_HISTORY_PATH = os.path.join(CONFIG_DIR, 'image_history.feather')
# 壁纸播放,运行时会被修改,需要从实例中获取
IMAGE_DIR = []  # 用户选择的图片文件夹
IMAGE_CHOICE_KEY = []  # 用户选择的关键词
IMAGE_TIME = 10.0  # 播放间隔,默认10秒
IMAGE_TEMP_NUM = 3  # 图片缓冲数量,默认3张
# 播放模式
IMAGE_CUSTOM_MODE = 0  # 自定义模式,从用户选择的本地文件夹中读取照片
IMAGE_KEY_MODE = 1  # 关键词模式,按照wallhaven模块中的收藏的关键词获取图像数据
IMAGE_VIDEO_MODE = 2  # 视频模式,仅在IMAGE_WINDOWS_QT模式下支持
# 播放接口
IMAGE_WINDOWS_API = 0  # windows系统API播放壁纸
IMAGE_WINDOWS_QT = 1  # windows系统使用qt创建桌面窗口播放壁纸
IMAGE_LINUX_API = 2  # liunx系统API播放壁纸
# 播放历史
IMAGE_HISTORY_COLUMNS = ['id']  # 如果是图像ID则去图像信息文件中查找图像的地址,如果是图像地址则直接排除
IMAGE_HISTORY_DTYPE = {'id': 'str'}


def default_config():
    """默认配置文件"""
    global CONFIG
    default = {
        'image_dir': ';'.join(IMAGE_DIR),
        'image_key': ';'.join(IMAGE_CHOICE_KEY),
        'image_time': IMAGE_TIME,
        'image_temp_num': IMAGE_TEMP_NUM,
        'image_mode': IMAGE_CUSTOM_MODE,
    }
    config = ini.INI(CONFIG_PATH, 'wallpaper')
    config.append_values(default)
    CONFIG = default


def save_config(image_dir: list, image_key: list, image_time: float, image_temp_num: int, image_mode: int):
    """保存配置文件"""
    global CONFIG
    config_dict = {
        'image_dir': ';'.join(image_dir),
        'image_key': ';'.join(image_key),
        'image_time': image_time,
        'image_temp_num': image_temp_num,
        'image_mode': image_mode,
    }
    config = ini.INI(CONFIG_PATH, 'wallpaper')
    config.append_values(config_dict)
    CONFIG = config_dict


def load_config():
    """加载配置文件"""
    global IMAGE_DIR, IMAGE_CHOICE_KEY, IMAGE_TIME, IMAGE_TEMP_NUM, IMAGE_HISTORY, CONFIG
    config = ini.INI(CONFIG_PATH, 'wallpaper')
    CONFIG = config.get_values()
    if CONFIG['image_dir'] != '':
        IMAGE_DIR = CONFIG['image_dir'].split(';')
    if CONFIG['image_key'] != '':
        IMAGE_CHOICE_KEY = CONFIG['image_key'].split(';')
    IMAGE_TIME = float(CONFIG['image_time'])
    IMAGE_TEMP_NUM = int(CONFIG['image_temp_num'])
    CONFIG['image_mode'] = int(CONFIG['image_mode'])
