"""
后端文件
功能模块内部实现UI和API接口
涉及到可能会大量实例化的QObject对象或临时弹窗类等
需要重写deleteLater方法来清理资源
并在不需要用时显式调用,防止内存溢出

启动:
    调用start_desktop
    ...
    未来新增了其它版本的UI调用不同方法即可

多进程问题:
    当前包DataManage的常量只在主进程下自动实例化
    当前包WallHaven的常量只在主进程下自动加载配置
    当前包WallPaper的常量只在主进程下自动加载配置
    使用多进程池任务时,所有所需的参数必须再主线程中
    直接传递给模块级函数,函数内不要使用任何全局变量
"""
from Fun.BaseTools import LogClass

logger = LogClass.get_logger(__name__, console_level='WARNING')


def global_value_init():
    from SubAPI.Settings import GlobalValue
    from Fun.BaseTools import TaskManage, TaskProcessManage, AsyncHTTPManage, TaskAsyncManage
    if GlobalValue.GLOBAL_TASK_ASYNC_MANAGE is None:
        GlobalValue.GLOBAL_TASK_ASYNC_MANAGE = TaskAsyncManage(50)
    if GlobalValue.GLOBAL_TASK_MANAGE is None:
        GlobalValue.GLOBAL_TASK_MANAGE = TaskManage(10)
    if GlobalValue.GLOBAL_Task_PROCESS_MANAGE is None:
        GlobalValue.GLOBAL_Task_PROCESS_MANAGE = TaskProcessManage(3)
    if GlobalValue.GLOBAL_ASYNC_HTTP_MANAGE is None:
        GlobalValue.GLOBAL_ASYNC_HTTP_MANAGE = AsyncHTTPManage(50, rate_limit=45)


def exit_handler():
    from SubAPI.DataManage import DATA_MANAGE
    from SubAPI.Settings.GlobalValue import (
        GLOBAL_TASK_MANAGE, IMAGE_CACHE_DIR, GLOBAL_ASYNC_HTTP_MANAGE,
        GLOBAL_Task_PROCESS_MANAGE, GLOBAL_TASK_ASYNC_MANAGE,
    )
    from SubAPI.WallHaven.api import save_config as WH_save_config
    from SubAPI.WallPaper.api import save_config as WP_save_config
    from Fun.BaseTools import FileBase, LogManager
    logger.info('执行清理...')
    WH_save_config()  # 保存wallhaven配置
    WP_save_config()  # 保存壁纸配置
    DATA_MANAGE.stop()  # 关闭数据管理
    GLOBAL_TASK_ASYNC_MANAGE.stop()  # 关闭全局异步线程池
    GLOBAL_TASK_MANAGE.stop()  # 关闭全局线程池
    GLOBAL_Task_PROCESS_MANAGE.stop()  # 关闭全局进程池
    GLOBAL_ASYNC_HTTP_MANAGE.stop()  # 关闭全局异步HTTP管理
    cache_dir = FileBase(IMAGE_CACHE_DIR)
    if cache_dir.folder_size() > 50:
        cache_dir.delete()  # 删除缓存文件夹
    logger.info('清理完成,程序已完成退出')
    LogManager().close_all_handlers()


def start_desktop(func):
    """
    启动桌面应用
    :param func:启动函数,需要返回顶层窗口
    """

    from SubAPI.Settings import GlobalValue
    from Fun.QtWidget import MainWidget
    from PySide6.QtWidgets import QApplication, QWidget
    from Fun.BaseTools import FileBase, LogManager
    # ---准备阶段---
    logger.info('准备启动桌面应用...')
    app = QApplication([])
    FileBase(GlobalValue.IMAGE_CACHE_DIR).ensure_exists()
    global_value_init()
    # ---启动阶段---
    win = func()
    if not isinstance(win, QWidget):
        raise TypeError('启动函数返回值必须是QWidget对象')
    GlobalValue.TOP_WINDOWS = win
    MainWidget.change_theme()
    # 设置全模块日志控制台输出级别, 默认为WARNING
    # LogManager().set_console_output(console_level='INFO')
    app.exec()
    # ---清理阶段---
    exit_handler()
