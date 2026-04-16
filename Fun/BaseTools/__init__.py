"""常用工具包"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # 模块
    from . import File, Get, Image, Str, Terminal, Time, Tools
    # File 模块中的类
    from .File import FileBase, ImageFileBase, EasyConfig
    # Image 模块中的类
    from .Image import ImageProcess, ImageLoad, ImageEnum
    # Time 模块中的类
    from .Time import ReuseTimer
    # Terminal 模块中的类
    from .Terminal import CreateTerminal, CapturePythonTerminal

# 声明对外接口
__all__ = [
    # 模块
    'File', 'Get', 'Image', 'Str', 'Terminal', 'Time', 'Tools',
    # File 模块中的类
    'FileBase', 'ImageFileBase', 'EasyConfig',
    # Image 模块中的类
    'ImageProcess', 'ImageLoad', 'ImageEnum',
    # Time 模块中的类
    'ReuseTimer',
    # Terminal 模块中的类
    'CreateTerminal', 'CapturePythonTerminal'
]

import importlib

# 模块名与模块路径的映射字典
_MODULE_MAP = {
    # 模块直接导入
    'File': '.File',
    'Get': '.Get',
    'Image': '.Image',
    'Str': '.Str',
    'Terminal': '.Terminal',
    'Time': '.Time',
    'Tools': '.Tools',
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
