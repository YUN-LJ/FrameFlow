"""全局常量"""
import os
import sys
import uuid
import threading
from io import BytesIO
from PySide6.QtCore import Signal, QObject
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
GLOBAL_TASK_MANAGE: TaskManage = None  # 全局线程管理,支持优先级
GLOBAL_TASK_ASYNC_MANAGE: TaskAsyncManage = None  # 全局异步管理
GLOBAL_Task_PROCESS_MANAGE: TaskProcessManage = None  # 全局进程管理
GLOBAL_ASYNC_HTTP_MANAGE: AsyncHTTPManage = None  # 全局异步HTTP管理
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


class SelectManager(QObject):
    """
    选择管理类
    内部使用列表,元素唯一
    """
    keyAppendSignal = Signal(object)  # 关键词选中信号,发送单个元素或列表
    keyRemoveSignal = Signal(object)  # 关键词取消信号,发送单个元素或列表

    def __init__(self, parent):
        super().__init__(parent)
        self._items = []  # 内部存储
        self._lock = threading.RLock()

    def append(self, item: object, emit: bool = True):
        """添加关键词"""
        with self._lock:
            if item not in self._items:
                self._items.append(item)
                if emit:
                    self.keyAppendSignal.emit(item)

    def extend(self, items: list, emit: bool = True):
        with self._lock:
            diff_item = set(items) - set(self._items)  # 筛选不再列表中的元素
            self._items.extend(diff_item)
            if emit:
                self.keyAppendSignal.emit(diff_item)

    def remove(self, item: object, emit: bool = True):
        """移除关键词"""
        with self._lock:
            if item in self._items:
                self._items.remove(item)
                if emit:
                    self.keyRemoveSignal.emit(item)

    def __contains__(self, item: object) -> bool:
        """支持 in 操作符"""
        with self._lock:
            return item in self._items

    def __len__(self) -> int:
        """支持 len() 函数"""
        with self._lock:
            return len(self._items)

    def get_items(self) -> list[object]:
        """获取所有项目（返回副本）"""
        with self._lock:
            return self._items.copy()

    def clear(self, emit=True):
        """清空所有元素"""
        with self._lock:
            items = self._items.copy()
            for item in items:
                self.remove(item, emit)
