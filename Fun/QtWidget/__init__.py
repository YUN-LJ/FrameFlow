"""Qt组件包"""
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from . import FTabelView, FTabelWidget
    from .FWidget import *
    from .FCell import *
    from .FTabel import *

# 声明对外接口
__all__ = [
    # 模块(由于该模块中有函数才导出)
    'MainWidget', 'FTabelView', 'FTabelWidget',
    # FWidget 模块中的类
    'ImageWidget', 'LazyLoadMS', 'TrayIcon', 'EmbeddedWindows', 'EmbeddedPythonTerminal',
    'WindowDesktop', 'FluentWidgetBase', 'TerminalWidget', 'AcondaWidget', 'AnsiTextEdit',
    'LoadBarDialog', 'LoadRingDialog', 'SidebarWidget', 'SubWidget', 'TopWidget',
    'FluentWidgetFromUI', 'SidebarWidgetCover', 'SplitterWidget', 'ProgressRingButton',
    # FCell 模块中的类
    'ImageCellBase', 'ImageCell',
    # FTabel 模块中的类
    'TableBase', 'TableCell', 'TableRow', 'TableDataCell', 'TableDataBase',
]

import importlib

# 模块名与模块路径的映射字典
_MODULE_MAP = {
    # 含函数的模块
    'MainWidget': '.FWidget',
    'FTabelView': '.',
    'FTabelWidget': '.',
    # FWidget 模块中的类
    'LazyLoadMS': '.FWidget',
    'SubWidgetBase': '.FWidget',
    'LoadSubWidget': '.FWidget',
    'TopWidget': '.FWidget',
    'TrayIcon': '.FWidget',
    'WindowDesktop': '.FWidget',
    'FluentWidgetBase': '.FWidget',
    'FluentWidgetFromUI': '.FWidget',
    'SplitterWidget': '.FWidget',
    'SidebarWidgetCover': '.FWidget',
    'SidebarWidget': '.FWidget',
    'AnsiTextEdit': '.FWidget',
    'EmbeddedWindows': '.FWidget',
    'EmbeddedPythonTerminal': '.FWidget',
    'TerminalWidget': '.FWidget',
    'AcondaWidget': '.FWidget',
    'ImageManager': '.FWidget',
    'FullScreenManager': '.FWidget',
    'ImageWidget': '.FWidget',
    'LoadDialogBase': '.FWidget',
    'LoadRingDialog': '.FWidget',
    'LoadBarDialog': '.FWidget',
    'CombinationIndeterminateProgressRing': '.FWidget',
    'CombinationProgressRing': '.FWidget',
    'ProgressRingButton': '.FWidget',
    # FCell 模块中的类
    'ImageCellBase': '.FCell',
    'ImageCell': '.FCell',
    # FTabel 模块中的类
    'TableBase': '.FTabel',
    'TableCell': '.FTabel',
    'TableRow': '.FTabel',
    'TableDataCell': '.FTabel',
    'TableDataBase': '.FTabel',
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


# ---函数部分---
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import Qt, QTimer, QObject, Signal, QMutex, QMutexLocker
from qfluentwidgets.components.widgets import (
    InfoBarIcon, InfoBar, InfoBarPosition, TeachingTip, TeachingTipTailPosition,  # 气泡消息
)
from functools import wraps
from weakref import WeakKeyDictionary
from Fun.BaseTools import Get, check_function_needs_args
from Fun.BaseTools.Time import ReuseTimer


def get_exist_dir(caption: str = None, dir_path: str = None) -> str:
    """
    用于选择单个目录
    :param caption:窗口标题
    :param dir_path:初始目录,默认为文件启动路径
    :return dir:str
    """
    caption = '选择文件夹' if caption is None else caption
    dir_path = Get.run_dir() if dir_path is None else dir_path
    dir = QFileDialog.getExistingDirectory(parent=None,  # 父对象
                                           caption=caption,  # 对话框标题提示词
                                           dir=dir_path,  # 默认显示目录
                                           options=QFileDialog.ShowDirsOnly  # 只显示文件夹
                                           )
    return dir


def get_exist_files(caption: str = None, dir_path: str = None, ext=None) -> list[str]:
    """
    用于选择单个文件
    :param caption:窗口标题
    :param dir_path:初始目录,默认为文件启动路径
    :param ext:设置文件的扩展名,如ext="视频(*.mp4;*.wmv;*.flv;*.avi);;文本(*.txt);;All file(*)"
    :return file:list[str]
    """
    caption = '选择文件' if caption is None else caption
    dir_path = Get.run_dir() if dir_path is None else dir_path
    file, _ = QFileDialog.getOpenFileNames(None,  # 父对象
                                           caption,  # 窗口标题
                                           dir_path,  # 默认启动路径
                                           ext  # 选择格式
                                           )
    return file


# 气泡提示装饰器,被装饰函数需要返回bool,content,parent
def info_bar_decorator(func):
    """气泡提示装饰器,被装饰函数需要返回bool|None,content,parent"""

    def wrapper(*args, **kwargs):
        func_result = None  # 初始化变量
        # 调用被装饰的函数，并获取返回值
        try:
            args_num = check_function_needs_args(func, False)
            if args_num == 0:  # 没有参数
                func_result = func()
            elif args_num == 1:  # 有一个参数,只传递一个参数,可能是函数的self参数
                func_result = func(args[0])
            else:  # 有多个参数
                func_result = func(*args, **kwargs)
            result, content, parent = func_result
        except Exception as e:
            print(f"info_bar_decorator:被装饰的函数执行错误: {e}")
            return None, None, None
        if result is None:
            return None, None, None
        icon = InfoBarIcon.SUCCESS if result else InfoBarIcon.ERROR
        title = '成功' if result else '失败'
        if parent.isVisible():
            QTimer.singleShot(0, lambda: InfoBar.new(
                icon=icon, title=title, content=content, orient=Qt.Horizontal,
                isClosable=True, position=InfoBarPosition.TOP,
                duration=1500, parent=parent))

        return result, title, content  # 必须返回被装饰函数的结果

    return wrapper  # 返回包装后的函数


# 信息提示装饰器,被装饰函数需要返回bool|None,content,target,parent
def teaching_tip_decorator(func):
    """信息提示装饰器,被装饰函数需要返回bool,content,target,parent"""

    def wrapper(*args, **kwargs):
        func_result = None  # 初始化变量
        # 调用被装饰的函数，并获取返回值
        try:
            args_num = check_function_needs_args(func, False)
            if args_num == 0:  # 没有参数
                func_result = func()
            elif args_num == 1:  # 有一个必填参数,只传递一个参数,可能是函数的self参数
                func_result = func(args[0])
            else:  # 有多个参数
                func_result = func(*args, **kwargs)
            result, content, target, parent = func_result
        except Exception as e:
            print(f"teaching_tip_decorator:被装饰的函数执行错误: {e}")
            return None, None, None, None
        if result is None:
            return None, None, None, None
        icon = InfoBarIcon.SUCCESS if result else InfoBarIcon.ERROR
        title = '成功' if result else '失败'
        if target.isVisible() and parent.isVisible():
            TeachingTip.create(
                target=target, icon=icon, title=title, content=content,
                isClosable=True, duration=1500, parent=parent,
                tailPosition=TeachingTipTailPosition.BOTTOM)
        return result, title, content, target, parent  # 必须返回被装饰函数的结果

    return wrapper  # 返回包装后的函数


def debouncer_timer(func) -> QTimer:
    """防抖器,依赖QT事件循环"""
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(func)
    return timer


def debouncer_reuse_timer(func) -> ReuseTimer:
    """防抖器,不依赖QT事件循环"""
    timer = ReuseTimer(0, func)
    timer.setSingleShot(True)
    return timer


def throttle_reuse_timer_decorator(timeout: float = 0.05):
    """
    节流函数装饰器（基于 ReuseTimer，不依赖 Qt 事件循环）
    
    Args:
        timeout: 节流时间间隔（秒），默认 0.05 秒（50ms）
    
    Example:
        @throttle_decorator(timeout=0.1)
        def handle_scroll(value):
            update_viewport(value)
        
        # 多次快速调用，只会执行最后一次
        handle_scroll(1)
        handle_scroll(2)
        handle_scroll(3)
        # 0.1秒后执行: handle_scroll(3)
    
    Note:
        - 适用于普通函数和类方法
        - 不依赖 Qt 事件循环，性能更好
        - 每个实例有独立的定时器，状态隔离
    """

    def decorator(func):
        # 使用弱引用字典存储每个实例的节流助手，避免内存泄漏
        helpers = WeakKeyDictionary()

        def wrapper(*args, **kwargs):
            # 判断是否是类方法（第一个参数是 self）
            if args and hasattr(args[0], '__dict__'):
                instance = args[0]

                # 获取或创建当前实例的节流助手
                if instance not in helpers:
                    helpers[instance] = _ThrottleHelper(func, timeout)

                helpers[instance].trigger(*args, **kwargs)
            else:
                # 普通函数，使用模块级别的助手
                if '_module_helper' not in wrapper.__dict__:
                    wrapper._module_helper = _ThrottleHelper(func, timeout)

                wrapper._module_helper.trigger(*args, **kwargs)

        # 保留原函数的元信息
        wrapper = wraps(func)(wrapper)

        return wrapper

    return decorator


class _ThrottleHelper:
    """轻量级节流助手（基于 ReuseTimer）"""

    def __init__(self, func, timeout: float):
        self.func = func
        self.timeout = timeout
        self._pending = False
        self._last_args = None
        self._last_kwargs = None

        # 使用 ReuseTimer，不依赖 Qt 事件循环
        self._timer = ReuseTimer(timeout, self._execute)
        self._timer.setSingleShot(True)

    def trigger(self, *args, **kwargs):
        """触发节流调用"""
        # 保存最新的参数
        self._last_args = args
        self._last_kwargs = kwargs

        # 如果不在等待状态，启动定时器
        if not self._pending:
            self._pending = True
            self._timer.start()

    def _execute(self):
        """定时器超时，执行原函数"""
        self._pending = False

        args = self._last_args
        kwargs = self._last_kwargs
        self._last_args = None
        self._last_kwargs = None

        # 执行原函数
        try:
            if args or kwargs:
                self.func(*args, **kwargs)
            else:
                self.func()
        except Exception as e:
            print(f"节流函数执行错误: {e}")


class _QTimerThrottleHelper(QObject):
    """QTimer 节流助手（依赖 Qt 事件循环）"""

    def __init__(self, func, timeout: int, parent=None):
        super().__init__(parent)
        self.func = func
        self.timeout = timeout
        self._pending = False
        self._last_args = None
        self._last_kwargs = None

        # 使用 QTimer，依赖 Qt 事件循环
        self._timer = QTimer(self)  # ✅ 设置 parent，确保生命周期管理
        self._timer.setSingleShot(True)
        self._timer.setInterval(timeout)
        self._timer.timeout.connect(self._execute)

    def trigger(self, *args, **kwargs):
        """触发节流调用"""
        # 保存最新的参数
        self._last_args = args
        self._last_kwargs = kwargs

        # 如果不在等待状态，启动定时器
        if not self._pending:
            self._pending = True
            self._timer.start()

    def _execute(self):
        """定时器超时，执行原函数"""
        self._pending = False

        args = self._last_args
        kwargs = self._last_kwargs
        self._last_args = None
        self._last_kwargs = None

        # 执行原函数
        try:
            if args or kwargs:
                self.func(*args, **kwargs)
            else:
                self.func()
        except Exception as e:
            print(f"节流函数执行错误: {e}")


def throttle_qtimer_decorator(timeout: int = 50):
    """
    节流函数装饰器（基于 QTimer，依赖 Qt 事件循环）

    Args:
        timeout: 节流时间间隔（毫秒），默认 50ms

    Example:
        @throttle_qtimer_decorator(timeout=100)
        def update_ui(value):
            progressBar.setValue(value)

        # 多次快速调用，只会执行最后一次
        update_ui(1)
        update_ui(2)
        update_ui(3)
        # 100ms后执行: update_ui(3)

    Note:
        - 适用于普通函数和类方法
        - 依赖 Qt 事件循环，适合 UI 更新操作
        - 每个实例有独立的定时器，状态隔离
        - 可以直接在槽函数中更新 UI，无需信号中转
    """
    from weakref import WeakKeyDictionary

    def decorator(func):
        # 使用弱引用字典存储每个实例的节流助手，避免内存泄漏
        helpers = WeakKeyDictionary()

        def wrapper(*args, **kwargs):
            # 判断是否是类方法（第一个参数是 self）
            if args and hasattr(args[0], '__dict__'):
                instance = args[0]

                # 获取或创建当前实例的节流助手
                if instance not in helpers:
                    # ✅ 传入 instance 作为 parent，确保生命周期绑定
                    helpers[instance] = _QTimerThrottleHelper(func, timeout, parent=instance)

                helpers[instance].trigger(*args, **kwargs)
            else:
                # 普通函数，使用模块级别的助手
                if '_module_helper' not in wrapper.__dict__:
                    wrapper._module_helper = _QTimerThrottleHelper(func, timeout)

                wrapper._module_helper.trigger(*args, **kwargs)

        # 保留原函数的元信息
        from functools import wraps
        wrapper = wraps(func)(wrapper)

        return wrapper

    return decorator
