"""模型视图,提供模型和展示表格"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .TableData import DataFrameModelBase, DataFrameListBase
    from .TableWidget import DelegateBase, ListDelegateBase, TableWidgetBase, ListWidgetBase

__all__ = [
    'DataFrameModelBase',
    'DelegateBase',
    'ListDelegateBase',
    'TableWidgetBase',
    'ListWidgetBase',
    'DataFrameListBase',
]

_MODULE_MAP = {
    'DataFrameModelBase': '.TableData',
    'DataFrameListBase': '.TableData',
    'DelegateBase': '.TableWidget',
    'ListDelegateBase': '.TableWidget',
    'TableWidgetBase': '.TableWidget',
    'ListWidgetBase': '.TableWidget',
}
import importlib


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
