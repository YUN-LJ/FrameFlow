"""数据管理模块"""
from SubAPI.DataManage.Tools import DataManage
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

import multiprocessing

# 检测是否为主进程
_is_main_process = multiprocessing.current_process().name == 'MainProcess'

if _is_main_process:
    # 单例模式实例化数据管理对象（仅主进程）
    DATA_MANAGE = DataManage()
    # 单例模式实例化数据对象（仅主进程）
    SEARCH_DATA = SearchData()
    IMAGE_INFO = ImageInfo()
    KEY_WORD = KeyWord()
    IMAGE_HISTORY = ImageHistory()
    CONFIG_DATA = ConfigData()
else:
    # 子进程中设置为 None，避免自动实例化
    DATA_MANAGE = None
    SEARCH_DATA = None
    IMAGE_INFO = None
    KEY_WORD = None
    IMAGE_HISTORY = None
    CONFIG_DATA = None


def get_data_object(name: str):
    """
    获取数据对象（子进程需要时手动调用）
    :param name: 对象名称，如 'IMAGE_INFO'
    :return: 数据对象实例
    """
    if not _is_main_process:
        # 子进程中按需创建
        class_map = {
            'SEARCH_DATA': SearchData,
            'IMAGE_INFO': ImageInfo,
            'KEY_WORD': KeyWord,
            'IMAGE_HISTORY': ImageHistory,
            'CONFIG_DATA': ConfigData,
        }
        if name in class_map:
            return class_map[name]()
    return globals().get(name)
