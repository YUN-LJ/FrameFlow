"""
任务管理
创建Task类的实例后
调用TaskManage.add_task方法即可执行任务
"""
import threading, queue, time, os
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, List, Any


class TaskProgress:
    """任务进度"""

    def __init__(self):
        self.total = 0  # 任务总量
        self.finished = 0  # 已完成数量
        self.rate = 0  # 速率

    def get_progress(self) -> int:
        """获取百分制进度"""
        value = int((self.finished / self.total) * 100) if self.total != 0 else 0
        return value

    def __str__(self):
        return f'已完成:{self.finished} 总计:{self.total} 速率:{self.rate}'

    def __repr__(self):
        return f'已完成:{self.finished} 总计:{self.total} 速率:{self.rate}'


class TaskSignalExecutor:
    """全局信号执行器，所有信号实例共享同一个线程"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.task_queue = queue.Queue()
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def _worker_loop(self):
        """工作线程主循环"""
        while self.running:
            try:
                # 从队列获取任务，超时时间1秒以便检查running状态
                task = self.task_queue.get(timeout=1)
                if task is None:  # 退出信号
                    break
                func, args, kwargs = task
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    print(f"槽函数执行错误: {e}")
                finally:
                    self.task_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"工作线程错误: {e}")

    def submit(self, func: Callable, *args, **kwargs):
        """提交任务到队列"""
        self.task_queue.put((func, args, kwargs))

    def shutdown(self):
        """关闭执行器"""
        self.running = False
        self.task_queue.put(None)  # 发送退出信号
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2)


class TaskSignal:
    """仿Qt的Signal信号类，所有槽函数在同一个后台线程执行"""

    _executor = TaskSignalExecutor()  # 共享执行器

    def __init__(self):
        self._funcs: List[Callable] = []
        self._lock = threading.Lock()  # 保护_funcs的并发访问

    def emit(self, value: Any):
        """发送信号，所有槽函数在工作线程中执行"""
        with self._lock:
            # 复制函数列表，避免遍历过程中被修改
            funcs = self._funcs.copy()

        # 提交每个槽函数到执行器
        for func in funcs:
            if callable(func):
                self._executor.submit(func, value)

    def connect(self, func: Callable):
        """连接槽函数"""
        if not callable(func):
            raise TypeError("槽函数必须是可调用的")

        with self._lock:
            if func not in self._funcs:
                self._funcs.append(func)

    def disconnect(self, func: Callable = None):
        """断开连接"""
        with self._lock:
            if func is None:
                self._funcs.clear()
            elif func in self._funcs:
                self._funcs.remove(func)

    def __len__(self):
        """返回连接的槽函数数量"""
        with self._lock:
            return len(self._funcs)


class TaskManage:
    """任务管理类"""

    def __init__(self, num_work: int = None):
        self.isStop = False  # 是否停止
        self.num_work = os.cpu_count() if num_work is None else num_work
        self.__thread_pool = ThreadPoolExecutor(max_workers=num_work)
        # 存储了全部未完成的Task任务,可通过name属性获取到任务名称
        self.__all_tasks: set[Task] = set()
        self.__lock = threading.Lock()

    def __add(self, task):
        with self.__lock:
            self.__all_tasks.add(task)

    def __discard(self, task):
        with self.__lock:
            self.__all_tasks.discard(task)

    def set_thread_num(self, value):
        if value == self.num_work:
            return
        self.num_work = value
        old_pool = self.__thread_pool  # 保持旧线程引用
        # 创建新线程池
        self.__thread_pool = ThreadPoolExecutor(max_workers=self.num_work)
        old_pool.shutdown(wait=False, cancel_futures=False)

    @property
    def get_all_task(self) -> set:
        with self.__lock:
            return self.__all_tasks.copy()

    def submit_task(self, task) -> Future | None:
        """添加任务"""
        if not self.isStop:
            try:
                self.__add(task)
                task.add_done_callback(lambda value=task: self.__discard(task))
                return self.__thread_pool.submit(task)
            except RuntimeError:
                print(f'线程池已关闭 {task.name},程序已强制退出')
                os._exit(-1)
                return None

    def stop(self):
        """
        停止
        注意当前正在执行的任务将不会被终止
        未开始的任务将全部被取消,未开始且被取消的任务不会调用回调函数
        """
        self.isStop = True
        self.__thread_pool.shutdown(wait=False, cancel_futures=True)
        with self.__lock:
            for task in self.__all_tasks.copy():
                task.stop()


class Task:
    """
    任务类
    start_signal,开始信号
    progress_signal,进度信号,需要在func函数中自定义
    finish_signal,完成信号
    自带的信号由独立的单线程维护不用考虑线程安全,
    添加的回调函数由各自任务所在的线程池维护,需要考虑线程安全
    """

    def __init__(self, func: Callable, task_manage: TaskManage, name: str = None, *args, **kwargs):
        """
        :param func:任务函数
        :param task_manage:任务池
        :param name:任务名称,默认使用任务函数名称
        :param args: 任务函数所需要的参数
        :param kwargs:任务函数所需要的参数
        """
        self.isRunning = False
        self.countRun = 0  # 已运行次数
        self.__args = args  # 依赖参数
        self.__kwargs = kwargs  # 依赖参数
        self.__func = lambda: func(*self.__args, **self.__kwargs)  # 可执行函数
        self.__task_manage = task_manage  # 线程池
        self.__callback_func = set()  # 所有的返回函数
        self.__future: Future = None  # 任务提交后的Future对象
        self.progress = TaskProgress()  # 进度属性
        # 信号的槽函数由单独的线程维护,循环调用会导致信号发送阻塞,这时请使用add_done_callback
        self.start_signal = TaskSignal()  # 任务开始信号
        self.progress_signal = TaskSignal()  # 任务进度信号
        self.finish_signal = TaskSignal()  # 任务完成信号
        self.stop_signal = TaskSignal()  # 任务停止信号
        self.__callback_func.add(lambda future: self.finish_signal.emit(future))
        # 尝试获取对象的__name__属性,如果属性不存在则返回str(func)
        self.name = getattr(func, '__name__', str(func)) if name is None else name

    def __call__(self):
        """返回执行函数,必须调用该函数"""
        return self.__func()

    def start(self, wait: float | int = None) -> Any | bool:
        """
        执行任务,可反复调用
        :param wait:是否等待任务完成,支持输入float|int值,默认不等待,等待时返回任务结果
        """
        if not self.isRunning:
            self.isRunning = True
        else:
            self.stop()
            self.isRunning = True
        self.start_signal.emit(self)
        self.__future = self.__task_manage.submit_task(self)
        if self.__future is not None:
            self.countRun += 1
            for callback in self.__callback_func:
                if callable(callback):
                    self.add_done_callback(callback)
            if wait is not None and isinstance(wait, (float, int)):
                wait_time = wait if isinstance(wait, (float, int)) and wait >= 0 else 1
                # 任务正在运行且没有被取消
                while self.isRunning and not self.done(): time.sleep(wait_time)
                return self.result()
            return True
        else:
            self.isRunning = False
            return False

    def stop(self) -> bool:
        if self.isRunning:
            self.isRunning = False
            self.__future.cancel()
            self.stop_signal.emit(True)

    def result(self, wait: float | int = None):
        """
        获取任务结果
        :param wait:是否等待任务完成,支持输入float|int值,默认不等待,等待时返回任务结果
        """
        if wait is not None and isinstance(wait, (float, int)):
            wait_time = wait if isinstance(wait, (float, int)) and wait >= 0 else 1
            while not self.done(): time.sleep(wait_time)
            return self.__future.result()
        return self.__future.result() if self.isRunning else None

    def done(self) -> bool:
        """任务是否完成"""
        return self.__future.done() if self.isRunning else False

    def clear_callback(self):
        """清空返回函数"""
        self.__callback_func.clear()

    def add_done_callback(self, callback_func: Callable):
        """添加回调函数,默认回传self"""

        def safe_callback(future: Future):
            """安全的回调包装器"""
            # 检查future是否被取消
            if future.cancelled():
                # print("Future已被取消，跳过回调")
                return
            # 执行回调
            # try:
            callback_func(self)
            # except Exception as e:
            #     print(e)

        self.__callback_func.add(callback_func)
        if self.isRunning and self.__future is not None:
            self.__future.add_done_callback(safe_callback)


if __name__ == '__main__':
    pass
