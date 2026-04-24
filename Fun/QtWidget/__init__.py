"""Qt组件包"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # 模块
    from . import FCell, FTabel
    # FWidget 模块中的类
    from .FWidget import ImageWidget, LazyLoadMS, TrayIcon, EmbeddedWindows, EmbeddedPythonTerminal, \
        WindowDesktop, LeftandRightSplitter, TerminalWidget, AcondaWidget, AnsiTextEdit
    # FCell 模块中的类
    from .FCell import ImageCellBase, ImageCell
    # FTabel 模块中的类
    from .FTabel import TableBase, TableCell, TableRow

# 声明对外接口
__all__ = [
    # 模块
    'FCell', 'FTabel',
    # FWidget 模块中的类
    'ImageWidget', 'LazyLoadMS', 'TrayIcon', 'EmbeddedWindows', 'EmbeddedPythonTerminal',
    'WindowDesktop', 'LeftandRightSplitter', 'TerminalWidget', 'AcondaWidget', 'AnsiTextEdit',
    # FCell 模块中的类
    'ImageCellBase', 'ImageCell',
    # FTabel 模块中的类
    'TableBase', 'TableCell', 'TableRow',
]

import importlib
from PySide6.QtWidgets import QFileDialog
from Fun.BaseTools import Get

# 模块名与模块路径的映射字典
_MODULE_MAP = {
    # 模块直接导入
    'FCell': '.FCell',
    'FTabel': '.FTabel',
    # FWidget 模块中的类
    'ImageWidget': '.FWidget',
    'LazyLoadMS': '.FWidget',
    'TrayIcon': '.FWidget',
    'EmbeddedWindows': '.FWidget',
    'EmbeddedPythonTerminal': '.FWidget',
    'WindowDesktop': '.FWidget',
    'LeftandRightSplitter': '.FWidget',
    'TerminalWidget': '.FWidget',
    'AcondaWidget': '.FWidget',
    'AnsiTextEdit': '.FWidget',
    # FCell 模块中的类
    'ImageCellBase': '.FCell',
    'ImageCell': '.FCell',
    # FTabel 模块中的类
    'TableBase': '.FTabel',
    'TableCell': '.FTabel',
    'TableRow': '.FTabel',
}


def __getattr__(name):
    """延迟导入内部模块或类"""
    if name not in __all__:
        raise AttributeError(f"模块 'Fun.QtWidget' 没有属性 '{name}'")
    try:
        # 使用importlib动态导入模块
        module = importlib.import_module(f'{_MODULE_MAP[name]}', package=__name__)
        return getattr(module, name)  # 从模块中获取指定的类或对象
    except ImportError as e:
        raise e
    raise AttributeError(f"无法导入模块 'Fun.QtWidget.{name}'")


def get_exist_dir(caption: str = '选择文件夹', dir_path: str = Get.run_dir()) -> str:
    """
    用于选择单个目录,外部调用时需要用lambda :方法

    :param caption:窗口标题
    :param dir_path:初始目录,默认为文件启动路径
    :return dir:str
    """
    dir = QFileDialog.getExistingDirectory(parent=None,  # 父对象
                                           caption=caption,  # 对话框标题提示词
                                           dir=dir_path,  # 默认显示目录
                                           options=QFileDialog.ShowDirsOnly  # 只显示文件夹
                                           )
    return dir


def get_exist_files(caption: str = '', dir_path: str = Get.run_dir(), ext=None) -> list[str]:
    """
    用于选择单个文件,外部调用时需要用lambda :方法
    :param caption:窗口标题
    :param dir_path:初始目录,默认为文件启动路径
    :param ext:设置文件的扩展名
    :return file:list[str]
    """
    # ext="视频(*.mp4;*.wmv;*.flv;*.avi);;文本(*.txt);;All file(*)"
    file, _ = QFileDialog.getOpenFileNames(None,  # 父对象
                                           caption,  # 窗口标题
                                           dir_path,  # 默认启动路径
                                           ext  # 选择格式
                                           )
    return file


from qfluentwidgets.components.widgets import (
    InfoBarIcon, InfoBar, InfoBarPosition, TeachingTip, TeachingTipTailPosition,  # 气泡消息
)
from PySide6.QtCore import Qt


# 气泡提示装饰器,被装饰函数需要返回bool,content,parent
def info_bar_decorator(func):
    def wrapper(*args, **kwargs):
        # 调用被装饰的函数，并获取返回值
        result, content, parent = func(*args, **kwargs)
        icon = InfoBarIcon.SUCCESS if result else InfoBarIcon.ERROR
        title = '成功' if result else '失败'
        InfoBar.new(
            icon=icon, title=title, content=content, orient=Qt.Horizontal,
            isClosable=True, position=InfoBarPosition.TOP,
            duration=1500, parent=parent)
        return result, title, content  # 必须返回被装饰函数的结果

    return wrapper  # 返回包装后的函数


# 信息提示装饰器,被装饰函数需要返回bool,content,target,parent
def teaching_tip_decorator(func):
    def wrapper(*args, **kwargs):
        # 调用被装饰的函数，并获取返回值
        result, content, target, parent = func(*args, **kwargs)
        icon = InfoBarIcon.SUCCESS if result else InfoBarIcon.ERROR
        title = '成功' if result else '失败'
        TeachingTip.create(
            target=target, icon=icon, title=title, content=content,
            isClosable=True, duration=1500, parent=parent,
            tailPosition=TeachingTipTailPosition.BOTTOM)
        return result, title, content, target, parent  # 必须返回被装饰函数的结果

    return wrapper  # 返回包装后的函数
