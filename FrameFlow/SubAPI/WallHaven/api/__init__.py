"""后端api包"""
from enum import Enum
from SubAPI.WallHaven.api.Tools import *
from SubAPI.WallHaven.api import WorkFlow


# 使用枚举值创建不同任务
class TaskClassEnum(Enum):
    """任务类型枚举值"""
    THUMB = 0  # 略缩图任务
    DOWNLOAD = 1  # 下载任务
    SEARCH = 2  # 搜索任务
    IMAGE_INFO = 3  # 图像信息
    KEY_INFO = 4  # 关键词信息


def create_task(task_event: TaskClassEnum, *args, **kwargs):
    """
    创建任务
    :param task_event:任务类型枚举值
    :param args:任务所需参数
    :param kwargs:任务所需参数
    """
