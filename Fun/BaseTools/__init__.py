"""常用工具包"""
import pyperclip, inspect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # 含函数的模块 - 使用 from . import 模块
    from . import File, Get, Image, Str, Terminal, Time, Tools, LogClass
    from .File import *
    from .Get import *
    from .Image import *
    from .Str import *
    from .Terminal import *
    from .Time import *
    from .Tools import *
    from .LogClass import *
    # 只有类的模块 - 使用 from 模块 import *
    from .AsyncHTTP import *
    from .TaskClass import *
    from .TaskOrch import *

# 声明对外接口
__all__ = [
    # 含函数的模块
    'File', 'Get', 'Image', 'Str', 'Terminal', 'Time', 'Tools', 'LogClass',
    # File 模块中的类
    'FileBase', 'ImageFileBase', 'EasyConfig',
    # Image 模块中的类
    'ImageProcess', 'ImageLoad', 'ImageEnum',
    # Time 模块中的类
    'ReuseTimer',
    # Terminal 模块中的类
    'CreateTerminal', 'CapturePythonTerminal',
    # TaskClass 模块中的类
    'TaskManageBase', 'TaskManage', 'TaskProcessManage', 'TaskAsyncManage',
    'Task', 'TaskProgress', 'TaskSignal', 'TaskSignalExecutor',
    'PriorityPoolExecutorBase', 'PriorityThreadPool',
    'PriorityProcessPool', 'PriorityAsyncPool', 'TaskExecutor', 'TaskSignalParams',
    'TaskEnum', 'TaskStateParams',
    # AsyncHTTP 模块中的类
    'AsyncHTTPManage', 'AsyncJson', 'AsyncChunkDownloader',
    # LogClass 模块中的类
    'LogConfig', 'LogManager',
    # TaskOrchestrator模块中的类
    'TaskChain', 'ParallelTaskGroup', 'TaskOrchestrator'
]

import importlib

# 模块名与模块路径的映射字典
_MODULE_MAP = {
    # 含函数的模块
    'File': '.File',
    'Get': '.Get',
    'Image': '.Image',
    'Str': '.Str',
    'Terminal': '.Terminal',
    'Time': '.Time',
    'Tools': '.Tools',
    'LogClass': '.LogClass',
    # File 模块中的类
    'FileBase': '.File',
    'ImageFileBase': '.File',
    'EasyConfig': '.File',
    # Image 模块中的类
    'ImageProcess': '.Image',
    'ImageLoad': '.Image',
    'ImageEnum': '.Image',
    # Time 模块中的类
    'ReuseTimer': '.Time',
    # Terminal 模块中的类
    'CreateTerminal': '.Terminal',
    'CapturePythonTerminal': '.Terminal',
    # TaskClass 模块中的类
    'TaskManageBase': '.TaskClass',
    'TaskManage': '.TaskClass',
    'TaskProcessManage': '.TaskClass',
    'TaskAsyncManage': '.TaskClass',
    'Task': '.TaskClass',
    'TaskProgress': '.TaskClass',
    'TaskSignal': '.TaskClass',
    'TaskSignalExecutor': '.TaskClass',
    'PriorityPoolExecutorBase': '.TaskClass',
    'PriorityThreadPool': '.TaskClass',
    'PriorityProcessPool': '.TaskClass',
    'PriorityAsyncPool': '.TaskClass',
    'TaskExecutor': '.TaskClass',
    'TaskSignalParams': '.TaskClass',
    'TaskEnum': '.TaskClass',
    'TaskStateParams': '.TaskClass',
    # AsyncHTTP 模块中的类
    'AsyncHTTPManage': '.AsyncHTTP',
    'AsyncJson': '.AsyncHTTP',
    'AsyncChunkDownloader': '.AsyncHTTP',
    # LogClass 模块中的类
    'LogConfig': '.LogClass',
    'LogManager': '.LogClass',
    # TaskOrchestrator 模块中的类
    'TaskChain': '.TaskOrch',
    'ParallelTaskGroup': '.TaskOrch',
    'TaskOrchestrator': '.TaskOrch'
}


def __getattr__(name):
    """延迟导入内部模块或类"""
    if name not in __all__:
        raise AttributeError(f"模块 'Fun.BaseTools' 没有属性 '{name}'")
    try:
        # 使用importlib动态导入模块
        module = importlib.import_module(f'{_MODULE_MAP[name]}', package=__name__)
        return getattr(module, name)  # 从模块中获取指定的类或对象
    except ImportError as e:
        raise e
    raise AttributeError(f"无法导入模块 'Fun.BaseTools.{name}'")


def singleton_decorator(cls):
    """单例模式装饰器"""
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def copy_text_to_clipboard(text: str):
    """复制文本到剪贴板"""
    pyperclip.copy(text)


def get_text_from_clipboard() -> str:
    """从剪贴板获取文本"""
    return pyperclip.paste()


def check_function_needs_args(func, exclude_self=True) -> int:
    """
    获取函数的全部参数数量（只排除 *args 和 **kwargs）
    
    :param func: 要检查的函数
    :param exclude_self: 是否排除 self 参数，默认为 True
    :return: 参数数量
    """
    sig = inspect.signature(func)
    params = sig.parameters

    # 统计参数数量（只排除 *args 和 **kwargs）
    all_params = [
        name for name, param in params.items()
        if param.kind not in (
            inspect.Parameter.VAR_POSITIONAL,  # *args
            inspect.Parameter.VAR_KEYWORD  # **kwargs
        )
           and not (exclude_self and name == 'self')  # 根据参数决定是否排除 self
    ]

    return len(all_params)
