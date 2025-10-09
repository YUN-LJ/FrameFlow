# 声明对外接口
__all__ = ['GUI_Qt', 'Norm', 'System','AutoGUI']  # 明确导出的成员

import importlib

# 模块名与模块路径的映射字典（仅需模块名即可，因为都是同级模块）
_MODULE_MAP = {
    'GUI_Qt': '.GUI_Qt',
    'Norm': '.Norm',
    'System': '.System',
    'AutoGUI': '.AutoGUI',
}


def __getattr__(name):
    """延迟导入内部模块"""
    if name not in __all__:
        raise AttributeError(f"模块 'Fun' 没有属性 '{name}'")
    try:
        # 使用importlib动态导入模块
        # 导入格式为：from .模块名 import 模块名
        module = importlib.import_module(f'{_MODULE_MAP[name]}', package=__name__)
        return getattr(module, name)
    except ImportError as e:
        raise e

    raise AttributeError(f"无法导入模块 'Fun.{name}'")
