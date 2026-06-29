"""全局常量"""
import os
import sys
import uuid
from enum import Enum
from io import BytesIO
from multiprocessing import Queue
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import HeaderCardWidget, TogglePushButton
# 自定义组件
from SubAPI.Settings.Desktop.SetCard import MenuCard
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


class WallHavenClassWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__uiInit()

    def __uiInit(self):
        # 主布局
        self.view_layout = QVBoxLayout(self)
        self.view_layout.setContentsMargins(0, 0, 0, 0)

        self.__addCategories()
        self.__addPurity()
        self.view_layout.addStretch()

    def __addCategories(self):
        # 类别选择
        self.categories_heard = HeaderCardWidget(self)
        self.categories_heard.setTitle('类别选择')

        # 添加布局
        self.categories_layout = QHBoxLayout(self)
        self.categories_heard.viewLayout.addLayout(self.categories_layout)

        # 添加切换按钮
        self.checkBox_general = TogglePushButton(self.categories_heard)
        self.checkBox_general.setText('常规')
        self.checkBox_general.setChecked(True)
        self.checkBox_anime = TogglePushButton(self.categories_heard)
        self.checkBox_anime.setText('动漫')
        self.checkBox_anime.setChecked(True)
        self.checkBox_people = TogglePushButton(self.categories_heard)
        self.checkBox_people.setText('人物')
        self.checkBox_people.setChecked(True)

        # 添加布局
        self.categories_layout.addWidget(self.checkBox_general)
        self.categories_layout.addWidget(self.checkBox_anime)
        self.categories_layout.addWidget(self.checkBox_people)

        self.view_layout.addWidget(self.categories_heard)

    def __addPurity(self):
        # 分级选择
        self.purity_heard = HeaderCardWidget(self)
        self.purity_heard.setTitle('分级选择')

        # 添加布局
        self.purity_layout = QHBoxLayout(self)
        self.purity_heard.viewLayout.addLayout(self.purity_layout)

        # 添加切换按钮
        self.checkBox_sfw = TogglePushButton(self.purity_heard)
        self.checkBox_sfw.setText('正常级')
        self.checkBox_sfw.setChecked(True)
        self.checkBox_sketchy = TogglePushButton(self.purity_heard)
        self.checkBox_sketchy.setText('粗略级')
        self.checkBox_sketchy.setChecked(True)
        self.checkBox_nsfw = TogglePushButton(self.purity_heard)
        self.checkBox_nsfw.setText('限制级')
        self.checkBox_nsfw.setChecked(True)

        # 添加布局
        self.purity_layout.addWidget(self.checkBox_sfw)
        self.purity_layout.addWidget(self.checkBox_sketchy)
        self.purity_layout.addWidget(self.checkBox_nsfw)

        self.view_layout.addWidget(self.purity_heard)

    def getPurity(self) -> str:
        return ''.join([
            str(int(self.checkBox_sfw.isChecked())),
            str(int(self.checkBox_sketchy.isChecked())),
            str(int(self.checkBox_nsfw.isChecked())),
        ])

    def getCategories(self) -> str:
        return ''.join([
            str(int(self.checkBox_general.isChecked())),
            str(int(self.checkBox_anime.isChecked())),
            str(int(self.checkBox_people.isChecked())),
        ])


class WallHavenClassWidgetExpand(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__uiInit()

    def __uiInit(self):
        # 主布局
        self.view_layout = QVBoxLayout(self)
        self.view_layout.setContentsMargins(0, 0, 0, 0)

        self.__addCategories()
        self.__addPurity()
        self.view_layout.addStretch()

    def __addCategories(self):
        # 类别选择
        self.categories_heard = MenuCard(parent=self)
        self.categories_heard.setTitle('类别选择')

        # 添加布局
        self.categories_layout = QHBoxLayout(self)
        self.categories_heard.addContentLayout(self.categories_layout)

        # 添加切换按钮
        self.checkBox_general = TogglePushButton(self.categories_heard)
        self.checkBox_general.setText('常规')
        self.checkBox_general.setChecked(True)
        self.checkBox_anime = TogglePushButton(self.categories_heard)
        self.checkBox_anime.setText('动漫')
        self.checkBox_anime.setChecked(True)
        self.checkBox_people = TogglePushButton(self.categories_heard)
        self.checkBox_people.setText('人物')
        self.checkBox_people.setChecked(True)

        # 添加布局
        self.categories_layout.addWidget(self.checkBox_general)
        self.categories_layout.addWidget(self.checkBox_anime)
        self.categories_layout.addWidget(self.checkBox_people)

        self.view_layout.addWidget(self.categories_heard)

    def __addPurity(self):
        # 分级选择
        self.purity_heard = MenuCard(parent=self)
        self.purity_heard.setTitle('分级选择')

        # 添加布局
        self.purity_layout = QHBoxLayout(self)
        self.purity_heard.addContentLayout(self.purity_layout)

        # 添加切换按钮
        self.checkBox_sfw = TogglePushButton(self.purity_heard)
        self.checkBox_sfw.setText('正常级')
        self.checkBox_sfw.setChecked(True)
        self.checkBox_sketchy = TogglePushButton(self.purity_heard)
        self.checkBox_sketchy.setText('粗略级')
        self.checkBox_sketchy.setChecked(True)
        self.checkBox_nsfw = TogglePushButton(self.purity_heard)
        self.checkBox_nsfw.setText('限制级')
        self.checkBox_nsfw.setChecked(True)

        # 添加布局
        self.purity_layout.addWidget(self.checkBox_sfw)
        self.purity_layout.addWidget(self.checkBox_sketchy)
        self.purity_layout.addWidget(self.checkBox_nsfw)

        self.view_layout.addWidget(self.purity_heard)


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = WallHavenClassWidgetExpand()
    w.show()
    app.exec()
