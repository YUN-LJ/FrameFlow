"""时间操作类"""
import threading
import time
from enum import Enum
from typing import Callable, Optional

from Fun.BaseTools import Tools


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
        print('sync_time:无管理员权限')
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
        print('sync_time:没有网络')
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
def timer_decorator(func):
    from functools import wraps
    import time
    # 使用 @wraps 保留被装饰函数的元信息（如函数名、文档字符串）
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 装饰器逻辑：执行前记录时间
        start_time = time.time()
        # 调用被装饰的函数，并获取返回值
        result = func(*args, **kwargs)
        # 装饰器逻辑：执行后计算耗时
        end_time = time.time()
        print(f"函数 {func.__name__} 执行耗时：{end_time - start_time:.4f} 秒")
        return result  # 必须返回被装饰函数的结果

    return wrapper  # 返回包装后的函数


class TimerState(Enum):
    """定时器状态"""
    IDLE = "idle"  # 空闲
    RUNNING = "running"  # 运行中
    PAUSED = "paused"  # 暂停
    STOPPING = "stopping"  # 停止中


class ReuseTimer:
    """可复用定时器（线程复用版）"""

    def __init__(self, interval: float, func: Callable, is_while=True, daemon=True, *args, **kwargs):
        """
        :param interval:间隔时间
        :param func:执行函数
        :param is_while:是否循环执行
        :param daemon:是否为守护线程,默认为守护线程
        :param args: 执行函数需要的位置参数
        :param kwargs: 执行函数需要的关键字参数
        """
        self.interval = interval
        self.func = func
        self.is_while = is_while
        self.daemon = daemon
        self.args = args
        self.kwargs = kwargs

        # 状态管理
        self._state = TimerState.IDLE
        self._state_lock = threading.RLock()
        self._state_changed = threading.Condition(self._state_lock)

        # 时间控制
        self._next_run_time: float = 0
        self._pause_accumulated_time: float = 0  # 累计暂停时间
        self._pause_start_time: float = 0

        # 线程控制
        self._thread: Optional[threading.Thread] = None
        self._wakeup_event = threading.Event()  # 用于唤醒工作线程

    @property
    def isRunning(self) -> bool:
        """是否正在运行"""
        with self._state_lock:
            return self._state in (TimerState.RUNNING, TimerState.PAUSED)

    @property
    def isPause(self) -> bool:
        """是否暂停"""
        with self._state_lock:
            return self._state == TimerState.PAUSED

    def set_is_while(self, is_while: bool):
        with self._state_lock:
            self.is_while = is_while

    def set_daemon(self, daemon: bool):
        with self._state_lock:
            self.daemon = daemon

    def set_interval(self, interval: float):
        with self._state_lock:
            self.interval = interval
            if self._state == TimerState.RUNNING:
                # 如果正在运行，重新调度
                self._next_run_time = time.time() + interval
                self._wakeup_event.set()

    def set_func(self, func: Callable):
        with self._state_lock:
            self.func = func

    def _worker(self):
        """工作线程主循环"""
        while True:
            # 等待状态变为非暂停或退出
            with self._state_changed:
                # 检查是否需要退出
                if self._state == TimerState.STOPPING:
                    break

                # 如果是暂停状态，等待恢复
                while self._state == TimerState.PAUSED:
                    self._state_changed.wait()
                    if self._state == TimerState.STOPPING:
                        break

                if self._state == TimerState.STOPPING:
                    break

                # 计算等待时间
                if self._state == TimerState.RUNNING:
                    wait_time = max(0, self._next_run_time - time.time())
                else:
                    wait_time = None  # 无限等待

                # 等待到达执行时间或状态变化
                if wait_time is not None:
                    self._state_changed.wait(wait_time)
                else:
                    self._state_changed.wait()

                # 再次检查状态
                if self._state == TimerState.STOPPING:
                    break

                if self._state == TimerState.PAUSED:
                    continue

                # 检查是否到达执行时间
                current_time = time.time()
                if self._state == TimerState.RUNNING and current_time >= self._next_run_time:
                    # 执行任务前，先复制任务信息并释放锁
                    func = self.func
                    args = self.args
                    kwargs = self.kwargs
                    is_while = self.is_while

                    # 释放锁执行用户函数
                    self._state_changed.release()
                    try:
                        func(*args, **kwargs)
                    except Exception as e:
                        print(f"定时器任务执行出错: {e}")
                    self._state_changed.acquire()

                    # 执行后处理
                    if self._state == TimerState.RUNNING:
                        if is_while:
                            # 设置下次执行时间
                            self._next_run_time = time.time() + self.interval
                        else:
                            # 单次执行，准备退出
                            self._state = TimerState.STOPPING
                            break

        # 清理状态
        with self._state_lock:
            self._state = TimerState.IDLE
            self._wakeup_event.clear()

    def start(self, time_out=None):
        """
        开始
        :param time_out:多少秒后执行,默认为间隔时间
        """
        with self._state_lock:
            # 如果已经在运行，先停止
            if self._state != TimerState.IDLE:
                self._stop_locked()
                # 等待线程结束
                if self._thread and self._thread.is_alive():
                    self._state_lock.release()
                    self._thread.join(timeout=2.0)
                    self._state_lock.acquire()

            # 设置为运行状态
            self._state = TimerState.RUNNING

            # 计算首次执行时间
            first_interval = time_out if time_out is not None else self.interval
            self._next_run_time = time.time() + first_interval
            self._pause_accumulated_time = 0

            # 创建并启动工作线程
            self._thread = threading.Thread(target=self._worker, daemon=self.daemon)
            self._thread.start()

    def _stop_locked(self):
        """内部停止方法（假设已持有锁）"""
        if self._state == TimerState.IDLE:
            return

        old_state = self._state
        self._state = TimerState.STOPPING

        # 唤醒工作线程
        with self._state_changed:
            self._state_changed.notify_all()

        self._wakeup_event.set()

    def pause(self):
        """暂停/恢复"""
        with self._state_lock:
            if self._state == TimerState.RUNNING:
                # 暂停
                self._state = TimerState.PAUSED
                self._pause_start_time = time.time()
                # 唤醒工作线程，让它进入暂停状态
                with self._state_changed:
                    self._state_changed.notify_all()

            elif self._state == TimerState.PAUSED:
                # 恢复
                self._state = TimerState.RUNNING
                # 计算暂停时间并调整下次执行时间
                pause_duration = time.time() - self._pause_start_time
                self._next_run_time += pause_duration
                self._pause_accumulated_time += pause_duration
                # 唤醒工作线程
                with self._state_changed:
                    self._state_changed.notify_all()
                self._wakeup_event.set()

    def stop(self):
        """停止"""
        with self._state_lock:
            if self._state == TimerState.IDLE:
                return

            self._stop_locked()

            # 获取线程引用
            thread = self._thread
            self._thread = None

        # 在锁外等待线程结束
        if thread and thread.is_alive():
            thread.join(timeout=2.0)

    def get_state(self) -> str:
        """获取当前状态"""
        with self._state_lock:
            return self._state.value
