"""
接口包
功能模块内部实现UI和API接口
涉及到可能会大量实例化的QObject对象或临时弹窗类等
需要重写deleteLater方法来清理资源
并在不需要用时显式调用,防止内存溢出

启动:
    UI与后端进程隔离,采用队列通信,后端API运行在主进程,UI运行在子进程中
    调用start_desktop
    ...
    未来新增了其它版本的UI调用不同方法即可

多进程问题:
    当前包DataManage的常量只在主进程下自动实例化
    当前包WallHaven的常量只在主进程下自动加载配置
    当前包WallPaper的常量只在主进程下自动加载配置
    使用多进程池任务时,直接传递给模块级函数,函数内不要使用任何全局变量
"""
from queue import Empty
from multiprocessing import current_process, Process, Queue, Pipe
from SubAPI.Settings import GlobalValue
from Fun.BaseTools import LogClass, LogManager

logger = LogClass.get_logger(__name__, console_level='INFO')


def client_load_config():
    """客户端加载本地配置"""


def server_event(event, *args, **kwargs):
    """处理服务端事件"""
    if isinstance(event, GlobalValue.WallHavenTaskClassEnum):  # WallHaven包事件
        WHAPI.run_task(event, *args, **kwargs)
    elif isinstance(event, GlobalValue.DataManageGetEnum):
        pass
    else:
        logger.warning(f'server_event 无事件处理{event} 位置参数{args} 关键字参数{kwargs}')


def client_event(event, *args, **kwargs):
    """处理客户端端事件"""
    logger.warning(f'client_event 无事件处理{event} 位置参数{args} 关键字参数{kwargs}')


def global_value_init():
    # 初始化全局任务池
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
    # 初始化数据
    from SubAPI.DataManage import initDataClass
    initDataClass()
    # 加载子类包本地配置数据
    from SubAPI.WallHaven.api import load_config as WH_load_config
    from SubAPI.WallPaper.api import load_config as WP_load_config
    WH_load_config()
    WP_load_config()


def put_queue(queue: Queue, event, *args, **kwargs):
    """提交参数"""
    queue.put((event, args, kwargs))


def exit_handler():
    from SubAPI.DataManage import DATA_MANAGE
    from SubAPI.Settings.GlobalValue import IMAGE_CACHE_DIR
    from SubAPI.WallHaven.api import save_config as WH_save_config
    from SubAPI.WallPaper.api import save_config as WP_save_config
    from Fun.BaseTools import FileBase, LogManager, TaskManageBase
    logger.info('执行清理...')
    WH_save_config()  # 保存wallhaven配置
    WP_save_config()  # 保存壁纸配置
    DATA_MANAGE.stop()  # 关闭数据管理
    GlobalValue.GLOBAL_TASK_MANAGE.stop()
    GlobalValue.GLOBAL_Task_PROCESS_MANAGE.stop()
    GlobalValue.GLOBAL_TASK_ASYNC_MANAGE.stop()
    GlobalValue.GLOBAL_ASYNC_HTTP_MANAGE.stop()
    TaskManageBase.stop_all()
    cache_dir = FileBase(IMAGE_CACHE_DIR)
    if cache_dir.folder_size() > 50:
        cache_dir.delete()  # 删除缓存文件夹
    logger.info('清理完成,程序已完成退出')
    LogManager().close_all_handlers()


def start_desktop(func, client_queue: Queue, server_queue: Queue, console_level='WARNING'):
    """
    启动桌面应用
    :param func:启动函数,需要返回顶层窗口
    :param client_queue:客户端队列,由客户端处理的事件,格式(任务类型枚举值,*args,**kwargs)
    :param server_queue:服务端队列,由服务端处理的事件,格式(任务类型枚举值,*args,**kwargs)
    :param console_level:控制台输出日志级别
    """

    from Fun.QtWidget import MainWidget
    from PySide6.QtWidgets import QApplication, QWidget
    from Fun.BaseTools import FileBase
    # ---准备阶段---
    logger.info('准备启动桌面应用')
    GlobalValue.CLIENT_QUEUE = client_queue
    GlobalValue.SERVER_QUEUE = server_queue
    app = QApplication([])
    FileBase(GlobalValue.IMAGE_CACHE_DIR).ensure_exists()
    # ---启动阶段---
    win = func()
    if not isinstance(win, QWidget):
        raise TypeError('启动函数返回值必须是QWidget对象')
    GlobalValue.TOP_WINDOWS = win
    MainWidget.change_theme()
    # 设置全模块日志控制台输出级别, 默认为WARNING
    LogManager().set_console_output(console_level=console_level)
    app.exec()
    # ---清理阶段---
    logger.info('桌面应用退出')
    put_queue(server_queue, 'exit')


class StartAPI:
    """启动接口"""

    def __init__(self, ui_type='desktop', func=None, console_level='WARNING'):
        """
        启用后端API事件服务
        :param ui_type:ui类型
        :param func:启动函数,默认不启动UI
        :param console_level:控制台输出日志级别
        """
        self.ui_type = ui_type
        self.func = func
        self.console_level = console_level
        self.client_queue = Queue()  # 客户端
        self.server_queue = Queue()  # 服务端
        if ui_type == 'desktop':
            self.process_func = start_desktop
        self.client_process = Process(
            target=self.process_func,
            args=(func, self.client_queue, self.server_queue, console_level)
        )
        # 设置全模块日志控制台输出级别, 默认为WARNING
        LogManager().set_console_output(console_level=console_level)
        GlobalValue.CLIENT_QUEUE = self.client_queue
        GlobalValue.SERVER_QUEUE = self.server_queue

    def start_thread(self):
        """线程模式"""
        self.process_func(self.func, self.client_queue, self.server_queue, self.console_level)
        exit_handler()  # 退出事件

    def start(self):
        """进程隔离模式"""
        self.client_process.start()
        while True:  # 处理服务端事件
            try:
                task_event, args, kwargs = self.server_queue.get(timeout=0.1)
                if task_event == 'exit':
                    break
                server_event(task_event, *args, **kwargs)
            except Empty:
                pass
            except Exception as e:
                logger.exception(f'任务事件处理失败{e}')
        exit_handler()  # 退出事件


# 检测是否为主进程
_is_main_process = current_process().name == 'MainProcess'
if _is_main_process:
    # 初始化全局数据和任务池
    global_value_init()
    # 导入后端包
    from SubAPI.WallHaven import api as WHAPI
