"""时间操作类"""
import time
import threading
from functools import wraps
from typing import Callable, Optional
from Fun.BaseTools import Tools, LogClass

logger = LogClass.get_logger(__name__, console_level='WARNING')


def now_time(format="%Y-%m-%d-%H-%M-%S"):
    """
    获取当前时间

    :param format:获取时间的格式
    :返回值:格式化时间
    """
    import time
    format_time = time.strftime(format, time.localtime())
    return format_time


def NTP_time(local_time=True) -> float:
    """
    通过NTP获取网络时间,无网络时返回本地时间

    :param local_time:是否允许返回本地时间,默认启用
    :return:返回时间戳
    """
    import ntplib, subprocess, time
    # 检查是否有网络
    response = subprocess.run('ping ntp.tuna.tsinghua.edu.cn -n 1', encoding='utf-8')
    if response.returncode == 0:
        # 网络同步时间,需要管理员权限
        ntp_client = ntplib.NTPClient()
        # 请求网络时间
        response = ntp_client.request('ntp.tuna.tsinghua.edu.cn', timeout=2)
        ntp_timestamp = response.tx_time
        return ntp_timestamp
    else:
        if local_time:
            return time.time()
        return -1.0


def sync_time() -> bool:
    """
    用于将系统时间与NTP网络时间同步
    需要有管理员权限才能设置成功
    """
    import subprocess, time
    ntp_timestamp = NTP_time()
    if not Tools.check_is_admin():
        logger.warning('sync_time:无管理员权限')
        return False
    if ntp_timestamp is not False:
        # 设置本地时间
        local_time = time.localtime(ntp_timestamp)  # 将时间本地化
        format_time = time.strftime("%Y-%m-%d-%H-%M-%S", local_time)  # 格式化时间
        format_time = format_time.split('-')
        set_date = format_time[0] + '-' + format_time[1] + '-' + format_time[2]
        set_time = format_time[3] + ':' + format_time[4] + ':' + format_time[5]
        command = f'date {set_date} && time {set_time}'
        subprocess.run(command, shell=True)
        return True
    else:
        logger.warning('sync_time:没有网络')
        return False


def stamp_to_strf(time_stamp: float, format="%Y-%m-%d-%H-%M-%S") -> str:
    """
    将时间戳转成格式化时间
    """
    import time
    local_time = time.localtime(time_stamp)  # 时间戳对象
    format_time = time.strftime(format, local_time)
    return format_time


# 自定义装饰器返回函数的执行耗时
def timer_decorator(_func=None, *, name=None):
    """
    计时装饰器，可传入自定义名称
    :param _func: 内部参数，用于支持不带括号的装饰器调用
    :param name: 可选，显示的名称，默认为函数名
    
    使用方式：
        @timer_decorator  # 不带括号，使用函数名
        @timer_decorator()  # 带括号但不传参，使用函数名
        @timer_decorator(name="自定义")  # 传入自定义名称
    """

    def decorator(func):
        # 使用 @wraps 保留被装饰函数的元信息（如函数名、文档字符串）
        display_name = name if name is not None else func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            # 装饰器逻辑：执行前记录时间
            start_time = time.time()
            # 调用被装饰的函数，并获取返回值
            result = func(*args, **kwargs)
            # 装饰器逻辑：执行后计算耗时
            end_time = time.time()
            logger.info(f"函数 {display_name} 执行耗时：{end_time - start_time:.4f} 秒")
            return result  # 必须返回被装饰函数的结果

        return wrapper  # 返回包装后的函数

    # 判断是否直接作为装饰器使用（不带括号）
    if _func is not None:
        return decorator(_func)

    return decorator


# class ReuseTimer:
#     """
#     仿照QTimer定时器,支持单次执行和循环执行,默认循环执行
#     start方法支持防抖设计
#     不依赖qt事件循环,内部采用独立线程执行任务
#     """
#     IDLE = "idle"  # 空闲状态,表示定时器未执行或正在等待执行,只有空闲状态下定时器才会执行,其余状态都会导致任务线程终止
#     RUNNING = "running"  # 运行状态,定时器正在执行任务,此时定时器的操作方法全部失效
#     PAUSED = "paused"  # 暂停状态
#     STOPPED = "stopped"  # 停止状态
#
#     def __init__(self, interval: float, func: Callable, name=None, args: tuple = None, kwargs: dict = None):
#         """
#         :param interval: 间隔时间（秒），最小值为0.01秒
#         :param func: 执行函数
#         :param name: 定时器名称
#         :param args: 执行函数需要的位置参数
#         :param kwargs: 执行函数需要的关键字参数
#         """
#         # 确保最小间隔为0.01秒，避免interval=0导致的忙循环
#         self.__interval = max(interval, 0.01)
#         self.__func = func
#         self.name = func.__name__ if name is None else name
#         self.__args = args if args is not None else ()
#         self.__kwargs = kwargs if kwargs is not None else {}
#         # 定时器属性
#         self.__single_shot = False
#         # 状态管理
#         self.__state = self.IDLE
#         self.__pause_requested = False
#         self.__state_lock = threading.Lock()
#         self.__timer_lock = threading.RLock()
#         # Timer对象
#         self.__timer: Optional[threading.Thread] = None
#
#     def _run_thread(self):
#         """启动定时器线程"""
#         with self.__timer_lock:
#             if self.__timer is not None:
#                 return
#             self.__timer = threading.Thread(target=self._execute, name=self.name, daemon=True)
#             self._set_state(self.IDLE)
#             self.__timer.start()
#
#     def _set_state(self, state: str):
#         with self.__state_lock:
#             self.__state = state
#
#     def _execute(self):
#         """
#         执行任务并安排下一次执行
#         执行任务前会将状态改为RUNNING
#         执行完成后会将状态改为IDLE
#         """
#         logger.debug(f"{self.name}定时器线程已启动")
#         while True:
#             # 等待计时器间隔
#             old_interval = self.__interval
#             count = max(int(old_interval / 0.1), 1)
#             for _ in range(count):
#                 if self.__state != self.IDLE or self.__pause_requested:
#                     break
#                 if self.__interval != old_interval:
#                     continue
#                 time.sleep(0.1)
#
#             # 检查是否应该退出循环
#             if self.__state != self.IDLE or self.__pause_requested:
#                 if self.__pause_requested:
#                     self.__state = self.PAUSED
#                     self.__pause_requested = False
#                 break
#
#             # 执行任务函数
#             with self.__state_lock:
#                 try:
#                     self.__state = self.RUNNING
#                     self.__func(*self.__args, **self.__kwargs)
#
#                     if self.__single_shot:
#                         self.__state = self.STOPPED
#                         break
#
#                     # 检查是否有暂停请求
#                     if self.__pause_requested:
#                         self.__state = self.PAUSED
#                         self.__pause_requested = False
#                         break
#
#                     self.__state = self.IDLE
#                 except Exception as e:
#                     logger.exception(f"{self.name}回调函数执行异常: {e}")
#                     break
#
#         with self.__timer_lock:
#             self.__timer = None
#         logger.debug(f"{self.name}定时器线程已结束")
#
#     @property
#     def isPause(self) -> bool:
#         """是否处于暂停状态"""
#         return self.__state == self.PAUSED
#
#     @property
#     def isRunning(self) -> bool:
#         """是否处于运行状态"""
#         return self.__state == self.RUNNING
#
#     @property
#     def isStopped(self) -> bool:
#         """是否处于停止状态"""
#         return self.__state == self.STOPPED
#
#     @property
#     def isIdle(self) -> bool:
#         """是否处于空闲状态"""
#         return self.__state == self.IDLE
#
#     @property
#     def state(self) -> str:
#         """获取当前状态"""
#         return self.__state
#
#     def setInterval(self, interval: float):
#         """设置间隔时间（秒），最小值为0.01秒"""
#         self.__interval = max(interval, 0.01)
#
#     def setSingleShot(self, single_shot: bool):
#         """设置是否为单次执行"""
#         self.__single_shot = single_shot
#
#     def start(self, interval: float = None):
#         """
#         启动定时器，只有空闲、暂停、停止状态下会运行线程
#         :param interval: 可选的间隔时间（秒），如果不提供则使用之前设置的值
#         """
#         if self.isRunning:
#             return
#         elif self.isPause:  # 如果处于暂停状态，执行恢复操作
#             self.resume()
#             return
#         else:
#             if self.__timer is None:
#                 with self.__timer_lock:
#                     if interval is not None:
#                         self.setInterval(interval)
#                     if self.__timer is not None:
#                         self.stop()
#                     self._run_thread()
#
#     def stop(self, timeout=None):
#         """停止定时器"""
#         if not self.isRunning:
#             self._set_state(self.STOPPED)  # 改变状态,定时器线程将会关闭
#             with self.__timer_lock:
#                 if timeout is not None and self.__timer is not None:
#                     self.__timer.join(timeout)
#
#     def pause(self):
#         """暂停定时器"""
#         if not self.isRunning:
#             self._set_state(self.PAUSED)
#         else:
#             # 如果正在运行，设置暂停请求标志
#             self.__pause_requested = True
#
#     def resume(self):
#         """恢复定时器"""
#         if not self.isRunning:
#             self._set_state(self.IDLE)
#             # 恢复运行
#             with self.__timer_lock:
#                 if self.__timer is None:
#                     self._run_thread()
#         else:
#             # 如果正在运行，设置暂停请求标志
#             self.__pause_requested = False


class ReuseTimer:
    """
    仿照QTimer定时器,支持单次执行和循环执行,默认循环执行
    start方法支持防抖设计
    不依赖qt事件循环,内部采用独立线程执行任务
    """
    IDLE = "idle"  # 空闲状态,表示定时器未执行或正在等待执行,只有空闲状态下定时器才会执行,其余状态都会导致任务线程终止
    RUNNING = "running"  # 运行状态,定时器正在执行任务,此时定时器的操作方法全部失效
    PAUSED = "paused"  # 暂停状态
    STOPPED = "stopped"  # 停止状态

    def __init__(self, interval: float, func: Callable, name=None, args: tuple = None, kwargs: dict = None):
        """
        :param interval: 间隔时间（秒），最小值为0.01秒
        :param func: 执行函数
        :param name: 定时器名称
        :param args: 执行函数需要的位置参数
        :param kwargs: 执行函数需要的关键字参数
        """
        # 确保最小间隔为0.01秒，避免interval=0导致的忙循环
        self.__interval = max(interval, 0.01)
        self.__func = func
        self.name = func.__name__ if name is None else name
        self.__args = args if args is not None else ()
        self.__kwargs = kwargs if kwargs is not None else {}

        # 定时器属性
        self.__single_shot = False

        # 线程控制事件
        self.__stop_event = threading.Event()
        self.__pause_event = threading.Event()

        # 状态管理
        self.__state = self.IDLE
        self.__state_lock = threading.RLock()

        # Timer对象
        self.__timer: Optional[threading.Thread] = None
        self.__timer_lock = threading.RLock()

        # 防抖相关
        self.__last_start_time: float = 0
        self.__debounce_timer: Optional[threading.Timer] = None
        self.__debounce_lock = threading.Lock()

    def _set_state(self, state: str):
        """设置状态（内部方法）"""
        with self.__state_lock:
            if self.__state != state:
                logger.debug(f"{self.name}: State change: {self.__state} -> {state}")
                self.__state = state

    def _run_thread(self):
        """启动定时器线程"""
        with self.__timer_lock:
            if self.__timer is not None and self.__timer.is_alive():
                return

            # 重置事件
            self.__stop_event.clear()
            self.__pause_event.clear()

            # 启动新线程
            self.__timer = threading.Thread(target=self._execute, name=self.name, daemon=True)
            self._set_state(self.IDLE)
            self.__timer.start()

    def _wait_interval(self) -> bool:
        """
        精确等待间隔时间
        :return: True-继续执行，False-应退出循环
        """
        start_time = time.monotonic()
        interval = self.__interval

        while not self.__stop_event.is_set():
            # 检查暂停
            if self.__pause_event.is_set():
                return False

            elapsed = time.monotonic() - start_time
            remaining = interval - elapsed

            if remaining <= 0:
                return True

            # 分段等待，以便及时响应停止/暂停信号
            wait_time = min(remaining, 0.05)
            time.sleep(wait_time)

        return False

    def _execute(self):
        """
        执行任务并安排下一次执行
        执行任务前会将状态改为RUNNING
        执行完成后会将状态改为IDLE
        """
        logger.debug(f"{self.name}定时器线程已启动")

        while not self.__stop_event.is_set():
            # 处理暂停状态
            if self.__pause_event.is_set():
                time.sleep(0.05)
                continue

            # 等待计时器间隔
            if not self._wait_interval():
                continue

            # 检查是否应该在执行前退出
            if self.__stop_event.is_set() or self.__pause_event.is_set():
                continue

            # 执行任务函数
            try:
                self._set_state(self.RUNNING)
                self.__func(*self.__args, **self.__kwargs)

                # 单次执行处理
                if self.__single_shot:
                    logger.debug(f"{self.name}: Single shot completed")
                    self._set_state(self.STOPPED)
                    break

                # 检查是否有暂停请求
                if self.__pause_event.is_set():
                    self._set_state(self.PAUSED)
                    continue

                self._set_state(self.IDLE)

            except Exception as e:
                logger.exception(f"{self.name}回调函数执行异常: {e}")
                self._set_state(self.STOPPED)
                break

        # 清理资源
        with self.__timer_lock:
            self.__timer = None
            self.__stop_event.clear()
            # 如果不是停止状态，设置为空闲
            if self.__state != self.STOPPED:
                self._set_state(self.IDLE)

        logger.debug(f"{self.name}定时器线程已结束")

    @property
    def isPause(self) -> bool:
        """是否处于暂停状态"""
        return self.__state == self.PAUSED

    @property
    def isRunning(self) -> bool:
        """是否处于运行状态"""
        return self.__state == self.RUNNING

    @property
    def isStopped(self) -> bool:
        """是否处于停止状态"""
        return self.__state == self.STOPPED

    @property
    def isIdle(self) -> bool:
        """是否处于空闲状态"""
        return self.__state == self.IDLE

    @property
    def state(self) -> str:
        """获取当前状态"""
        return self.__state

    def setInterval(self, interval: float):
        """设置间隔时间（秒），最小值为0.01秒"""
        self.__interval = max(interval, 0.01)

    def setSingleShot(self, single_shot: bool):
        """设置是否为单次执行"""
        with self.__state_lock:
            if self.__state == self.RUNNING:
                logger.warning(f"{self.name}: Cannot change single_shot while running")
                return
            self.__single_shot = single_shot

    def _do_start(self, interval: float = None):
        """实际执行启动逻辑"""
        # 防抖检查
        current_time = time.monotonic()
        if current_time - self.__last_start_time < 0.05:  # 50ms防抖
            logger.debug(f"{self.name}: Debounced repeated start")
            return

        self.__last_start_time = current_time

        # 更新间隔
        if interval is not None:
            self.setInterval(interval)

        # 根据状态执行操作
        if self.isRunning:
            return
        elif self.isPause:
            self.resume()
            return
        else:
            # 停止状态或空闲状态
            if self.__timer is None or not self.__timer.is_alive():
                with self.__timer_lock:
                    if self.__timer is None or not self.__timer.is_alive():
                        self._run_thread()

    def start(self, interval: float = None):
        """
        启动定时器，只有空闲、暂停、停止状态下会运行线程
        :param interval: 可选的间隔时间（秒），如果不提供则使用之前设置的值
        """
        # 取消防抖定时器
        with self.__debounce_lock:
            if self.__debounce_timer is not None:
                self.__debounce_timer.cancel()

            # 创建新的防抖定时器
            self.__debounce_timer = threading.Timer(0.05, self._do_start, args=[interval])
            self.__debounce_timer.daemon = True
            self.__debounce_timer.start()

    def stop(self, timeout=None):
        """停止定时器"""
        # 取消防抖定时器
        with self.__debounce_lock:
            if self.__debounce_timer is not None:
                self.__debounce_timer.cancel()
                self.__debounce_timer = None

        # 设置停止信号
        self.__stop_event.set()
        self.__pause_event.clear()
        self._set_state(self.STOPPED)

        # 等待线程结束
        with self.__timer_lock:
            if timeout is not None and self.__timer is not None:
                self.__timer.join(timeout)

    def pause(self):
        """暂停定时器"""
        if not self.isRunning:
            self._set_state(self.PAUSED)
        else:
            # 如果正在运行，设置暂停事件
            self.__pause_event.set()

    def resume(self):
        """恢复定时器"""
        if not self.isRunning:
            # 清除暂停事件
            self.__pause_event.clear()
            self._set_state(self.IDLE)

            # 恢复运行
            with self.__timer_lock:
                if self.__timer is None or not self.__timer.is_alive():
                    self._run_thread()
        else:
            # 如果正在运行，清除暂停请求
            self.__pause_event.clear()
