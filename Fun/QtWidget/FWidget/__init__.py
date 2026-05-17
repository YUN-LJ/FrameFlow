from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .SubWidget import *
    from .LoadDialog import *
    from .ImageClass import *
    from .MainWidget import *
    from .TerminalClass import *
    from .CombinationWidget import *

__all__ = [
    # 含函数的模块
    'MainWidget',
    # MainWidget.py 中的类
    'LazyLoadMS', 'SubWidgetBase', 'LoadSubWidget', 'TopWidget', 'TrayIcon',
    # SubWidget.py 中的类
    'WindowDesktop', 'FluentWidgetBase', 'FluentWidgetFromUI', 'SplitterWidget', 
    'SidebarWidgetCover', 'SidebarWidget',
    # TerminalClass.py 中的类
    'AnsiTextEdit', 'EmbeddedWindows', 'EmbeddedPythonTerminal', 'TerminalWidget', 'AcondaWidget',
    # ImageClass.py 中的类
    'ImageManager', 'FullScreenManager', 'ImageWidget',
    # LoadDialog.py 中的类
    'LoadDialogBase', 'LoadRingDialog', 'LoadBarDialog',
    # CombinationWidget.py 中的类
    'CombinationIndeterminateProgressRing', 'CombinationProgressRing', 'ProgressRingButton',
]

import importlib

# 模块名与模块路径的映射字典
_MODULE_MAP = {
    # 含函数的模块
    'MainWidget': '.MainWidget',
    # MainWidget.py 中的类
    'LazyLoadMS': '.MainWidget',
    'SubWidgetBase': '.MainWidget',
    'LoadSubWidget': '.MainWidget',
    'TopWidget': '.MainWidget',
    'TrayIcon': '.MainWidget',
    # SubWidget.py 中的类
    'WindowDesktop': '.SubWidget',
    'FluentWidgetBase': '.SubWidget',
    'FluentWidgetFromUI': '.SubWidget',
    'SplitterWidget': '.SubWidget',
    'SidebarWidgetCover': '.SubWidget',
    'SidebarWidget': '.SubWidget',
    # TerminalClass.py 中的类
    'AnsiTextEdit': '.TerminalClass',
    'EmbeddedWindows': '.TerminalClass',
    'EmbeddedPythonTerminal': '.TerminalClass',
    'TerminalWidget': '.TerminalClass',
    'AcondaWidget': '.TerminalClass',
    # ImageClass.py 中的类
    'ImageManager': '.ImageClass',
    'FullScreenManager': '.ImageClass',
    'ImageWidget': '.ImageClass',
    # LoadDialog.py 中的类
    'LoadDialogBase': '.LoadDialog',
    'LoadRingDialog': '.LoadDialog',
    'LoadBarDialog': '.LoadDialog',
    # CombinationWidget.py 中的类
    'CombinationIndeterminateProgressRing': '.CombinationWidget',
    'CombinationProgressRing': '.CombinationWidget',
    'ProgressRingButton': '.CombinationWidget',
}


def __getattr__(name):
    """延迟导入内部模块或类"""
    if name not in __all__:
        raise AttributeError(f"模块 'Fun.QtWidget.FWidget' 没有属性 '{name}'")
    try:
        # 使用importlib动态导入模块
        module = importlib.import_module(f'{_MODULE_MAP[name]}', package=__name__)
        return getattr(module, name)  # 从模块中获取指定的类或对象
    except ImportError as e:
        raise e
    raise AttributeError(f"无法导入模块 'Fun.QtWidget.FWidget.{name}'")
