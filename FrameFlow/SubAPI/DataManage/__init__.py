"""数据管理模块"""
from SubAPI.DataManage.Tools import DataManage, DataBase
from SubAPI.DataManage.DataClass import (
    SearchData, ImageInfo, KeyWord, ImageHistory, ConfigData
)

__all__ = [
    # 类
    'DataManage',
    'SearchData',
    'ImageInfo',
    'KeyWord',
    'ImageHistory',
    'ConfigData',
    # 对象
    'DATA_MANAGE',
    'SEARCH_DATA',
    'IMAGE_INFO',
    'KEY_WORD',
    'IMAGE_HISTORY',
    'CONFIG_DATA'
]

from typing import Optional

DATA_MANAGE: Optional[DataManage] = None
SEARCH_DATA: Optional[SearchData] = None
IMAGE_INFO: Optional[ImageInfo] = None
KEY_WORD: Optional[KeyWord] = None
IMAGE_HISTORY: Optional[ImageHistory] = None
CONFIG_DATA: Optional[ConfigData] = None


def initDataClass():
    """初始化单例类"""
    global DATA_MANAGE, SEARCH_DATA, IMAGE_INFO, \
        KEY_WORD, IMAGE_HISTORY, CONFIG_DATA
    # 单例模式实例化数据管理对象（仅主进程）
    DATA_MANAGE = DataManage()
    # 单例模式实例化数据对象（仅主进程）
    SEARCH_DATA = SearchData()
    IMAGE_INFO = ImageInfo()
    KEY_WORD = KeyWord()
    IMAGE_HISTORY = ImageHistory()
    CONFIG_DATA = ConfigData()
