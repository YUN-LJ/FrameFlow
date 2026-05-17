"""
任务类说明:
    Task为核心类,其余类为任务管理类或/各种任务池
    任务对象依赖于Future
    任务池与ProcessPoolExecutor接口一致
使用方法:
    创建Task类的实例、或继承内部传入任务函数即可
    调用start方法即可运行在不同任务池中
"""
import os
import time
import heapq
import queue
import asyncio
import warnings
import threading
from concurrent.futures import Future, ProcessPoolExecutor
from typing import Callable, List, Any
from Fun.BaseTools import singleton_decorator
from Fun.BaseTools import LogClass

logger = LogClass.get_logger(__name__, console_level='WARNING')  # 日志
# 抑制asyncio的pending task警告
warnings.filterwarnings("ignore", message=".*Task was destroyed but it is pending!*")


class PriorityPoolExecutorBase:
    """支持优先级的池执行器基类"""

    def __init__(self, max_workers=None):
        self.max_workers = max_workers or os.cpu_count()
        self._work_queue = []  # 优先级队列（使用heapq）
        self._queue_counter = 0  # 用于保证相同优先级的任务按FIFO顺序
        self._shutdown = False

        # 创建工作单元（线程或进程）
        self._workers = []
        self._create_workers()

    def _create_workers(self):
        """创建工作单元（由子类实现）"""
        raise NotImplementedError("子类必须实现 _create_workers 方法")

    def _get_queue_lock(self):
        """获取队列锁（由子类实现）"""
        raise NotImplementedError("子类必须实现 _get_queue_lock 方法")

    def _get_counter_lock(self):
        """获取计数器锁（由子类实现）"""
        raise NotImplementedError("子类必须实现 _get_counter_lock 方法")

    def _worker_loop(self):
        """工作单元循环（由子类实现）"""
        raise NotImplementedError("子类必须实现 _worker_loop 方法")

    def _submit_task_to_queue(self, priority, counter, task_data):
        """将任务提交到队列（由子类实现）"""
        raise NotImplementedError("子类必须实现 _submit_task_to_queue 方法")

    def _create_future(self) -> Future:
        """创建Future对象（由子类实现）"""
        raise NotImplementedError("子类必须实现 _create_future 方法")

    def _wrap_function(self, fn, future, *args, **kwargs):
        """包装函数以捕获结果和异常（由子类实现）"""
        raise NotImplementedError("子类必须实现 _wrap_function 方法")

    def submit(self, fn, *args, priority=5, **kwargs) -> Future:
        """
        提交任务
        :param fn: 可调用函数
        :param args: 位置参数
        :param priority: 优先级（1-10，1为最高优先级，默认为5）
        :param kwargs: 关键字参数
        :return: Future对象
        """
        if self._shutdown:
            raise RuntimeError(f"{self.__class__.__name__}已关闭")

        future = self._create_future()
        wrapped_task = self._wrap_function(fn, future, *args, **kwargs)

        with self._get_counter_lock():
            counter = self._queue_counter
            self._queue_counter += 1

        # 限制优先级范围在1-10之间
        priority = max(1, min(10, priority))

        self._submit_task_to_queue(priority, counter, wrapped_task)

        return future

    def shutdown(self, wait=True, cancel_futures=False):
        """关闭池"""
        self._shutdown = True
        self._perform_shutdown(cancel_futures)

        if wait:
            for worker in self._workers:
                self._join_worker(worker)

    def _perform_shutdown(self, cancel_futures):
        """执行关闭操作（由子类实现）"""
        raise NotImplementedError("子类必须实现 _perform_shutdown 方法")

    def _join_worker(self, worker):
        """等待工作单元结束（由子类实现）"""
        raise NotImplementedError("子类必须实现 _join_worker 方法")

    # ========== 新增方法 ==========
    def running_cnt(self) -> int:
        """获取当前运行的任务数量（由子类实现）"""
        raise NotImplementedError("子类必须实现 running_cnt 方法")

    def is_full(self) -> bool:
        """判断当前是否满载（由子类实现）"""
        raise NotImplementedError("子类必须实现 is_full 方法")


class PriorityThreadPoolExecutor(PriorityPoolExecutorBase):
    """支持优先级的线程池执行器"""

    def __init__(self, max_workers=None):
        super().__init__(max_workers)

    def _create_workers(self):
        """创建工作线程"""
        for index in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f'{self.__class__.__name__}-{index}',
                daemon=True
            )
            worker.start()
            self._workers.append(worker)

    def _get_queue_lock(self):
        """获取线程锁"""
        return threading.Lock() if not hasattr(self, '_queue_lock') else self._queue_lock

    def _get_counter_lock(self):
        """获取计数器锁"""
        return threading.Lock() if not hasattr(self, '_counter_lock') else self._counter_lock

    def __init__(self, max_workers=None):
        self.max_workers = max_workers or os.cpu_count()
        self._work_queue = []
        self._queue_lock = threading.Lock()
        self._queue_counter = 0
        self._counter_lock = threading.Lock()
        self._shutdown = False
        self._workers = []
        self._running_cnt = 0  # 新增：运行任务计数
        self._running_lock = threading.Lock()  # 新增：运行计数锁
        self._create_workers()

    def _create_workers(self):
        for index in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f'{self.__class__.__name__}-{index}',
                daemon=True
            )
            worker.start()
            self._workers.append(worker)

    def _worker_loop(self):
        """工作线程循环"""
        while True:
            try:
                task_to_execute = None
                with self._queue_lock:
                    if not self._work_queue and self._shutdown:
                        break
                    if not self._work_queue:
                        pass
                    else:
                        # 弹出最高优先级的任务（数字越小优先级越高）
                        priority, counter, func, args, kwargs = heapq.heappop(self._work_queue)
                        task_to_execute = (func, args, kwargs)

                # 在锁外执行任务
                if task_to_execute:
                    func, args, kwargs = task_to_execute
                    with self._running_lock:
                        self._running_cnt += 1
                    try:
                        func(*args, **kwargs)
                    except Exception as e:
                        logger.exception(f"{func} 任务执行错误: {e}")
                    finally:
                        with self._running_lock:
                            self._running_cnt -= 1
                else:
                    time.sleep(0.01)
            except Exception as e:
                logger.exception(f"{self.__class__.__name__} 工作线程错误: {e}")

    def _create_future(self) -> Future:
        """创建Future对象"""
        return Future()

    def _wrap_function(self, fn, future, *args, **kwargs):
        """包装函数以捕获结果和异常"""

        def wrapped():
            try:
                result = fn(*args, **kwargs)
                future.set_result(result)
            except Exception as e:
                if future.cancelled():
                    return
                future.set_exception(e)

        return wrapped

    def _submit_task_to_queue(self, priority, counter, wrapped_task):
        """将任务提交到队列"""
        with self._queue_lock:
            heapq.heappush(self._work_queue, (priority, counter, wrapped_task, (), {}))

    def _perform_shutdown(self, cancel_futures):
        """执行关闭操作"""
        if cancel_futures:
            with self._queue_lock:
                self._work_queue.clear()

    def _join_worker(self, worker):
        """等待线程结束"""
        worker.join()

    # ========== 新增方法实现 ==========
    def running_cnt(self) -> int:
        with self._running_lock:
            return self._running_cnt

    def is_full(self) -> bool:
        return self.running_cnt() >= self.max_workers


class PriorityProcessPoolExecutor(PriorityPoolExecutorBase):
    """支持优先级的进程池执行器"""

    def __init__(self, max_workers=None):
        # 初始化变量，但不创建实际的队列，因为这些对象不能在多进程中传递
        self.max_workers = max_workers or os.cpu_count()
        self._work_queue = []  # 本地优先级队列
        self._queue_lock = threading.Lock()
        self._queue_counter = 0
        self._counter_lock = threading.Lock()
        self._shutdown = False
        self._futures_map = {}  # 存储任务ID和Future的映射
        self._task_counter = 0
        self._task_counter_lock = threading.Lock()
        self._running_cnt = 0  # 新增：运行任务计数
        self._running_lock = threading.Lock()  # 新增：运行计数锁

        self._executor = ProcessPoolExecutor(max_workers=self.max_workers)

        # 启动调度线程
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()
        self._workers = []

    def _get_next_task_id(self):
        """获取下一个任务ID"""
        with self._task_counter_lock:
            task_id = self._task_counter
            self._task_counter += 1
            return task_id

    def _create_workers(self):
        """不需要手动创建，使用ProcessPoolExecutor"""
        pass

    def _get_queue_lock(self):
        """获取队列锁"""
        return self._queue_lock

    def _get_counter_lock(self):
        """获取计数器锁"""
        return self._counter_lock

    def _scheduler_loop(self):
        """调度线程 - 从本地队列按优先级取出任务提交给进程池"""
        while not (self._shutdown and len(self._work_queue) == 0):
            task_to_execute = None
            with self._queue_lock:
                if self._work_queue:
                    # 弹出最高优先级的任务（数字越小优先级越高）
                    priority, counter, task_id, func, args, kwargs = heapq.heappop(self._work_queue)
                    task_to_execute = (task_id, func, args, kwargs)

            if task_to_execute:
                task_id, func, args, kwargs = task_to_execute
                try:
                    # 提交任务到实际的进程池
                    process_future = self._executor.submit(func, *args, **kwargs)

                    # 只有在成功提交后才增加运行计数
                    with self._running_lock:
                        self._running_cnt += 1

                    # 获取对应的future对象
                    if task_id in self._futures_map:
                        user_future = self._futures_map[task_id]
                        # 创建一个线程来等待进程池的结果并设置用户future
                        threading.Thread(
                            target=self._transfer_result,
                            args=(process_future, user_future),
                            daemon=True
                        ).start()
                except Exception as e:
                    logger.exception(f"任务提交失败: {e}")
                    if task_id in self._futures_map:
                        self._futures_map[task_id].set_exception(e)
            else:
                time.sleep(0.01)

    def _transfer_result(self, process_future, user_future):
        """将进程池的结果转移到用户future"""
        try:
            result = process_future.result()
            # 检查用户Future是否已被取消
            if not user_future.cancelled():
                user_future.set_result(result)
        except Exception as e:
            # 检查用户Future是否已被取消
            if not user_future.cancelled():
                user_future.set_exception(e)
        finally:
            # 确保无论如何都减少运行计数
            with self._running_lock:
                self._running_cnt -= 1
        # 清理映射
        task_ids_to_remove = [k for k, v in self._futures_map.items() if v == user_future]
        for task_id in task_ids_to_remove:
            self._futures_map.pop(task_id, None)

    def _worker_loop(self):
        """不需要，使用调度线程代替"""
        pass

    def _create_future(self) -> Future:
        """创建Future对象"""
        return Future()

    def _wrap_function(self, fn, future, *args, **kwargs):
        """包装函数，返回可以直接提交给进程池的函数"""
        task_id = self._get_next_task_id()
        # 保存future映射
        self._futures_map[task_id] = future

        # 特殊处理：如果是Task对象，我们提取其内部函数
        if hasattr(fn, '__call__') and hasattr(fn, '_Task__func'):
            # 这是一个Task对象，提取其内部函数和参数
            actual_func = fn._Task__func
            actual_args = fn._Task__args
            actual_kwargs = fn._Task__kwargs
        else:
            # 这是一个普通函数，使用传入的参数
            actual_func = fn
            actual_args = args
            actual_kwargs = kwargs

        # 返回原始函数和参数，它们是可序列化的
        # 注意：fn必须是模块级别的函数，否则无法被pickle
        return actual_func, actual_args, actual_kwargs, task_id

    def _submit_task_to_queue(self, priority, counter, wrapped_task_info):
        """将任务提交到本地优先级队列"""
        func, args, kwargs, task_id = wrapped_task_info
        with self._queue_lock:
            heapq.heappush(self._work_queue, (priority, counter, task_id, func, args, kwargs))

    def _perform_shutdown(self, cancel_futures):
        """执行关闭操作"""
        self._shutdown = True
        self._executor.shutdown(wait=True, cancel_futures=cancel_futures)

    def _join_worker(self, worker):
        """不需要，使用ProcessPoolExecutor的内部实现"""
        pass

    # ========== 新增方法实现 ==========
    def running_cnt(self) -> int:
        with self._running_lock:
            return self._running_cnt

    def is_full(self) -> bool:
        return self.running_cnt() >= self.max_workers


class PriorityAsyncPoolExecutor(PriorityPoolExecutorBase):
    """支持优先级的异步协程池执行器

    特性：
    - 只接受异步函数（async def）
    - 使用独立的事件循环线程
    - 支持优先级调度（1-10，1为最高）
    - 跨线程通信使用 queue.Queue（线程安全）
    - 通过信号量控制并发数量
    """

    def __init__(self, max_workers=None):
        self.max_workers = max_workers or os.cpu_count()
        self._work_queue = []  # 优先级队列（使用heapq）
        self._queue_lock = threading.Lock()
        self._queue_counter = 0
        self._counter_lock = threading.Lock()
        self._shutdown = False
        self._workers = []
        self._running_cnt = 0  # 新增：运行任务计数
        self._running_lock = threading.Lock()  # 新增：运行计数锁
        # 创建独立的事件循环线程
        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(
            target=self._run_event_loop,
            name=f'{self.__class__.__name__}.事件循环',
            daemon=True
        )
        self._loop_thread.start()
        # 等待事件循环启动完成
        while not hasattr(self, '_loop_ready'):
            time.sleep(0.01)
        # 在事件循环中创建信号量来控制并发
        self._semaphore = None
        self._init_semaphore()
        # 创建调度线程
        self._create_workers()

    def _init_semaphore(self):
        """在事件循环中初始化信号量"""
        future = asyncio.run_coroutine_threadsafe(self._wrap_semaphore_create(), self._loop)
        future.result()  # 等待创建完成

    async def _wrap_semaphore_create(self):
        """包装信号量创建"""
        self._semaphore = asyncio.Semaphore(self.max_workers)

    def _run_event_loop(self):
        """运行异步事件循环"""
        asyncio.set_event_loop(self._loop)
        self._loop_ready = True
        try:
            self._loop.run_forever()
        finally:
            self._loop.close()

    def _create_workers(self):
        """创建调度工作线程"""
        scheduler = threading.Thread(
            target=self._worker_loop,
            name=f'{self.__class__.__name__}.调度器',
            daemon=True
        )
        scheduler.start()
        self._workers.append(scheduler)

    def _get_queue_lock(self):
        """获取队列锁"""
        return self._queue_lock

    def _get_counter_lock(self):
        """获取计数器锁"""
        return self._counter_lock

    def submit(self, fn, *args, priority=5, **kwargs) -> Future:
        """
        提交异步任务
        :param fn: 异步函数（必须是 async def 定义）
        :param args: 位置参数
        :param priority: 优先级（1-10，1为最高优先级，默认为5）
        :param kwargs: 关键字参数
        :return: Future对象
        :raises TypeError: 如果传入的不是异步函数
        :raises RuntimeError: 如果池已关闭
        """
        if self._shutdown:
            raise RuntimeError(f"{self.__class__.__name__}已关闭")

        # 验证必须是异步函数
        if not asyncio.iscoroutinefunction(fn):
            raise TypeError(
                f"异步池只接受异步函数，但收到了: "
                f"{fn.__name__ if hasattr(fn, '__name__') else fn}"
            )

        future = self._create_future()
        wrapped_task = self._wrap_function(fn, future, *args, **kwargs)

        with self._get_counter_lock():
            counter = self._queue_counter
            self._queue_counter += 1

        # 限制优先级范围在1-10之间
        priority = max(1, min(10, priority))

        self._submit_task_to_queue(priority, counter, wrapped_task)

        return future

    def _wrap_function(self, fn, future, *args, **kwargs):
        """包装异步函数以捕获结果和异常，并添加信号量控制"""

        async def async_wrapper():
            """异步包装器，使用信号量控制并发"""
            # 等待获取信号量
            await self._semaphore.acquire()
            with self._running_lock:
                self._running_cnt += 1
            try:
                result = await fn(*args, **kwargs)
                if not future.cancelled():
                    future.set_result(result)
            except Exception as e:
                if not future.cancelled():
                    future.set_exception(e)
            finally:
                with self._running_lock:
                    self._running_cnt -= 1
                # 释放信号量前检查事件循环是否仍有效
                try:
                    if not self._loop.is_closed():
                        self._semaphore.release()
                except Exception:
                    pass

        return async_wrapper

    def _submit_task_to_queue(self, priority, counter, wrapped_task):
        """将包装后的异步任务提交到优先级队列"""
        with self._queue_lock:
            heapq.heappush(self._work_queue, (priority, counter, wrapped_task, (), {}))

    def _worker_loop(self):
        """调度线程 - 从优先级队列取出任务并提交到事件循环"""
        while not (self._shutdown and len(self._work_queue) == 0):
            task_to_execute = None
            with self._queue_lock:
                if self._work_queue:
                    # 弹出最高优先级的任务（数字越小优先级越高）
                    priority, counter, wrapped_func, args, kwargs = heapq.heappop(self._work_queue)
                    task_to_execute = (wrapped_func, args, kwargs)

            if task_to_execute:
                wrapped_func, args, kwargs = task_to_execute
                try:
                    # 将协程提交到事件循环执行
                    asyncio.run_coroutine_threadsafe(
                        wrapped_func(*args, **kwargs),
                        self._loop
                    )
                except Exception as e:
                    logger.exception(f"任务执行失败: {e}")
            else:
                time.sleep(0.01)

    def _create_future(self) -> Future:
        """创建Future对象"""
        return Future()

    def _perform_shutdown(self, cancel_futures):
        """执行关闭操作"""
        if cancel_futures:
            with self._queue_lock:
                self._work_queue.clear()

        # 先停止事件循环
        if self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)

        # 等待事件循环线程结束（给协程足够时间完成finally块）
        if self._loop_thread.is_alive():
            self._loop_thread.join(timeout=5)

        # 如果仍有协程未清理，记录警告
        if self._loop_thread.is_alive():
            logger.warning(f"{self.__class__.__name__} 事件循环线程未能在超时内结束")

    def _join_worker(self, worker):
        """等待工作线程结束"""
        worker.join(timeout=2)

    # ========== 新增方法实现 ==========
    def running_cnt(self) -> int:
        with self._running_lock:
            return self._running_cnt

    def is_full(self) -> bool:
        return self.running_cnt() >= self.max_workers


class TaskManageBase:
    """
    任务管理类基类
    submit_task方法为对外提交任务方法
    内部由_pool_submit负责执行具体任务池的提交
    子类需要更改提交任务逻辑重写_pool_submit方法即可
    """
    all_manage: list['TaskManageBase'] = []

    def __init__(self, num_work: int = None):
        self.isStop = False  # 是否停止
        self.num_work = os.cpu_count() if num_work is None else num_work
        self.pool = self.create_pool(self.num_work)
        # 存储了全部未完成的Task任务
        self.__all_tasks: set[Task] = set()
        self.__lock = threading.Lock()
        self.__class__.all_manage.append(self)

    def create_pool(self, num_work: int) -> PriorityThreadPoolExecutor:
        """创建内部池的方法"""
        return PriorityThreadPoolExecutor(num_work)

    def __add(self, task):
        with self.__lock:
            self.__all_tasks.add(task)

    def __discard(self, task):
        with self.__lock:
            self.__all_tasks.discard(task)

    def set_num_work(self, value):
        if value == self.num_work:
            return
        self.num_work = value
        old_pool = self.pool  # 保持旧线程引用
        # 创建新线程池
        self.pool = self.create_pool(self.num_work)
        old_pool.shutdown(False, False)

    @property
    def get_all_task(self) -> set:
        with self.__lock:
            return self.__all_tasks.copy()

    def submit_task(self, task: 'Task', priority=5) -> Future | None:
        """
        添加任务
        :param task: 任务对象
        :param priority: 优先级（1-10，1为最高优先级，默认为5）
        :return: Future对象或None
        """
        if not self.isStop:
            try:
                self.__add(task)
                task.add_done_callback(lambda value=task: self.__discard(task))
                return self._pool_submit(task, priority)
            except RuntimeError:
                logger.critical(f'线/协/进程池已关闭 {task.name}')
                return None

    def _pool_submit(self, task: 'Task', priority=5):
        return self.pool.submit(task, priority=priority)

    def stop(self):
        """停止"""
        try:
            self.isStop = True
            with self.__lock:
                for task in self.__all_tasks.copy():
                    task.stop()
            self.pool.shutdown(wait=False, cancel_futures=True)
            self.__class__.all_manage.remove(self)
        except Exception as e:
            logger.exception(f'{self.__class__.__name__}.stop() 错误: {e}')

    # ========== 新增方法 ==========
    @property
    def running_cnt(self) -> int:
        """获取当前运行的任务数量"""
        return self.pool.running_cnt()

    @property
    def is_full(self) -> bool:
        """判断当前是否满载"""
        return self.pool.is_full()

    def wait_idle(self, parent_task: 'Task', keep=0) -> bool:
        """
        等待到任务池空闲
        :param parent_task:关联任务
        :param keep: 留存任务数量,默认为0,表示占满任务池,1表示提交改任务后,
                     任务池预计剩余一个工作线程,由于多线程同时提交可能任务池还是会占满
        """
        while parent_task.isRunning:
            if keep == 0 and not self.is_full:
                return True
            elif 0 < keep < self.num_work - self.running_cnt:
                return True
            time.sleep(0.1)
        return False


# ----------外部调用类---------
class TaskManage(TaskManageBase):
    """任务管理类（多线程）"""

    def __init__(self, num_work: int = None):
        super().__init__(num_work)

    def create_pool(self, num_work: int):
        return PriorityThreadPoolExecutor(max_workers=num_work)


class TaskProcessManage(TaskManageBase):
    """任务管理类（多进程）"""

    def __init__(self, num_work: int = None):
        super().__init__(num_work)

    def create_pool(self, num_work: int):
        return PriorityProcessPoolExecutor(max_workers=num_work)


class TaskAsyncManage(TaskManageBase):
    """任务管理类（异步协程）"""

    def __init__(self, num_work: int = None):
        super().__init__(num_work)

    def create_pool(self, num_work: int):
        return PriorityAsyncPoolExecutor(max_workers=num_work)

    def _pool_submit(self, task: 'Task', priority=5):
        func, args, kwargs = task.get_func()
        return self.pool.submit(func, *args, priority=priority, **kwargs)


# ----------辅助类---------
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

    def __init__(self):
        self.task_queue = queue.Queue()
        self.isRunning = True
        self.worker_thread = threading.Thread(
            target=self._worker_loop, name=f'{self.__class__.__name__}.信号线程', daemon=True)
        self.worker_thread.start()

    def _worker_loop(self):
        """工作线程主循环"""
        while self.isRunning:
            try:
                task = self.task_queue.get(timeout=0.2)
                if task is None:  # 退出信号
                    break
                func, args, kwargs = task
                try:
                    func(*args, **kwargs)
                except Exception:
                    logger.exception(f'{self.__class__.__name__} 槽函数执行错误')
                finally:
                    self.task_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.exception(f'{self.__class__.__name__} 工作线程错误')

    def submit(self, func: Callable, *args, **kwargs):
        """提交任务到队列"""
        self.task_queue.put((func, args, kwargs))

    def shutdown(self):
        """关闭执行器"""
        self.isRunning = False
        self.task_queue.put(None)  # 放入停止标识符
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

        def wrapped(*args, **kwargs):
            """槽函数包装器"""
            try:
                for func in funcs:
                    func(*args, **kwargs)
            except Exception as e:
                if 'Signal source has been deleted' in str(e):
                    self.disconnect(func)
                else:
                    logger.exception(f'{self.__class__.__name__} {func.__name__}槽函数执行错误')

        with self._lock:
            # 复制函数列表，避免遍历过程中被修改
            funcs = self._funcs.copy()

        # 提交槽函数包装器到执行器
        self._executor.submit(wrapped, value)

    def connect(self, func: Callable):
        """连接槽函数"""
        if not callable(func):
            raise TypeError("槽函数必须是可调用的")

        with self._lock:
            if func not in self._funcs:
                self._funcs.append(func)

    def connect_once(self, func: Callable):
        """
        单次连接槽函数，发射一次后自动移除
        :param func: 槽函数
        """
        if not callable(func):
            raise TypeError("槽函数必须是可调用的")

        def wrapper(value):
            try:
                func(value)
            except Exception:
                logger.exception(f'{self.__class__.__name__} {func.__name__}槽函数执行错误')
            finally:
                # 执行完成后断开连接
                self.disconnect(wrapper)

        with self._lock:
            if wrapper not in self._funcs:
                self._funcs.append(wrapper)

    def disconnect(self, func: Callable = None):
        """断开连接"""
        with self._lock:
            if func is None:
                self._funcs.clear()
            elif func in self._funcs:
                self._funcs.remove(func)

    def bridge_signal(self, signal: Any):
        """
        桥接信号,一般用于转接Qt信号
        :param signal:实现了emit方法的类
        """
        self.connect(signal.emit)

    def __len__(self):
        """返回连接的槽函数数量"""
        with self._lock:
            return len(self._funcs)


class Task:
    """
    基本说明:
        任务类,所有继承该类的都带有四个信号,开始、进度、完成、停止
        支持协程/多线程/多进程,提交到不同的管理类中将即可,
        如果是异步则传入的函数支持异步写法
    信号说明:
        start_signal,开始信号,发送自身
        progress_signal,进度信号,需要在func函数中自定义
        finish_signal,完成信号,发送自身
        stop_signal,停止信号,发送自身
        自带的信号由独立的单线程维护不用考虑线程安全,
        添加的回调函数由各自任务所在的线程池/进程池维护,需要考虑线程安全
        高耗时任务使用add_done_callback添加回调
    执行状态:
        isRunning属性(只读且子类无法修改)用于判断任务是否正在运行
        任务调用了start方法后isRunning将变为True
        任务完成后isRuning将变为False,依赖finish_signal信号修改
    """

    def __init__(self, func: Callable, task_manage: 'TaskManageBase' = None, name: str = None,
                 use_process: bool = False, args: tuple = (), kwargs: dict = None):
        """
        :param func:任务函数
        :param task_manage:任务池,不传入时内部创建一个单线程任务池,启用use_process时使用子进程任务池
        :param name:任务名称,默认使用任务函数名称
        :param use_process:是否使用多进程模式
        :param parent_task:父任务,父任务被停止时,子任务也会被终止
        :param args: 任务函数所需要的参数
        :param kwargs:任务函数所需要的参数
        """
        self.__isRunning = False
        self.countRun = 0  # 已运行次数
        self.__func = func  # 保存原始函数
        self.__args = args if isinstance(args, tuple) else (args,)  # 保存位置参数
        self.__kwargs = kwargs if kwargs is not None else {}  # 保存关键字参数

        if task_manage is None:
            if use_process:
                self.__task_manage = TaskProcessManage(1)
            else:
                self.__task_manage = TaskManage(1)
        else:
            self.__task_manage = task_manage

        self.__callback_func = set()  # 所有的返回函数
        self.__future: Future = None  # 任务提交后的Future对象
        self.progress = TaskProgress()  # 进度属性
        # 信号的槽函数由单独的线程维护,循环调用会导致信号发送阻塞,这时请使用add_done_callback
        self.start_signal = TaskSignal()  # 任务开始信号
        self.progress_signal = TaskSignal()  # 任务进度信号
        self.finish_signal = TaskSignal()  # 任务完成信号
        self.stop_signal = TaskSignal()  # 任务停止信号
        self.__callback_func.add(self.__finished_solt)
        # 尝试获取对象的__name__属性,如果属性不存在则返回str(func)
        self.name = getattr(func, '__name__', str(func)) if name is None else name

    def __call__(self):
        """返回执行函数,必须调用该函数"""
        # 当在多进程环境中被调用时，只执行函数部分，不传递整个对象
        return self.__func(*self.__args, **self.__kwargs)

    @property
    def isRunning(self) -> bool:
        return self.__isRunning

    def get_func(self) -> tuple[Callable, tuple, dict]:
        """获取任务函数及其参数"""
        return self.__func, self.__args, self.__kwargs

    def start(self, timeout: float | int = None, priority: int = 5, parent_task: 'Task' = None) -> Any | bool:
        """
        执行任务,可反复调用
        :param timeout:是否等待任务完成,支持输入float|int值,0为无限等待,默认不等待,等待时返回任务结果,超时停止
        :param priority: 任务优先级（1-10，1为最高优先级，默认为5）
        :param parent_task:关联父任务,用于父任务被停止时关闭阻塞中的子任务,timeout>=0时生效
        """
        if not self.__isRunning:
            self.__isRunning = True
        else:
            self.stop()
            self.__isRunning = True
        self.start_signal.emit(self)
        self.__future = self.__task_manage.submit_task(self, priority=priority)
        if self.__future is not None:
            self.countRun += 1
            for callback in self.__callback_func:
                if callable(callback):
                    self.add_done_callback(callback)
            if timeout is not None:
                return self.result(timeout, parent_task)
            return True
        else:
            self.stop()
            logger.warning(f'{self.name} 任务提交失败')
            return False

    def start_sync(self) -> Any | bool:
        """同步开始,在本线程同步执行任务函数,返回任务结果"""
        if not self.__isRunning:
            self.__isRunning = True
        else:
            self.stop()
            self.__isRunning = True
        self.start_signal.emit(self)
        self.__future = Future()
        self.countRun += 1
        for callback in self.__callback_func:
            if callable(callback):
                self.add_done_callback(callback)
        try:
            result = self.__call__()
            self.__future.set_result(result)
            return result
        except Exception as e:
            self.__future.set_exception(e)
            return False

    def stop(self) -> bool:
        """停止任务,已开始的任务无法被取消,需要在提交函数内引用isRunning标识符"""
        state = False
        if self.__isRunning:
            self.__isRunning = False
            state = self.__future.cancel()
        self.stop_signal.emit(state)
        return state

    def result(self, timeout: float | int = None, parent_task: 'Task' = None):
        """
        获取任务结果
        :param timeout:是否等待任务完成,支持输入float|int值,0为无限等待,默认不等待,等待时返回任务结果,超时时会停止当前任务
        :param parent_task:关联父任务,用于父任务被停止时关闭阻塞中的子任务,timeout>=0时生效
        """
        try:
            if timeout is not None and isinstance(timeout, (float, int)):
                timeout = max(timeout, 0)
                # 任务正在运行且没有被取消
                start_time = time.time()
                while self.__isRunning and not self.done():
                    if parent_task is not None and not parent_task.__isRunning:
                        self.stop()
                        return None
                    if timeout != 0 and time.time() - start_time >= timeout:
                        self.stop()
                        return None
                    else:
                        time.sleep(0.1)
                if not self.__future.cancelled():
                    return self.__future.result()
            # 即使 isRunning 为 False，只要任务已完成，仍可获取结果
            if self.__future is not None and self.__future.done() and not self.__future.cancelled():
                return self.__future.result()
        except Exception as e:
            logger.exception(f'{self.__class__.__name__}.result 错误{e}')
        return None

    def set_result(self, result):
        """
        设置任务结果，必须在任务结束后才可设置
        :param result: 任务结果
        :raises RuntimeError: 如果任务仍在运行
        """
        if self.__isRunning:
            raise RuntimeError(f"任务 '{self.name}' 仍在运行中，无法设置结果")

        if self.__future is not None and not self.__future.done():
            self.__future.set_result(result)
        else:
            logger.warning(f"警告: 任务 '{self.name}' 的 Future 对象不存在或已完成，无法设置结果")

    def done(self) -> bool:
        """任务是否完成"""
        if self.__future is not None:
            return self.__future.done()
        return False

    def clear_callback(self):
        """清空返回函数"""
        self.__callback_func.clear()

    def add_done_callback(self, callback_func: Callable):
        """添加回调函数,默认回传self"""

        def safe_callback(future: Future):
            """安全的回调包装器"""
            # 检查future是否被取消
            if future.cancelled():
                logger.debug(f"{self.name} Future已被取消,跳过回调")
                return
            # 执行回调
            try:
                callback_func(self)
            except Exception as e:
                logger.exception(f'{self.name}回调执行错误')

        self.__callback_func.add(callback_func)
        if self.__isRunning and self.__future is not None:
            self.__future.add_done_callback(safe_callback)

    def __finished_solt(self, task: 'Task'):
        """任务执行后发送完成信号"""
        self.__isRunning = False
        self.finish_signal.emit(task)

    def cleanup(self):
        """
        显式清理任务对象及其缓存
        用于彻底释放任务资源，断开所有信号连接，清除回调函数
        
        使用场景：
        1. 任务完成后不再需要该任务对象
        2. 页面/组件销毁时需要清理关联的任务
        3. 防止信号累积和内存泄漏
        
        注意：
        - 调用后任务对象不应再被使用
        - 会自动停止正在运行的任务
        - 会断开所有TaskSignal的连接
        """
        # 1. 停止正在运行的任务
        if self.__isRunning:
            self.stop()

        # 2. 取消Future（如果存在）
        if self.__future is not None:
            try:
                self.__future.cancel()
            except Exception:
                pass
            self.__future = None

        # 3. 清空所有回调函数
        self.clear_callback()

        # 4. 断开所有信号连接
        self.start_signal.disconnect()
        self.progress_signal.disconnect()
        self.finish_signal.disconnect()
        self.stop_signal.disconnect()

        # 5. 清理进度对象
        self.progress = None

        # 6. 清理函数引用和参数（帮助垃圾回收）
        self.__func = None
        self.__args = ()
        self.__kwargs = {}

        # 7. 清理任务管理器引用（如果是内部创建的）
        # 注意：外部传入的task_manage不由这里清理
        if hasattr(self, '_Task__task_manage'):
            # 只清理内部创建的单线程管理器
            if isinstance(self.__task_manage, (TaskManage, TaskProcessManage)):
                # 检查是否是单工作线程的内部管理器
                if self.__task_manage.num_work == 1:
                    try:
                        self.__task_manage.stop()
                    except Exception:
                        pass

        # 8. 标记为已清理
        self.__isRunning = False
        self.name = f"{self.name}_CLEANED"

    def __del__(self):
        """析构函数，确保资源被清理"""
        try:
            # 避免在解释器关闭时出错
            if hasattr(self, '_Task__isRunning'):
                self.cleanup()
        except Exception:
            pass
