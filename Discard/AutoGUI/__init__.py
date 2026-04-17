# 声明对外接口
__all__ = ['check_locked','lock_screen', 'force_lock']  # 明确导出的成员

import importlib

# 模块名与模块路径的映射字典
_MODULE_MAP = {
    'check_locked': '.LockDetect',
    'lock_screen': '.LockGUI',
    'force_lock': '.LockGUI'
}

def __getattr__(name):
    """延迟导入内部模块"""
    if name not in __all__:
        raise AttributeError(f"模块 '{__name__}' 没有属性 '{name}'")
    try:
        # 使用importlib动态导入模块
        module = importlib.import_module(f'{_MODULE_MAP[name]}', package=__name__)
        # 从模块中获取对应的函数
        return getattr(module, name)
    except ImportError as e:
        raise AttributeError(f"无法导入模块 '{_MODULE_MAP[name]}'") from e