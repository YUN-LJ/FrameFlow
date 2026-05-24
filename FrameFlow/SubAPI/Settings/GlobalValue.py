"""全局常量"""
import os
import sys
import uuid
from enum import Enum
from io import BytesIO
from multiprocessing import Queue
from typing import Optional
# 自定义组件
from Fun.BaseTools import (
    FileBase, TaskManage, TaskProcessManage, Get, ImageLoad,
    ImageProcess, AsyncHTTPManage, TaskAsyncManage,
)

THUMB_SIZE = (300, 200)  # 略缩图尺寸
RUN_DIR = 'E:/code/Python/simple/AutoWallpaper/FrameFlow' if FileBase(sys.argv[0]).extension == '.py' else Get.run_dir()
CONFIG_DIR = os.path.join(RUN_DIR, 'config')
LOG_PATH = os.path.join(CONFIG_DIR, 'log.txt')
IMAGE_CACHE_DIR = os.path.join(CONFIG_DIR, 'image_cache')
CLIENT_QUEUE: Optional[Queue] = None  # 客户端队列,由客户端处理的事件,格式(任务类型枚举值,*args,**kwargs)
SERVER_QUEUE: Optional[Queue] = None  # 服务端队列,由服务端处理的事件,格式(任务类型枚举值,*args,**kwargs)
GLOBAL_TASK_MANAGE: Optional[TaskManage] = None  # 全局线程管理,支持优先级
GLOBAL_TASK_ASYNC_MANAGE: Optional[TaskAsyncManage] = None  # 全局异步管理
GLOBAL_Task_PROCESS_MANAGE: Optional[TaskProcessManage] = None  # 全局进程管理
GLOBAL_ASYNC_HTTP_MANAGE: Optional[AsyncHTTPManage] = None  # 全局异步HTTP管理
TOP_WINDOWS = None  # 全局顶层窗口


def generate_thumb(image, format='.jpg') -> BytesIO:
    """生成略缩图"""
    image_load = ImageLoad(image)
    ImageProcess(image_load).resize(THUMB_SIZE)
    return image_load.get_bytesIO(format)


def load_file(path: str) -> BytesIO:
    """加载文件"""
    return FileBase(path).open_bytesIO()


class ImageDataBase:
    """
    图像数据基类,项目内涉及到图像的由该类及其子类进行管理
    image数据会返回load_image方法,进行惰性加载,返回ImageLoad对象
    """

    def __init__(self, image_id: str = None):
        self.image_id = uuid.uuid4().hex if image_id is None else image_id  # 图像ID

    @property
    def image(self) -> ImageLoad:
        """图像数据"""
        return ImageLoad(self.load_image())

    def load_image(self):
        """图像加载方法"""
        raise NotImplementedError('请实现load_image方法')

    def save_image(self):
        """保存图像数据"""
        raise NotImplementedError('请实现save_image方法')

    def del_image(self):
        """删除本地文件"""
        raise NotImplementedError('请实现del_image方法')


class DataManageGetEnum(Enum):
    """获取数据类型枚举值"""
    CONFIG_DATA = 0


class WallHavenTaskClassEnum(Enum):
    """任务类型枚举值"""
    THUMB = 0  # 略缩图任务
    DOWNLOAD = 1  # 下载任务
    SEARCH = 2  # 搜索任务
    IMAGE_INFO = 3  # 图像信息
    KEY_INFO = 4  # 关键词信息
