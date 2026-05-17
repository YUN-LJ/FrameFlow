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


class ReuseTimer_old:
    """PySide6 QTimer 风格的定时器"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"

    def __init__(self, interval: float, func: Callable, *args, **kwargs):
        """
        :param interval: 间隔时间（秒）
        :param func: 执行函数
        :param args: 执行函数需要的位置参数
        :param kwargs: 执行函数需要的关键字参数
        """
        self._interval = interval  # 间隔时间（秒）
        self.func = func
        self.args = args
        self.kwargs = kwargs

        # 定时器属性
        self._single_shot = False

        # 状态管理
        self._state = self.IDLE
        self._state_lock = threading.RLock()

        # 线程控制
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()

    @property
    def isActive(self) -> bool:
        """是否处于活动状态"""
        with self._state_lock:
            return self._state in (self.RUNNING, self.PAUSED)

    @property
    def isPause(self) -> bool:
        """是否处于暂停状态"""
        return self._state == self.PAUSED

    @property
    def isRunning(self) -> bool:
        """是否处于运行状态"""
        return self._state == self.RUNNING

    @property
    def isIdle(self) -> bool:
        """是否处于空闲状态"""
        return self._state == self.IDLE

    @property
    def state(self) -> str:
        """获取当前状态"""
        return self._state

    def setInterval(self, interval: float):
        """设置间隔时间（秒）"""
        with self._state_lock:
            self._interval = interval

    def setSingleShot(self, single_shot: bool):
        """设置是否为单次执行"""
        with self._state_lock:
            self._single_shot = single_shot

    def _worker(self):
        """工作线程"""
        while not self._stop_event.is_set():
            # 检查是否暂停
            while self._pause_event.is_set() and not self._stop_event.is_set():
                time.sleep(0.01)  # 小幅休眠避免CPU占用

            # 检查是否停止
            if self._stop_event.is_set():
                break

            # 等待指定的时间间隔或直到被停止/暂停
            sleep_time = 0.01
            total_slept = 0
            while total_slept < self._interval and not self._stop_event.is_set():
                if self._pause_event.is_set():
                    # 当进入暂停状态时，等待暂停结束
                    while self._pause_event.is_set() and not self._stop_event.is_set():
                        time.sleep(0.01)
                    if self._stop_event.is_set():
                        break
                time.sleep(sleep_time)
                total_slept += sleep_time

            # 检查是否在等待期间被停止或暂停
            if self._stop_event.is_set():
                break
            if self._pause_event.is_set():
                continue

            # 执行回调函数
            self.func(*self.args, **self.kwargs)

            # 如果是单次执行，则退出循环
            if self._single_shot:
                break

        # 重置状态
        with self._state_lock:
            self._state = self.IDLE

    def start(self, interval: float = None):
        """
        启动定时器
        :param interval: 可选的间隔时间（秒），如果不提供则使用之前设置的值
        """
        with self._state_lock:
            if self._state in (self.RUNNING, self.PAUSED):
                self.stop()

            if interval is not None:
                self._interval = interval

            self._state = self.RUNNING
            self._stop_event.clear()
            self._pause_event.clear()

            # 创建并启动工作线程
            self._thread = threading.Thread(target=self._worker, daemon=True)
            self._thread.start()

    def stop(self):
        """停止定时器"""
        with self._state_lock:
            if self._state == self.IDLE:
                return

            self._state = self.IDLE
            self._stop_event.set()
            self._pause_event.clear()

        # 等待线程结束
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
            self._stop_event.clear()

    def pause(self):
        """暂停定时器"""
        with self._state_lock:
            if self._state == self.RUNNING:
                self._state = self.PAUSED
                self._pause_event.set()
            elif self._state == self.PAUSED:
                self.resume()

    def resume(self):
        """恢复定时器"""
        with self._state_lock:
            if self._state == self.PAUSED:
                self._state = self.RUNNING
                self._pause_event.clear()


class ReuseTimer:
    """PySide6 QTimer 风格的定时器"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"

    def __init__(self, interval: float, func: Callable, *args, **kwargs):
        """
        :param interval: 间隔时间（秒）
        :param func: 执行函数
        :param args: 执行函数需要的位置参数
        :param kwargs: 执行函数需要的关键字参数
        """
        self._interval = interval
        self.func = func
        self.args = args
        self.kwargs = kwargs

        # 定时器属性
        self._single_shot = False

        # 状态管理
        self._state = self.IDLE
        self._state_lock = threading.RLock()

        # Timer对象
        self._timer: Optional[threading.Timer] = None

    @property
    def isActive(self) -> bool:
        """是否处于活动状态"""
        with self._state_lock:
            return self._state in (self.RUNNING, self.PAUSED)

    @property
    def isPause(self) -> bool:
        """是否处于暂停状态"""
        return self._state == self.PAUSED

    @property
    def isRunning(self) -> bool:
        """是否处于运行状态"""
        return self._state == self.RUNNING

    @property
    def isIdle(self) -> bool:
        """是否处于空闲状态"""
        return self._state == self.IDLE

    @property
    def state(self) -> str:
        """获取当前状态"""
        return self._state

    def setInterval(self, interval: float):
        """设置间隔时间（秒）"""
        with self._state_lock:
            self._interval = interval

    def setSingleShot(self, single_shot: bool):
        """设置是否为单次执行"""
        with self._state_lock:
            self._single_shot = single_shot

    def _execute_callback(self):
        """执行回调并安排下一次执行"""
        with self._state_lock:
            if self._state != self.RUNNING:
                return

            # 执行回调函数
            self.func(*self.args, **self.kwargs)

            # 如果不是单次执行，安排下一次执行
            if not self._single_shot and self._state == self.RUNNING:
                self._timer = threading.Timer(self._interval, self._execute_callback)
                self._timer.daemon = True
                self._timer.start()
            else:
                self._state = self.IDLE

    def start(self, interval: float = None):
        """
        启动定时器
        :param interval: 可选的间隔时间（秒），如果不提供则使用之前设置的值
        """
        with self._state_lock:
            # 如果已经在运行，忽略本次调用（实现防抖效果）
            if self._state == self.RUNNING:
                return

            # 如果处于暂停状态，执行恢复操作
            if self._state == self.PAUSED:
                self._state = self.RUNNING
                self._timer = threading.Timer(self._interval, self._execute_callback)
                self._timer.daemon = True
                self._timer.start()
                return

            # 只有在IDLE状态才启动新定时器
            if interval is not None:
                self._interval = interval

            self._state = self.RUNNING

            # 创建并启动Timer
            self._timer = threading.Timer(self._interval, self._execute_callback)
            self._timer.daemon = True
            self._timer.start()

    def stop(self):
        """停止定时器"""
        with self._state_lock:
            if self._state == self.IDLE:
                return

            self._state = self.IDLE

            # 取消Timer
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None

    def pause(self):
        """暂停定时器"""
        with self._state_lock:
            if self._state == self.RUNNING:
                self._state = self.PAUSED
                # 取消当前Timer
                if self._timer is not None:
                    self._timer.cancel()
                    self._timer = None
            elif self._state == self.PAUSED:
                self.resume()

    def resume(self):
        """恢复定时器"""
        with self._state_lock:
            if self._state == self.PAUSED:
                self._state = self.RUNNING
                # 重新启动Timer
                self._timer = threading.Timer(self._interval, self._execute_callback)
                self._timer.daemon = True
                self._timer.start()
