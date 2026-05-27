"""
任务类说明:
    Task为核心类,其余类为任务管理类或/各种任务池
    任务对象依赖于Future
    任务池与ProcessPoolExecutor接口一致
    对于Task内递归提交到任务管理内需要
使用方法:
    创建Task类的实例、或继承内部传入任务函数即可
    调用start方法即可运行在不同任务池中
"""
import os
import time
import queue
import asyncio
import weakref
import warnings
import threading
from enum import Enum
from weakref import ReferenceType, WeakSet
from Fun.BaseTools import LogClass
from queue import PriorityQueue, Empty
from concurrent.futures import Future, ThreadPoolExecutor, ProcessPoolExecutor
from typing import Callable, Any, Optional, Iterable
from functools import partial

logger = LogClass.get_logger(__name__, console_level='WARNING')  # 日志
# 抑制asyncio的pending task警告
warnings.filterwarnings("ignore", message=".*Task was destroyed but it is pending!*")


# 优先级任务池
class BasePriorityPool:
    """优先级任务池基类"""

    def __init__(self, max_workers: Optional[int] = None):
        """
        初始化优先级池
        :param max_workers: 最大工作线程数，默认为CPU核心数
        """
        self._max_workers = max_workers or os.cpu_count()
        self._task_queue = PriorityQueue()  # 优先级队列
        self._seq = 0  # 序列号，保证同优先级FIFO
        self._shutdown = False
        self._shutdown_lock = threading.Lock()

        # 跟踪运行中的任务
        self._running_futures = set()
        self._running_lock = threading.Lock()
        self._idle_condition = threading.Condition()

        # 启动调度线程
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()

    def submit(self,
               fn: Callable,
               *args,
               priority: int = 5,
               **kwargs) -> Future:
        """
        提交任务
        :param fn: 可调用对象
        :param args: 位置参数
        :param priority: 优先级(1-10，1最高，默认5)
        :param retry_count:重试次数,默认为0即不重试
        :param kwargs: 关键字参数
        :return: Future对象
        """
        if self._shutdown:
            raise RuntimeError(f"{self.__class__.__name__}已关闭")

        # 限制优先级范围
        priority = max(1, min(10, priority))

        # 创建用户Future
        user_future = Future()

        # 获取序列号
        with self._running_lock:
            seq = self._seq
            self._seq += 1

        # 放入优先级队列 (优先级越小越先执行)
        self._task_queue.put((priority, seq, fn, args, kwargs, user_future))

        return user_future

    def _scheduler_loop(self):
        """调度线程主循环"""
        while True:
            # 检查关闭状态
            if self._shutdown and self._task_queue.empty():
                break

            # 等待空闲槽位
            with self._idle_condition:
                with self._running_lock:
                    running_count = len(self._running_futures)

                while running_count >= self._max_workers and not self._shutdown:
                    logger.debug(f"{self.__class__.__name__}已满，等待空闲槽位")
                    self._idle_condition.wait(timeout=0.1)
                    with self._running_lock:
                        running_count = len(self._running_futures)

                if self._shutdown and self._task_queue.empty():
                    break

            # 从队列获取任务
            try:
                item = self._task_queue.get_nowait()
            except Empty:
                # 队列为空，短暂休眠避免CPU空转
                threading.Event().wait(0.01)
                continue

            priority, seq, fn, args, kwargs, user_future = item

            # 检查用户Future是否已被取消
            if user_future.cancelled():
                continue

            # 提交任务到具体执行器
            try:
                executor_future = self._submit_to_executor(fn, args, kwargs)

                # 记录运行中的任务
                with self._running_lock:
                    self._running_futures.add(executor_future)

                # 注册完成回调
                executor_future.add_done_callback(
                    partial(self._on_task_done, user_future=user_future)
                )

            except Exception as e:
                # 提交失败，直接设置异常
                if not user_future.cancelled():
                    user_future.set_exception(e)

    def _submit_to_executor(self, fn: Callable, args: tuple, kwargs: dict) -> Future:
        """
        提交任务到具体执行器（子类实现）
        :param fn: 函数
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 执行器的Future对象
        """
        raise NotImplementedError("子类必须实现 _submit_to_executor 方法")

    def _on_task_done(self, executor_future: Future, user_future: Future):
        """
        任务完成回调
        :param executor_future: 执行器的Future
        :param user_future: 用户的Future
        """
        try:
            # 检查用户Future是否已被取消
            if user_future.cancelled():
                # 尝试取消执行器任务
                if not executor_future.done():
                    executor_future.cancel()
                return

            # 传递结果或异常
            if executor_future.cancelled():
                if not user_future.cancelled():
                    user_future.cancel()
            else:
                try:
                    result = executor_future.result()
                    if not user_future.cancelled():
                        user_future.set_result(result)
                except Exception as e:
                    if not user_future.cancelled():
                        user_future.set_exception(e)
        finally:
            # 清理并通知调度线程
            with self._running_lock:
                self._running_futures.discard(executor_future)

            with self._idle_condition:
                self._idle_condition.notify()

    def shutdown(self, wait: bool = True, cancel_futures: bool = False):
        """
        关闭任务池
        :param wait: 是否等待所有任务完成
        :param cancel_futures: 是否取消待执行的任务
        """
        with self._shutdown_lock:
            if self._shutdown:
                return
            self._shutdown = True

        # 取消待执行任务
        if cancel_futures:
            self._cancel_pending_futures()

        # 等待调度线程结束
        if wait:
            self._scheduler_thread.join(timeout=5)

        # 关闭执行器
        self._shutdown_executor(wait, cancel_futures)

    def _cancel_pending_futures(self):
        """取消队列中等待的任务"""
        while not self._task_queue.empty():
            try:
                item = self._task_queue.get_nowait()
                user_future = item[-1]
                if not user_future.done():
                    user_future.cancel()
            except Empty:
                break

    def _shutdown_executor(self, wait: bool, cancel_futures: bool):
        """关闭执行器（子类实现）"""
        pass

    def running_count(self) -> int:
        """获取当前运行中的任务数量"""
        with self._running_lock:
            return len(self._running_futures)

    def pending_count(self) -> int:
        """获取等待中的任务数量"""
        return self._task_queue.qsize()

    def is_full(self) -> bool:
        """判断是否已满"""
        return self.running_count() >= self._max_workers

    def wait_completion(self, timeout: Optional[float] = None):
        """等待所有任务完成"""
        start_time = time.time()
        while True:
            if self._task_queue.empty() and self.running_count() == 0:
                break
            if timeout is not None:
                if time.time() - start_time > timeout:
                    break
            threading.Event().wait(0.1)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown(wait=True)


class PriorityThreadPool(BasePriorityPool):
    """优先级线程池"""

    def __init__(self, max_workers: Optional[int] = None):
        super().__init__(max_workers)
        self._executor = ThreadPoolExecutor(max_workers=self._max_workers)

    def _submit_to_executor(self, fn: Callable, args: tuple, kwargs: dict) -> Future:
        """提交到线程池"""
        return self._executor.submit(fn, *args, **kwargs)

    def _shutdown_executor(self, wait: bool, cancel_futures: bool):
        """关闭线程池"""
        self._executor.shutdown(wait=wait, cancel_futures=cancel_futures)


class PriorityProcessPool(BasePriorityPool):
    """优先级进程池

    注意:
    1. Windows平台需要在 if __name__ == '__main__' 保护下使用
    2. 所有参数和函数必须可pickle序列化
    3. 不支持lambda、内部类等方法
    """

    def __init__(self, max_workers: Optional[int] = None):
        super().__init__(max_workers)
        self._executor = ProcessPoolExecutor(max_workers=self._max_workers)

    def _submit_to_executor(self, fn: Callable, args: tuple, kwargs: dict) -> Future:
        """提交到进程池"""
        return self._executor.submit(fn, *args, **kwargs)

    def _shutdown_executor(self, wait: bool, cancel_futures: bool):
        """关闭进程池"""
        self._executor.shutdown(wait=wait, cancel_futures=cancel_futures)


# class PriorityAsyncPool(BasePriorityPool):
#     """优先级异步协程池
#
#     特性:
#     - 只接受异步函数(async def)
#     - 使用独立的事件循环线程
#     - 支持优先级调度
#     """
#
#     def __init__(self, max_workers: Optional[int] = None):
#         self._max_workers = max_workers or os.cpu_count()
#         self._task_queue = PriorityQueue()
#         self._seq = 0
#         self._shutdown = False
#         self._shutdown_lock = threading.Lock()
#
#         # 异步池专用：信号量控制并发
#         self._semaphore = None
#         self._running_tasks = set()
#         self._running_lock = threading.Lock()
#
#         # 创建事件循环线程
#         self._loop = asyncio.new_event_loop()
#         self._loop_thread = threading.Thread(
#             target=self._run_event_loop,
#             daemon=True
#         )
#         self._loop_thread.start()
#
#         # 等待事件循环就绪并初始化信号量
#         while not hasattr(self, '_loop_ready'):
#             threading.Event().wait(0.01)
#
#         # 在事件循环中创建信号量
#         future = asyncio.run_coroutine_threadsafe(
#             self._init_semaphore(),
#             self._loop
#         )
#         future.result()
#
#         # 启动调度线程
#         self._scheduler_thread = threading.Thread(
#             target=self._scheduler_loop,
#             daemon=True
#         )
#         self._scheduler_thread.start()
#
#     def _run_event_loop(self):
#         """运行事件循环"""
#         asyncio.set_event_loop(self._loop)
#         self._loop_ready = True
#         try:
#             self._loop.run_forever()
#         finally:
#             self._loop.close()
#
#     async def _init_semaphore(self):
#         """初始化信号量"""
#         self._semaphore = asyncio.Semaphore(self._max_workers)
#
#     def submit(self, fn: Callable, *args, priority: int = 5, **kwargs) -> Future:
#         """
#         提交异步任务
#         :param fn: 异步函数(async def)
#         """
#         if not asyncio.iscoroutinefunction(fn):
#             raise TypeError(f"异步池只接受异步函数，但收到了: {fn.__name__ if hasattr(fn, '__name__') else fn}")
#
#         return super().submit(fn, *args, priority=priority, **kwargs)
#
#     def _submit_to_executor(self, fn: Callable, args: tuple, kwargs: dict) -> Future:
#         """
#         提交到异步执行器
#         注意：异步池返回的是包装后的Future，不是真正的执行器Future
#         """
#         # 创建内部Future用于跟踪
#         internal_future = Future()
#
#         # 创建异步任务包装器
#         async def task_wrapper():
#             # 获取信号量控制并发
#             await self._semaphore.acquire()
#             try:
#                 # 执行用户异步函数
#                 result = await fn(*args, **kwargs)
#                 return result
#             finally:
#                 self._semaphore.release()
#
#         # 提交到事件循环
#         coro = task_wrapper()
#         asyncio.run_coroutine_threadsafe(coro, self._loop)
#
#         # 异步池的特殊处理：直接标记为运行中
#         # 实际运行状态由信号量控制
#         internal_future.set_result(None)
#
#         return internal_future
#
#     def _scheduler_loop(self):
#         """异步池调度循环（重写以处理异步特殊性）"""
#         while True:
#             if self._shutdown and self._task_queue.empty():
#                 break
#
#             # 检查是否还有并发槽位
#             with self._running_lock:
#                 running_count = len(self._running_tasks)
#
#             if running_count >= self._max_workers:
#                 threading.Event().wait(0.01)
#                 continue
#
#             try:
#                 item = self._task_queue.get_nowait()
#             except Empty:
#                 threading.Event().wait(0.01)
#                 continue
#
#             priority, seq, fn, args, kwargs, user_future = item
#
#             if user_future.cancelled():
#                 continue
#
#             # 记录运行中的任务
#             task_id = id(user_future)
#             with self._running_lock:
#                 self._running_tasks.add(task_id)
#
#             # 创建异步任务（使用默认参数立即捕获当前变量）
#             async def run_and_callback(
#                     fn=fn, args=args, kwargs=kwargs, user_future=user_future, task_id=task_id
#             ):
#                 try:
#                     await self._semaphore.acquire()
#                     try:
#                         result = await fn(*args, **kwargs)
#                         if not user_future.cancelled():
#                             user_future.set_result(result)
#                     finally:
#                         self._semaphore.release()
#                 except Exception as e:
#                     if not user_future.cancelled():
#                         user_future.set_exception(e)
#                 finally:
#                     with self._running_lock:
#                         self._running_tasks.discard(task_id)
#
#             # 提交到事件循环
#             asyncio.run_coroutine_threadsafe(run_and_callback(), self._loop)
#
#     def _on_task_done(self, executor_future: Future, user_future: Future):
#         """异步池不需要此回调"""
#         pass
#
#     def _shutdown_executor(self, wait: bool, cancel_futures: bool):
#         """关闭异步池"""
#         # 停止事件循环
#         if self._loop.is_running():
#             self._loop.call_soon_threadsafe(self._loop.stop)
#
#         # 等待事件循环线程结束
#         if wait and self._loop_thread.is_alive():
#             self._loop_thread.join(timeout=5)
#
#     def running_count(self) -> int:
#         """获取运行中的任务数"""
#         with self._running_lock:
#             return len(self._running_tasks)
class PriorityAsyncPool(BasePriorityPool):
    """优先级异步协程池

    特性:
    - 只接受异步函数(async def)
    - 使用独立的事件循环线程
    - 支持优先级调度
    """

    def __init__(self, max_workers: Optional[int] = None):
        self._max_workers = max_workers or os.cpu_count()
        self._task_queue = PriorityQueue()
        self._seq = 0
        self._shutdown = False
        self._shutdown_lock = threading.Lock()

        # 添加关闭完成事件
        self._shutdown_complete = threading.Event()

        # 异步池专用：信号量控制并发
        self._semaphore = None
        self._running_tasks = set()
        self._running_lock = threading.Lock()

        # 添加待取消的任务集合
        self._pending_cancel = set()
        self._cancel_lock = threading.Lock()

        # 创建事件循环线程
        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(
            target=self._run_event_loop,
            daemon=True
        )
        self._loop_thread.start()

        # 等待事件循环就绪并初始化信号量
        while not hasattr(self, '_loop_ready'):
            threading.Event().wait(0.01)

        # 在事件循环中创建信号量
        future = asyncio.run_coroutine_threadsafe(
            self._init_semaphore(),
            self._loop
        )
        future.result()

        # 启动调度线程
        self._scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True
        )
        self._scheduler_thread.start()

    def _run_event_loop(self):
        """运行事件循环"""
        asyncio.set_event_loop(self._loop)
        self._loop_ready = True
        try:
            self._loop.run_forever()
        finally:
            # 清理未完成的任务，避免警告
            pending = asyncio.all_tasks(self._loop)
            for task in pending:
                task.cancel()

            # 运行一轮循环让取消生效
            if pending:
                self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

            self._loop.close()

    async def _init_semaphore(self):
        """初始化信号量"""
        self._semaphore = asyncio.Semaphore(self._max_workers)

    @staticmethod
    def is_async_callable(obj):
        """判断对象是否可异步调用"""
        if asyncio.iscoroutinefunction(obj):
            return True
        if callable(obj) and hasattr(obj, '__call__'):
            return asyncio.iscoroutinefunction(obj.__call__)
        return False

    def submit(self, fn: Callable, *args, priority: int = 5, **kwargs) -> Future:
        """
        提交异步任务
        :param fn: 异步函数(async def)
        """
        if not self.is_async_callable(fn):
            raise TypeError(f"异步池只接受异步函数，但收到了: {fn.__name__ if hasattr(fn, '__name__') else fn}")

        return super().submit(fn, *args, priority=priority, **kwargs)

    def _scheduler_loop(self):
        """异步池调度循环（重写以处理异步特殊性）"""
        while True:
            # 检查关闭状态
            if self._shutdown and self._task_queue.empty() and len(self._running_tasks) == 0:
                self._shutdown_complete.set()
                break

            # 检查是否还有并发槽位
            with self._running_lock:
                running_count = len(self._running_tasks)

            if running_count >= self._max_workers:
                threading.Event().wait(0.01)
                continue

            try:
                item = self._task_queue.get_nowait()
            except Empty:
                threading.Event().wait(0.01)
                continue

            priority, seq, fn, args, kwargs, user_future = item

            # 检查是否已取消
            if user_future.cancelled():
                continue

            # 检查是否在待取消列表中
            with self._cancel_lock:
                if user_future in self._pending_cancel:
                    self._pending_cancel.discard(user_future)
                    continue

            # 记录运行中的任务
            task_id = id(user_future)
            with self._running_lock:
                self._running_tasks.add(task_id)

            # 创建异步任务（使用默认参数立即捕获当前变量）
            async def run_and_callback(
                    fn=fn, args=args, kwargs=kwargs, user_future=user_future, task_id=task_id
            ):
                try:
                    # 获取信号量
                    await self._semaphore.acquire()
                    try:
                        # 再次检查取消状态
                        if user_future.cancelled():
                            return
                        # 执行用户异步函数
                        result = await fn(*args, **kwargs)
                        # 检查取消状态后再设置结果
                        if not user_future.cancelled():
                            user_future.set_result(result)
                    finally:
                        self._semaphore.release()
                except asyncio.CancelledError:
                    # 任务被取消，不设置异常
                    if not user_future.cancelled():
                        user_future.cancel()
                except Exception as e:
                    if not user_future.cancelled():
                        user_future.set_exception(e)
                finally:
                    with self._running_lock:
                        self._running_tasks.discard(task_id)
                    # 通知调度线程有槽位释放
                    with self._idle_condition:
                        self._idle_condition.notify()

            # 提交到事件循环
            asyncio.run_coroutine_threadsafe(run_and_callback(), self._loop)

    def _on_task_done(self, executor_future: Future, user_future: Future):
        """异步池不需要此回调"""
        pass

    def _shutdown_executor(self, wait: bool, cancel_futures: bool):
        """关闭异步池（改进版）"""

        if cancel_futures:
            # 取消所有待执行的任务
            self._cancel_pending_futures()

        # 等待调度线程完成所有任务
        if wait:
            # 设置关闭标志并等待调度线程完成
            self._shutdown = True
            self._shutdown_complete.wait(timeout=10)

            # 等待调度线程结束
            if self._scheduler_thread.is_alive():
                self._scheduler_thread.join(timeout=2)

        # 停止事件循环
        if self._loop.is_running():
            # 获取所有运行中的任务并取消
            future = asyncio.run_coroutine_threadsafe(
                self._cancel_all_tasks(),
                self._loop
            )
            try:
                future.result(timeout=5)
            except Exception:
                pass

            # 停止事件循环
            self._loop.call_soon_threadsafe(self._loop.stop)

        # 等待事件循环线程结束
        if wait and self._loop_thread.is_alive():
            self._loop_thread.join(timeout=5)

    async def _cancel_all_tasks(self):
        """取消所有运行中的任务"""
        # 获取当前循环中的所有任务
        tasks = [t for t in asyncio.all_tasks(self._loop)
                 if t is not asyncio.current_task()]

        # 取消所有任务
        for task in tasks:
            task.cancel()

        # 等待所有任务取消完成
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def _cancel_pending_futures(self):
        """取消队列中等待的任务（重写）"""
        with self._cancel_lock:
            while not self._task_queue.empty():
                try:
                    item = self._task_queue.get_nowait()
                    user_future = item[-1]
                    if not user_future.done():
                        user_future.cancel()
                        self._pending_cancel.add(user_future)
                except Empty:
                    break

    def running_count(self) -> int:
        """获取运行中的任务数"""
        with self._running_lock:
            return len(self._running_tasks)

    def shutdown(self, wait: bool = True, cancel_futures: bool = False):
        """
        关闭任务池（重写基类方法）
        :param wait: 是否等待所有任务完成
        :param cancel_futures: 是否取消待执行的任务
        """
        with self._shutdown_lock:
            if self._shutdown:
                return
            self._shutdown = True

        # 取消待执行任务
        if cancel_futures:
            self._cancel_pending_futures()

        # 等待调度线程完成
        if wait:
            self._shutdown_complete.wait(timeout=10)
            if self._scheduler_thread.is_alive():
                self._scheduler_thread.join(timeout=2)

        # 关闭执行器
        self._shutdown_executor(wait, cancel_futures)


class TaskManageBase:
    """
    任务管理类基类
    submit_task方法为对外提交任务方法
    内部由_pool_submit负责执行具体任务池的提交
    子类需要更改提交任务逻辑重写_pool_submit方法即可
    """
    all_manage: WeakSet['TaskManageBase'] = WeakSet()  # 全部任务管理类,弱引用
    __class_lock = threading.Lock()

    def __init__(self, num_work: int = None):
        self.isStop = False  # 是否停止
        self.num_work = os.cpu_count() if num_work is None else num_work
        self.pool: Optional[BasePriorityPool] = self.create_pool(self.num_work)
        # 存储了全部未完成的Task任务
        self.__all_tasks: set[Task] = set()
        self.__lock = threading.Lock()
        with self.__class__.__class_lock:
            self.__class__.all_manage.add(self)

    def create_pool(self, num_work: int) -> PriorityThreadPool:
        """创建内部池的方法"""
        return PriorityThreadPool(num_work)

    def __add(self, task):
        with self.__lock:
            self.__all_tasks.add(task)

    def __discard(self, task):
        with self.__lock:
            self.__all_tasks.discard(task)

    def set_num_work(self, value: int):
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
        func, args, kwargs = task.executor.get_func()
        if task.retry_count > 0:
            task_retry = TaskRetry(
                func=func,
                args=args,
                kwargs=kwargs,
                retry_count=task.retry_count,
                retry_should=task.retry_should
            )
            return self.pool.submit(task_retry, priority=priority)
        else:
            return self.pool.submit(func, *args, priority=priority, **kwargs)

    def stop(self):
        """停止"""
        try:
            self.isStop = True
            with self.__lock:
                for task in self.__all_tasks.copy():
                    task.stop()
            self.pool.shutdown(wait=False, cancel_futures=True)
            with self.__class__.__class_lock:
                self.__class__.all_manage.discard(self)
        except Exception as e:
            logger.exception(f'{self.__class__.__name__}.stop() 错误: {e}')

    @classmethod
    def stop_all(cls):
        """停止全部任务管理类"""
        with cls.__class_lock:
            manages = cls.all_manage.copy()
        for manage in manages:
            manage.stop()

    # ========== 新增方法 ==========
    @property
    def running_cnt(self) -> int:
        """获取当前运行的任务数量"""
        return self.pool.running_count()

    @property
    def pending_count(self) -> int:
        """获取等待任务数量"""
        return self.pool.pending_count()

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


# 优先级任务管理类
class TaskManage(TaskManageBase):
    """任务管理类（多线程）"""

    def __init__(self, num_work: int = None):
        super().__init__(num_work)

    def create_pool(self, num_work: int):
        return PriorityThreadPool(max_workers=num_work)


class TaskProcessManage(TaskManageBase):
    """任务管理类（多进程）"""

    def __init__(self, num_work: int = None):
        super().__init__(num_work)

    def create_pool(self, num_work: int):
        return PriorityProcessPool(max_workers=num_work)


class TaskAsyncManage(TaskManageBase):
    """任务管理类（异步协程）"""

    def __init__(self, num_work: int = None):
        super().__init__(num_work)

    def create_pool(self, num_work: int):
        return PriorityAsyncPool(max_workers=num_work)

    def _pool_submit(self, task: 'Task', priority=5):
        func, args, kwargs = task.executor.get_func()
        if task.retry_count > 0:
            task_retry = TaskRetryAsync(
                func=func,
                args=args,
                kwargs=kwargs,
                retry_count=task.retry_count,
                retry_should=task.retry_should
            )
            return self.pool.submit(task_retry, priority=priority)
        else:
            return self.pool.submit(func, *args, priority=priority, **kwargs)


# 信号类
class TaskSignalExecutor:
    """全局信号执行器，所有信号实例共享同一个线程"""

    def __init__(self):
        self.task_queue = queue.Queue()
        self.isRunning = True
        self.worker_thread = threading.Thread(
            target=self._worker_loop, name=f'{self.__class__.__name__}.信号线程', daemon=True)
        self.worker_thread.start()

    @staticmethod
    def execute_func(func: Callable, *args):
        """执行单个槽函数，自动判断参数"""
        try:
            try:
                func(*args)
            except TypeError:
                func()
        except RuntimeError as e:
            if 'Signal source has been deleted' not in str(e):
                raise e

    def _worker_loop(self):
        """工作线程主循环"""
        while self.isRunning:
            try:
                task = self.task_queue.get(timeout=0.2)
                if task is None:  # 退出信号
                    break
                # 支持批量执行
                for func, args in task:
                    try:
                        self.execute_func(func, *args)
                    except Exception:
                        logger.exception(f'{self.__class__.__name__} 槽函数执行错误'
                                         f'函数: {func} 位置参数{args}')
                self.task_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.exception(f'{self.__class__.__name__} 工作线程错误{e}')

    def submit(self, func: Callable, *args):
        """提交单个任务到队列"""
        self.task_queue.put((func, args))

    def submit_emit(self, funcs: Iterable[Callable], *args):
        """
        批量提交信号发射任务

        :param funcs: 槽函数列表
        :param args: 位置参数
        :param kwargs: 关键词参数
        """
        if not funcs:
            return

        # 直接提交(func, args)对，不做参数判断
        tasks = [(func, args) for func in funcs]
        self.task_queue.put(tasks)

    def shutdown(self):
        """关闭执行器"""
        self.isRunning = False
        self.task_queue.put(None)
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2)


class TaskSignal:
    """
    仿Qt信号类
    支持强/弱引用(默认强引用)
    所有槽函数在同一后台线程执行,请勿执行阻塞函数
    槽函数可选择不接受参数
    一旦接受必须符合
    """

    _executor = TaskSignalExecutor()  # 共享执行器

    def __init__(self, use_weak: bool = False, is_shared=False, name=None):
        """
        :param use_weak: True=弱引用 False=强引用(默认)
        :param is_shared:是否是共享信号类,注意管理生命周期
        """
        self._use_weak = use_weak
        self._is_shared = is_shared
        self._slots: set[Callable] = set()  # 存储函数或弱引用
        self._lock = threading.RLock()
        self.name = name or f'{self.__class__.__name__}_{hex(id(self))}'

    def set_name(self, name):
        self.name = name

    def emit(self, *args):
        """发送信号"""
        slots = self.clear_dead_slot()
        self._executor.submit_emit(slots, *args)

    def connect(self, func: Callable, use_weak=None, enable_strict_repeat=False) -> ReferenceType | None:
        """
        连接槽函数
        :param use_weak:是否使用弱引用,为None根据全局配置来使用
        :param enable_strict_repeat:是否启用严格重复检查(默认判断是否重复采用内存地址是否一致,启用严格检查后同名函数算重复)
        :return :使用弱引用时返回弱引用对象,用于解除连接
        """
        if not callable(func):
            raise TypeError("槽函数必须是可调用的")
        is_add = True  # 是否添加
        with self._lock:
            use_weak = self._use_weak if use_weak is None else use_weak
            if use_weak:
                func = weakref.ref(func)  # 弱引用
            for slot in self._slots:
                if not isinstance(slot, ReferenceType) and self._is_same_closure(slot, func):
                    if enable_strict_repeat:
                        is_add = False
                    else:
                        logger.debug(f'{repr(self)}'
                                     f'存在同名函数重复添加,可能造成槽函数溢出'
                                     f'即将连接的槽函数{func}|已连接槽函数数量{len(self)}')
            if is_add:
                self._slots.add(func)
            if use_weak:
                return func

    def _is_same_closure(self, func1, func2):
        """判断两个闭包函数是否相同"""
        if func1 is func2:
            return True
        # 比较函数名
        if func1.__name__ != func2.__name__:
            return False
        # 比较代码对象
        # if func1.__code__ != func2.__code__:
        #     return False
        # 比较闭包变量
        # if func1.__closure__ != func2.__closure__:
        #     return False
        return True

    def connect_once(self, func: Callable):
        """单次连接，执行一次后自动断开"""

        def wrapper(*args):
            try:
                TaskSignalExecutor.execute_func(func, *args)
            except Exception as e:
                logger.exception(f'{self.__class__.__name__} 槽函数执行错误{e}')
            finally:
                self.disconnect(wrapper)

        return self.connect(wrapper, use_weak=False)

    def disconnect(self, func: Callable | ReferenceType = None, compulsory=False):
        """
        断开连接，func为None时断开所有
        :param compulsory:是否强制清理,如果信号为共享信号默认不会清理
        """
        with self._lock:
            if func is None:
                if self._is_shared and not compulsory:
                    logger.debug(f'{self.name} 共享信号无法自动清理全部槽函数,请使用compulsory参数')
                    return
                self._slots.clear()
            else:
                self._slots.discard(func)

    def bridge_signal(self, signal, use_weak=None, enable_strict_repeat=False):
        """桥接到另一个信号"""
        self.connect(signal.emit, use_weak, enable_strict_repeat)

    def transfer_to(self, target_signal: 'TaskSignal',
                    disconnect_original: bool = True,
                    enable_strict_repeat: bool = False) -> int:
        """
        将当前信号的所有槽函数转移到目标信号

        :param target_signal: 目标信号
        :param disconnect_original: 转移后是否断开原信号的连接（默认True）
        :param enable_strict_repeat: 是否启用严格重复检查（默认False）
        :return: 成功转移的槽函数数量
        """
        if not isinstance(target_signal, TaskSignal):
            raise TypeError(f"target_signal 必须是 TaskSignal 类型，收到: {type(target_signal).__name__}")

        if target_signal is self:
            logger.debug(f'{self.name} 不能转移到自身')
            return 0

        transferred_count = 0

        # 获取所有有效的槽函数
        with self._lock:
            slots_snapshot = self._slots.copy()

        for slot in slots_snapshot:
            try:
                if isinstance(slot, ReferenceType):
                    # 弱引用槽函数：解引用后以弱引用方式连接到目标
                    func = slot()
                    if func is None:
                        # 弱引用已失效，跳过
                        continue
                    # 以弱引用方式连接到目标信号
                    target_signal.connect(func, use_weak=True, enable_strict_repeat=enable_strict_repeat)
                else:
                    # 强引用槽函数：直接以强引用方式连接到目标
                    target_signal.connect(slot, use_weak=False, enable_strict_repeat=enable_strict_repeat)

                transferred_count += 1
            except Exception as e:
                logger.exception(f'{self.name} 转移槽函数失败: {e}')
                continue

        # 如果需要断开原连接
        if disconnect_original:
            self.disconnect(compulsory=True)

        logger.debug(f'{self.name} 转移 {transferred_count} 个槽函数到 {target_signal.name}')
        return transferred_count

    def clear_dead_slot(self) -> set[Callable]:
        """清理死亡的弱引用槽函数,返回可用的槽函数集合"""
        # 清理已死亡弱引用
        _slots = self._slots.copy()
        slots = set()  # 存储有效的槽函数
        for slot in _slots:
            if isinstance(slot, ReferenceType):
                func = slot()
                if func is None:
                    self._slots.remove(slot)
                else:
                    slots.add(func)
            else:
                slots.add(slot)
        return slots

    def get_slots(self):
        """获取可用的槽函数"""
        return self.clear_dead_slot()

    def __len__(self):
        return len(self.clear_dead_slot())

    def __contains__(self, item):
        return item in self._slots

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'{self._use_weak},'
                f'{self._is_shared},'
                f'{self.name}) 连接的槽函数{self._slots}')

    def __del__(self):
        self.disconnect()


# 任务类及其属性类
class TaskRetry:
    """支持重试的工作函数包装器"""

    def __init__(self,
                 func,
                 args: tuple = None,
                 kwargs: dict = None,
                 retry_count: int = 0,
                 retry_should: Callable = None):
        """
        重试任务函数,任务函数或者retry_should函数发生异常时之间返回,不再重试
        :param func:任务函数
        :param args:参数
        :param kwargs:参数
        :param retry_count:重试次数,默认为0即不重试
        :param retry_should:重试条件,默认通过判断func返回值是None则重试,否则不重试
                            如果指定重试条件判断函数,True表示不重试,False表示重试
        """
        self.__func = func
        self.__args = args or ()
        self.__kwargs = kwargs or {}
        self.__last_result = None  # 任务执行结果
        self.__retry_count = retry_count
        self.__retry_should = retry_should

    def __execute(self) -> Any | None:
        for count in range(self.__retry_count + 1):
            try:
                self.__last_result = self.__func(*self.__args, **self.__kwargs)
                # 判断是否重试
                if self.__retry_should is None:
                    if self.__last_result is not None:
                        break
                else:
                    if self.__retry_should(self.__last_result):
                        break
                logger.debug(f"任务 {self.__func.__name__} 第{count + 1}次重试")
            except Exception as e:
                logger.exception(f"任务 {self.__func.__name__} 第{count + 1}次重试异常: {e}")
                break
        return self.__last_result

    async def __execute_async(self) -> Any | None:
        for count in range(self.__retry_count + 1):
            try:
                self.__last_result = await self.__func(*self.__args, **self.__kwargs)
                # 判断是否重试
                if self.__retry_should is None:
                    if self.__last_result is not None:
                        break
                else:
                    if self.__retry_should(self.__last_result):
                        break
                logger.debug(f"任务 {self.__func.__name__} 第{count + 1}次重试")
            except Exception as e:
                logger.exception(f"任务 {self.__func.__name__} 第{count + 1}次重试异常: {e}")
                break
        return self.__last_result

    def set_retry_count(self, retry_count: int):
        """设置重试次数"""
        self.__retry_count = retry_count

    def set_retry_should(self, retry_should: Callable):
        """
        设置重试判断函数
        返回Ture表示不重试,False表示重试
        """
        self.__retry_should = retry_should

    def __call__(self):
        return self.__execute()

    def __await__(self):
        return self.__execute_async()


class TaskRetryAsync(TaskRetry):
    """伪装成异步函数的类,支持重试的工作函数包装器"""

    async def __call__(self):
        return await self.__await__()


class TaskEnum:
    """任务枚举统一入口"""

    class Status(Enum):
        """任务状态"""
        RUNNING = 0  # 运行中
        PAUSED = 1  # 暂停中
        STOPPED = 2  # 已停止
        ERROR = 3  # 错误
        CANCELED = 4  # 已取消
        FINISHED = 5  # 已完成
        CLEAR = 6  # 已清理

    class Priority(Enum):
        """任务优先级（1-10，1最高）"""
        HIGHEST = 1
        HIGH = 2
        NORMAL = 5
        LOW = 8
        LOWEST = 10

    class Type(Enum):
        """任务类型"""
        THREAD = 0  # 线程任务
        PROCESS = 1  # 进程任务
        ASYNC = 2  # 异步任务


class TaskProgress:
    """任务进度"""

    def __init__(self):
        self.__lock = threading.Lock()
        self.__total = 0  # 任务总量
        self.__finished = 0  # 已完成数量
        self.__rate = 0  # 速率

    def get_progress(self) -> int:
        """获取百分制进度"""
        with self.__lock:
            value = int((self.__finished / self.__total) * 100) if self.__total != 0 else 0
            return value

    def set_progress(self, progress: 'TaskProgress'):
        with self.__lock:
            self.__total = progress.total
            self.__finished = progress.finished
            self.__rate = progress.rate

    @property
    def total(self) -> int | float:
        """获取任务总量"""
        with self.__lock:
            return self.__total

    @total.setter
    def total(self, value: int | float):
        if not isinstance(value, (int, float)):
            raise TypeError(f'参数只能为数字 {value}')
        with self.__lock:
            self.__total = value

    @property
    def finished(self) -> int | float:
        with self.__lock:
            return self.__finished

    @finished.setter
    def finished(self, value: int | float):
        if not isinstance(value, (int, float)):
            raise TypeError(f'参数只能为数字 {value}')
        with self.__lock:
            self.__finished = value

    @property
    def rate(self) -> int | float:
        with self.__lock:
            return self.__rate

    @rate.setter
    def rate(self, value: int | float):
        if not isinstance(value, (int, float)):
            raise TypeError(f'参数只能为数字 {value}')
        with self.__lock:
            self.__rate = value

    def __str__(self):
        with self.__lock:
            return f'已完成:{self.__finished} 总计:{self.__total} 速率:{self.__rate}'

    def __repr__(self):
        return f'已完成:{self.__finished} 总计:{self.__total} 速率:{self.__rate}'

    def __eq__(self, other):
        with self.__lock:
            return all([self.__total == other.total,
                        self.__finished == other.finished,
                        self.__rate == other.rate])


class TaskSignalParams:
    """Task类内部的信号参数"""

    def __init__(self, is_shared=False):
        """
        :param is_shared:是否是共享信号类
        """
        self.is_shared = is_shared
        self.start_signal = TaskSignal(is_shared=is_shared, name='start_signal')  # 任务开始信号
        self.progress_signal = TaskSignal(is_shared=is_shared, name='progress_signal')  # 任务进度信号
        self.finish_signal = TaskSignal(is_shared=is_shared, name='finish_signal')  # 任务完成信号
        self.stop_signal = TaskSignal(is_shared=is_shared, name='stop_signal')  # 任务停止信号
        self.clear_signal = TaskSignal(is_shared=is_shared, name='clear_signal')  # 任务清理信号

    def set_start(self, signal: TaskSignal):
        self.start_signal = signal

    def set_progress(self, signal: TaskSignal):
        self.progress_signal = signal

    def set_finish(self, signal: TaskSignal):
        self.finish_signal = signal

    def set_stop(self, signal: TaskSignal):
        self.stop_signal = signal

    def set_clear(self, signal: TaskSignal):
        self.clear_signal = signal

    def bridge_other_signal(self, signal: 'TaskSignalParams'):
        """
        桥接其他信号
        等价于start_signal.connect(signal.start_signal.emit)
        """
        self.start_signal.bridge_signal(signal.start_signal)
        self.progress_signal.bridge_signal(signal.progress_signal)
        self.finish_signal.bridge_signal(signal.finish_signal)
        self.stop_signal.bridge_signal(signal.stop_signal)
        self.clear_signal.bridge_signal(signal.clear_signal)

    def clear(self, compulsory=False):
        """清空信号"""
        self.start_signal.disconnect(compulsory=compulsory)
        self.progress_signal.disconnect(compulsory=compulsory)
        self.finish_signal.disconnect(compulsory=compulsory)
        self.stop_signal.disconnect(compulsory=compulsory)
        self.clear_signal.disconnect(compulsory=compulsory)


class TaskStateParams:
    """任务状态参数"""

    def __init__(self):
        self.__lock = threading.Lock()
        self.__current_state = TaskEnum.Status.STOPPED

    @property
    def state(self) -> TaskEnum.Status:
        with self.__lock:
            return self.__current_state

    @state.setter
    def state(self, value: TaskEnum.Status):
        if not isinstance(value, TaskEnum.Status):
            raise TypeError(f'状态必须为TaskEnum.Status类型，收到: {type(value).__name__}')
        with self.__lock:
            self.__current_state = value

    @property
    def isRunning(self) -> bool:
        with self.__lock:
            return self.__current_state == TaskEnum.Status.RUNNING

    @property
    def isPaused(self) -> bool:
        with self.__lock:
            return self.__current_state == TaskEnum.Status.PAUSED

    @property
    def isStopped(self) -> bool:
        with self.__lock:
            return self.__current_state == TaskEnum.Status.STOPPED

    @property
    def isError(self) -> bool:
        with self.__lock:
            return self.__current_state == TaskEnum.Status.ERROR

    @property
    def isCanceled(self) -> bool:
        with self.__lock:
            return self.__current_state == TaskEnum.Status.CANCELED

    @property
    def isFinished(self) -> bool:
        with self.__lock:
            return self.__current_state == TaskEnum.Status.FINISHED

    @property
    def isClear(self) -> bool:
        with self.__lock:
            return self.__current_state == TaskEnum.Status.CLEAR

    @property
    def isUsable(self) -> bool:
        """判断当前是否可使用"""
        with self.__lock:
            return self.__current_state in (
                TaskEnum.Status.RUNNING,
                TaskEnum.Status.PAUSED,
                TaskEnum.Status.STOPPED,
                TaskEnum.Status.FINISHED,
                TaskEnum.Status.ERROR,
                TaskEnum.Status.CANCELED
            )

    def set_running(self):
        with self.__lock:
            self.__current_state = TaskEnum.Status.RUNNING

    def set_stopped(self):
        with self.__lock:
            self.__current_state = TaskEnum.Status.STOPPED

    def set_finished(self):
        with self.__lock:
            self.__current_state = TaskEnum.Status.FINISHED

    def set_error(self):
        with self.__lock:
            self.__current_state = TaskEnum.Status.ERROR

    def set_canceled(self):
        with self.__lock:
            self.__current_state = TaskEnum.Status.CANCELED

    def set_paused(self):
        with self.__lock:
            self.__current_state = TaskEnum.Status.PAUSED

    def set_clear(self):
        with self.__lock:
            self.__current_state = TaskEnum.Status.CLEAR

    def reset(self):
        with self.__lock:
            self.__current_state = TaskEnum.Status.STOPPED

    def __str__(self) -> str:
        with self.__lock:
            return f"状态:{self.__current_state.name}"

    def __repr__(self) -> str:
        return self.__str__()


class TaskExecutor:
    """
    任务执行器 - 负责任务函数的执行和结果管理

    职责：
    1. 存储任务函数和参数
    2. 管理 Future 对象
    3. 管理回调函数,默认传递TaskExecutor所属的Task类,可以选择接受或不接受
    4. 管理运行次数
    5. 提供 __call__ 方法供线程/进程池调用
    """

    def __init__(self,
                 func: Callable,
                 task: 'Task',
                 args: tuple | Any = (),
                 kwargs: dict = None,
                 name: str = None):
        """
        初始化任务执行器
        :param func: 任务函数
        :param task: 所属Task类
        :param args: 位置参数
        :param kwargs: 关键字参数
        :param name: 任务名称
        """
        self.__func = func
        self.__args = args if isinstance(args, tuple) else (args,)
        self.__kwargs = kwargs if kwargs is not None else {}
        # 尝试获取对象的__name__属性,如果属性不存在则返回str(func)
        self.__name = name or getattr(func, '__name__', str(func))
        self.__future: Optional[Future] = None
        self.__callback_func: set[Callable] = set()
        self.__run_count = 0  # 运行次数
        self.__lock = threading.RLock()
        # 注册内部回调时使用弱引用包装
        self.__weak_task: Optional['Task'] = weakref.ref(task)

    @property
    def name(self) -> str:
        """获取任务名称"""
        return self.__name

    @name.setter
    def name(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f'任务名称必须为str类型，收到: {type(value).__name__}')
        with self.__lock:
            self.__name = value

    @property
    def run_count(self) -> int:
        """获取运行次数"""
        with self.__lock:
            return self.__run_count

    @run_count.setter
    def run_count(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f'运行次数必须为int类型，收到: {type(value).__name__}')
        with self.__lock:
            self.__run_count = value

    # Future对象
    @property
    def future(self) -> Future | None:
        """获取 Future 对象"""
        with self.__lock:
            if not self.future_valid():
                return None
            return self.__future

    def submit_task(self, task_manage: TaskManageBase, priority=5) -> bool:
        """提交任务 - 产生Future"""
        with self.__lock:
            if self.__future is not None:
                self.cancel_future()
            self.__run_count += 1
            # 提交任务
            self.__future = task_manage.submit_task(self.__weak_task(), priority)
            # 注册回调函数
            self.register_callbacks_to_future()
            if self.__future is not None:
                return True
            logger.warning(f"{self.__class__.__name__} {self.name} 提交任务失败")
            return False

    def future_valid(self) -> bool:
        """
        检查 Future 对象 是否可使用
        可用标准
            - 任务提交
            - 任务已完成
            - 任务未被取消
        """
        with self.__lock:
            if self.__future is None:
                return False
            else:
                return all(
                    [not self.__future.cancelled(),
                     self.__future.done()]
                )

    def get_func(self) -> tuple[Callable, tuple, dict]:
        """获取任务函数及其参数"""
        return self.__func, self.__args, self.__kwargs

    def __call__(self):
        """执行任务函数，供线程/进程池调用"""
        return self.__func(*self.__args, **self.__kwargs)

    # 结果
    def _result_wait(self, timeout: float | int, parent_task: 'Task' = None):
        """返回是否等待"""
        if isinstance(timeout, (float, int)):
            timeout = max(timeout, 0)
            # 任务正在运行且没有被取消
            start_time = time.time()
            task = self.__weak_task()
            while task.state.isRunning and not self.done_future():
                if parent_task is not None and not parent_task.state.isRunning:
                    yield False
                if timeout != 0 and time.time() - start_time >= timeout:
                    yield False
                else:
                    yield True
        yield False

    def result(self, timeout: float | int = None, parent_task: 'Task' = None) -> Any | None:
        """
        获取任务结果
        :param timeout:是否等待任务完成,支持输入float|int值,0为无限等待,默认不等待,等待时返回任务结果,超时时会停止当前任务
        :param parent_task:关联父任务,用于父任务被停止时关闭阻塞中的子任务,timeout>=0时生效
        """
        try:
            # Future可用时直接返回任务结果
            if self.future_valid():
                return self.__future.result()
            # 等待结果
            if timeout is not None and isinstance(timeout, (float, int)):
                for state in self._result_wait(timeout, parent_task):
                    if state:
                        time.sleep(0.1)
                    else:
                        if self.future_valid():
                            return self.__future.result()
                        return None
        except Exception as e:
            logger.exception(f'{self.__class__.__name__}.result 错误{e}')
        return None

    async def result_async(self, timeout: float | int = None, parent_task: 'Task' = None) -> Any | None:
        """
        异步获取任务结果（非阻塞等待）

        :param timeout: 超时时间（秒），0表示无限等待，None表示立即返回（不等待）
        :param parent_task: 关联父任务，父任务停止时自动停止当前任务
        :return: 任务结果，超时、失败或未启动时返回None

        使用示例:
            # 在异步函数中使用
            async def my_async_func():
                task = SomeTask(...)
                task.start_async()
                result = await task.async_result(timeout=30)

            # 在普通函数中使用（需要事件循环）
            import asyncio
            result = asyncio.run(task.async_result(timeout=30))

        注意:
            - 该方法不会阻塞线程池工作线程，适合在异步池中调用
            - 父任务应该在异步池中运行，子任务在线程池中运行，避免死锁
        """
        # 参数验证
        if timeout is not None and not isinstance(timeout, (int, float)):
            raise TypeError(f"timeout 必须是数字或None，收到: {type(timeout).__name__}")
        try:
            # Future可用时直接返回任务结果
            if self.future_valid():
                return self.__future.result()
            # 等待结果
            if timeout is not None and isinstance(timeout, (float, int)):
                for state in self._result_wait(timeout, parent_task):
                    if state:
                        await asyncio.sleep(0.1)
                    else:
                        if self.future_valid():
                            return self.__future.result()
        except asyncio.CancelledError:
            # 协程被取消，停止任务并重新抛出异常
            logger.debug(f"异步等待被取消: {self.name}")
            raise  # 必须重新抛出，保持协程取消语义
        except Exception as e:
            logger.exception(f'{self.__class__.__name__}.async_result 错误: {e}')
        return None

    def set_result(self, result) -> bool:
        """
        设置任务结果，必须在任务结束后才可设置
        :param result: 任务结果
        """
        with self.__lock:
            if self.future_valid():
                self.__future.set_result(result)
                return True
            logger.debug(f"{self.__class__.__name__} {self.name} 的 Future 对象不可用,无法设置结果")
            return False

    # 状态
    def done_future(self) -> bool:
        """任务是否完成"""
        with self.__lock:
            if self.__future is not None:
                return self.__future.done()
            return False

    def cancel_future(self) -> bool:
        """取消任务"""
        with self.__lock:
            if self.__future is not None and not self.__future.done():
                return self.__future.cancel()
            return False

    # 回调处理
    def _executor_callback(self, callback: Callable):
        try:
            try:
                # 尝试带参数调用
                callback(self.__weak_task())
            except TypeError:
                # 如果因为参数错误，尝试无参调用
                callback()
        except Exception as e:
            logger.exception(f'{self.__name}回调执行错误: {e}')

    def add_done_callback(self, callback: Callable):
        """添加完成回调"""
        self.__callback_func.add(callback)
        if self.future_valid():
            self._executor_callback(callback)

    def register_callbacks_to_future(self) -> bool:
        """将回调函数注册到 Future 对象"""

        def safe_callback(future: Future):
            """安全的回调包装器"""
            if future.cancelled():
                logger.debug(f"{self.__name} Future已被取消,跳过回调")
                return
            for callback in self.__callback_func:
                self._executor_callback(callback)

        with self.__lock:
            if self.__future is None:
                return False

            self.__future.add_done_callback(safe_callback)
            return True

    def clear_callbacks(self):
        """清空所有回调函数"""
        self.__callback_func.clear()

    # 清理
    def reset(self):
        """重置执行器（清空 Future 和回调，保留函数和参数）"""
        self.cancel_future()
        self.__future = None
        self.__callback_func.clear()

    def clear(self):
        """完全清理执行器"""
        self.cancel_future()
        self.__future = None
        self.__callback_func.clear()
        self.__func = None
        self.__args = ()
        self.__kwargs = {}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.__name}' run_count={self.__run_count} done={self.done_future()}>"


class Task:
    """
    基本说明:
        任务类,所有继承该类的都带有四个信号,开始、进度、完成、停止、清理
        支持协程/多线程/多进程,提交到不同的管理类中将即可,
        如果是异步则传入的函数支持异步写法
        内部复杂属性都已经差分为独立的类进行管理,如传入TaskSignalParams即内部不会再创建信号
    使用方法说明:
        传入参数后调用start方法(具有同步和异步,以及是否阻塞的等)
        使用完后最好显示调用clear方法清理资源
        或使用with语句+阻塞等待方法来使用(退出时自动清理资源)
    重试设置说明:
        重试实现是将任务函数通过TaskRetry包装后的一个整体
        执行重试期间不受Task类状态影响(理论上应该是处于RUNNING状态)
        如果需要停止任务时打断重试可以在自定义的retry_should函数中检查任务状态
    多进程问题:
        如果func或retry_should函数不是模块级函数或者是类方法/静态方法之类的
        任务可能无法使用多进程完成
    信号说明:
        如果没有特殊声明,默认发送自身
        start_signal,开始信号,发送自身
        progress_signal,进度信号,需要在func函数中自定义
        finish_signal,完成信号,发送自身
        stop_signal,停止信号,发送自身
        clear_signal,清理信号,发送自身
        自带的信号由独立的单线程维护不用考虑线程安全,
        添加的回调函数由各自任务所在的线程池/进程池维护,需要考虑线程安全
        高耗时任务使用add_done_callback添加回调
    执行状态:
        isRunning属性(只读且子类无法修改)用于判断任务是否正在运行
        任务调用了start方法后isRunning将变为True
        任务完成后isRunning将变为False,依赖finish_signal信号修改
    任务管理类参数说明:
        如果不指定任务管理类,默认会在内部创建一个线程管理类
        通过use_process或use_async参数指定默认创建的管理类类型
    """

    def __init__(self, func: Callable | TaskExecutor,
                 task_manage: 'TaskManageBase' = None,
                 name: str = None,
                 use_process: bool = False,
                 use_async: bool = False,
                 args: tuple | Any = (),
                 kwargs: dict = None,
                 parent_task: 'Task' = None,
                 signal: TaskSignalParams = None,
                 progress: TaskProgress = None,
                 retry_count: int = 0,
                 retry_should: Callable = None):
        """
        :param func:任务函数或任务执行器
        :param task_manage:任务池,不传入时内部创建一个单线程任务池,启用use_process时使用子进程任务池
        :param name:任务名称,默认使用任务函数名称
        :param use_process:是否使用多进程模式
        :param args: 任务函数所需要的参数,单个参数直接传递,多参数元组传递
        :param kwargs:任务函数所需要的参数
        :param parent_task:关联的父对象,任务启动会检查父对象是否被停止或清理,父对象停止或清理会同步关闭子任务或清理子任务
        :param signal:传入指定的信号参数,默认内部创建独立的信号
        :param progress:传入指定的进度参数,默认内部创建独立的进度参数
        :param retry_should:重试条件,默认通过判断func返回值的bool值为False时重试
                            如果指定重试条件判断函数,True表示不重试,False表示重试
        """
        # 创建执行器
        if isinstance(func, TaskExecutor):
            self.__executor = func
        else:
            self.__executor = TaskExecutor(func, self, args, kwargs, name)
        self.__retry_count = retry_count
        self.__retry_should = retry_should
        self.__executor.add_done_callback(self.__finished_slot)  # 任务完成信号槽
        # 创建任务管理器
        self.__need_delete_task_manage = False  # 是否需要删除任务管理器
        self.__task_manage = self.__create_task_manage(use_process, use_async) if task_manage is None else task_manage
        # 状态属性
        self.__state = TaskStateParams()  # 状态属性
        self.__progress = TaskProgress() if progress is None else self.set_progress(progress)  # 进度属性
        # 信号的槽函数由单独的线程维护,循环调用会导致信号发送阻塞,这时请使用add_done_callback
        self.__signal = TaskSignalParams() if signal is None else self.set_signal(signal)  # 信号参数
        at = hex(id(self))
        # 设置名称
        self.__signal.start_signal.set_name(f'{self.__signal.start_signal.name}->Parent:{self.__class__.__name__}_{at}')
        self.__signal.progress_signal.set_name(
            f'{self.__signal.progress_signal.name}->Parent:{self.__class__.__name__}_{at}')
        self.__signal.finish_signal.set_name(
            f'{self.__signal.finish_signal.name}->Parent:{self.__class__.__name__}_{at}')
        self.__signal.stop_signal.set_name(f'{self.__signal.stop_signal.name}->Parent:{self.__class__.__name__}_{at}')
        self.__signal.clear_signal.set_name(f'{self.__signal.clear_signal.name}->Parent:{self.__class__.__name__}_{at}')

        self.__parent_task = None
        self.__sub_tasks: WeakSet[Task] = WeakSet()  # 子任务
        if parent_task is not None:
            self.set_parent_task(parent_task)

    # ----------基本属性----------
    @property
    def name(self) -> str:
        return self.__executor.name

    @name.setter
    def name(self, value: str):
        self.__executor.name = value

    @property
    def retry_count(self) -> int:
        return self.__retry_count

    @property
    def retry_should(self) -> Optional[Callable] | None:
        return self.__retry_should

    @property
    def parent_task(self) -> Optional['Task'] | None:
        """安全的获取父任务"""
        if self.__parent_task is None:
            return None
        return self.__parent_task()  # 可能返回 None

    @property
    def state(self) -> TaskStateParams:
        return self.__state

    @property
    def executor(self) -> TaskExecutor:
        return self.__executor

    @property
    def manage(self) -> TaskManageBase:
        """获取任务管理类"""
        return self.__task_manage

    @property
    def signal(self) -> TaskSignalParams:
        return self.__signal

    @property
    def progress(self) -> TaskProgress:
        return self.__progress

    @property
    def isRunning(self) -> bool:
        return self.__state.isRunning

    @property
    def countRun(self) -> int:
        return self.__executor.run_count

    @countRun.setter
    def countRun(self, value: int):
        self.__executor.run_count = value

    @property
    def start_signal(self) -> TaskSignal:
        return self.__signal.start_signal

    @property
    def progress_signal(self) -> TaskSignal:
        return self.__signal.progress_signal

    @property
    def finish_signal(self) -> TaskSignal:
        return self.__signal.finish_signal

    @property
    def stop_signal(self) -> TaskSignal:
        return self.__signal.stop_signal

    @property
    def clear_signal(self) -> TaskSignal:
        return self.__signal.clear_signal

    @property
    def sub_tasks(self) -> WeakSet:
        return self.__sub_tasks.copy()

    def get_progress(self) -> int:
        """获取百分制进度"""
        return self.__progress.get_progress()

    # ----------设置方法----------
    def set_result(self, result) -> bool:
        """
        设置任务结果，必须在任务结束后才可设置
        :param result: 任务结果
        """
        return self.__executor.set_result(result)

    def set_signal(self, signal: TaskSignalParams) -> TaskSignalParams:
        """设置信号参数"""
        if isinstance(signal, TaskSignalParams):
            # 转移原有信号的槽函数
            self.__signal.start_signal.transfer_to(signal.start_signal)
            self.__signal.progress_signal.transfer_to(signal.progress_signal)
            self.__signal.finish_signal.transfer_to(signal.finish_signal)
            self.__signal.stop_signal.transfer_to(signal.stop_signal)

            # 清空原有信号的槽函数
            if not self.__signal.is_shared:
                self.__signal.clear()

            self.__signal = signal
            return signal
        else:
            raise TypeError("参数 signal 必须为 TaskSignalParams 类型")

    def set_progress(self, progress: TaskProgress) -> TaskProgress:
        if isinstance(progress, TaskProgress):
            self.__progress = progress
            return progress
        else:
            raise TypeError("参数 progress 必须为 TaskProgress 类型")

    def set_manage(self, task_manage: TaskManageBase, need_delete: bool = False):
        """
        设置任务管理器
        :param task_manage:任务管理类
        :param need_delete:是否需要删除,默认为不删除,删除则会在clear方法内删除任务池
        """
        if isinstance(task_manage, TaskManageBase):
            self.__task_manage = task_manage
            if need_delete:
                self.__need_delete_task_manage = True
            return task_manage
        else:
            raise TypeError("参数 task_manage 必须为 TaskManageBase 类型")

    def set_parent_task(self, parent_task: Optional['Task'] | None):
        """设置父任务"""
        if parent_task == self.parent_task:
            return
        # 解除父任务连接
        if parent_task is None and self.parent_task is not None:
            self.parent_task.signal.stop_signal.disconnect(self.__parent_task_stop_slot)
            self.parent_task.signal.clear_signal.disconnect(self.__parent_task_clear_slot)
            self.__parent_task = None
            return
        # 断开旧父任务连接
        if self.parent_task is not None:
            self.parent_task.signal.stop_signal.disconnect(self.__parent_task_stop_slot)
            self.parent_task.signal.clear_signal.disconnect(self.__parent_task_clear_slot)
        # 连接新父任务
        if parent_task.signal != self.signal:
            self.__parent_task = weakref.ref(parent_task)
            parent_task.signal.stop_signal.connect(self.__parent_task_stop_slot)
            parent_task.signal.clear_signal.connect(self.__parent_task_clear_slot)
        else:
            logger.warning(f'父任务信号与该任务信号一致 父任务{parent_task.name}.signal == 子任务{self.name}.signal')

    def set_retry_count(self, retry_count: int):
        """设置重试次数"""
        self.__retry_count = retry_count

    def set_retry_should(self, retry_should: Callable):
        """
        设置重试判断函数
        返回Ture表示不重试,False表示重试
        """
        self.__retry_should = retry_should

    def add_sub_task(self, sub_task: 'Task'):
        if not isinstance(sub_task, Task):
            raise TypeError("参数 sub_task 必须为 Task 类型")
        self.__sub_tasks.add(sub_task)

    # ----------任务运行类方法----------
    def __call__(self):
        """返回执行函数,必须调用该函数"""
        return self.__executor()

    def __create_task_manage(self, use_process, use_async) -> TaskManageBase:
        """创建任务管理器"""
        if use_process and use_async:
            raise ValueError('不能同时使用多进程和异步任务')
        self.__need_delete_task_manage = True  # 是否需要删除任务管理器
        if use_process:
            return TaskProcessManage(1)
        elif use_async:
            return TaskAsyncManage(1)
        else:
            return TaskManage(1)

    def _start(self, priority: int = 5) -> bool:
        """
        内部启动任务的核心逻辑（私有方法）

        :param priority: 任务优先级（1-10，1为最高优先级，默认为5）
        :return: 是否成功提交任务
        """
        if self.__state.isClear:
            logger.debug(f"任务 {self.name} 已被清理，无法再次启动")
            return False
        # 如果任务正在运行，先停止
        if self.__state.isRunning:
            self.stop()
        # 检查父任务状态
        if self.__parent_task is not None:
            if (self.parent_task is None or
                    self.parent_task.state.isStopped or
                    self.parent_task.state.isClear):
                logger.warning(f"{self.__class__.__name__} 父任务已停止/已清理,无法启动任务: {self.name}")
                return False
        # 标记为运行状态
        self.__state.set_running()
        # 发送开始信号
        self.start_signal.emit(self)
        # 提交任务到任务池
        return self.__executor.submit_task(self.__task_manage, priority)

    def start(self, timeout: float | int = None, priority: int = 5,
              parent_task: 'Task' = None) -> Any | bool:
        """
        执行任务,可反复调用
        :param timeout:是否等待任务完成,支持输入float|int值,0为无限等待,默认不等待,等待时返回任务结果,超时停止
        :param priority: 任务优先级（1-10，1为最高优先级，默认为5）
        :param parent_task: 指定父任务
        """
        if parent_task is not None:
            self.set_parent_task(parent_task)
        # 启动任务
        if not self._start(priority):
            return False
        # 根据 timeout 决定是否等待
        if timeout is not None:
            return self.result(timeout)
        return True

    async def start_async(self, timeout: float | int = None, priority: int = 5,
                          parent_task: 'Task' = None) -> Any | bool:
        """
        异步执行任务（非阻塞等待），适合在异步池中使用

        :param timeout: 超时时间（秒），0表示无限等待，None表示不等待立即返回True
        :param priority: 任务优先级（1-10，1为最高优先级，默认为5）
        :param parent_task: 指定父任务
        :return:
            - timeout=None: 返回 True（提交成功）或 False（提交失败）
            - timeout>=0: 返回任务结果或 None（超时/失败）

        使用示例:
            # 方式1：不等待，立即返回
            success = await task.start_async(timeout=None)

            # 方式2：限时等待结果
            result = await task.start_async(timeout=30, parent_task=self)

            # 方式3：无限等待结果
            result = await task.start_async(timeout=0)

        注意:
            - 该方法应该在异步池中调用，避免占用线程池工作线程
            - 子任务应该提交到线程池，父任务在异步池中等待，防止死锁
            - 与同步 start() 不同，该方法不会阻塞工作线程
        """
        if parent_task is not None:
            self.set_parent_task(parent_task)
        # 启动任务
        if not self._start(priority):
            return False
        # 根据 timeout 决定行为
        if timeout is not None:
            # 异步等待结果
            return await self.result_async(timeout)
        return True

    def result(self, timeout: float | int = None) -> Any | None:
        """
        获取任务结果
        :param timeout:是否等待任务完成,支持输入float|int值,0为无限等待,默认不等待,等待时返回任务结果,超时时会停止当前任务,内部每0.1秒检查一次
        """
        result = self.__executor.result(timeout, self.parent_task)
        return result

    async def result_async(self, timeout: float | int = None) -> Any | None:
        """
        异步获取任务结果（非阻塞等待）

        :param timeout: 超时时间（秒），0表示无限等待，None表示立即返回（不等待）,内部每0.1秒检查一次
        :return: 任务结果，超时、失败或未启动时返回None

        使用示例:
            # 在异步函数中使用
            async def my_async_func():
                task = SomeTask(...)
                task.start_async()
                result = await task.async_result(timeout=30)

            # 在普通函数中使用（需要事件循环）
            import asyncio
            result = asyncio.run(task.async_result(timeout=30))

        注意:
            - 该方法不会阻塞线程池工作线程，适合在异步池中调用
            - 父任务应该在异步池中运行，子任务在线程池中运行，避免死锁
        """
        result = await self.__executor.result_async(timeout, self.parent_task)
        return result

    def stop(self) -> bool:
        """停止任务,已开始的任务无法被取消,需要在提交函数内引用isRunning标识符"""
        state = False
        if self.__state.isRunning:
            self.__state.set_stopped()
            state = self.__executor.cancel_future()
        for sub_task in self.__sub_tasks.copy():
            sub_task.stop()
        self.stop_signal.emit(self)
        return state

    def add_done_callback(self, callback: Callable):
        """添加回调函数,默认回传self"""
        self.__executor.add_done_callback(callback)

    def __parent_task_stop_slot(self, task: 'Task'):
        """父任务停止信号处理"""
        if task == self.parent_task:
            self.stop()
        else:
            logger.debug(f'不是父任务: {task.name},忽略停止处理')

    def __parent_task_clear_slot(self, task: 'Task'):
        """父任务清理信号处理"""
        if task == self.parent_task:
            self.clear()
        else:
            logger.debug(f'不是父任务: {task.name},忽略清理处理')

    def __finished_slot(self):
        """任务执行后发送完成信号"""
        self.__state.set_finished()
        self.finish_signal.emit(self)

    def progress_emit(self, progress: TaskProgress):
        """任务进度更新信号"""
        if isinstance(progress, TaskProgress) and self.progress != progress:
            self.progress.set_progress(progress)
        self.progress_signal.emit(self)

    def clear(self):
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
        if self.__state.isClear:
            return
        # 1. 停止正在运行的任务
        if self.__state.isRunning:
            self.stop()
        # 2. 发送清理信号
        self.__signal.clear_signal.emit(self)
        for sub_task in self.__sub_tasks.copy():
            sub_task.clear()
        # 3. 清理执行器
        self.__executor.clear()
        # 4. 断开所有信号连接
        if not self.__signal.is_shared:
            self.__signal.clear()
        # 解除父任务链接
        self.set_parent_task(None)
        # 5. 清理任务管理器引用 注意：外部传入的task_manage不由这里清理,只清理内部创建的单线程管理器
        if self.__need_delete_task_manage:
            try:
                if self.__task_manage is not None:
                    self.__task_manage.stop()
            except Exception as e:
                logger.exception(f"{self.__class__.__name__}.clear 释放任务管理器错误: {e}")
            finally:
                self.__task_manage = None
        # 6. 标记为已清理
        self.__state.set_clear()
        self.name = f"{self.name}_CLEANED"

    def __del__(self):
        """析构函数，确保资源被清理"""
        try:
            if hasattr(self, '_Task__state'):
                if not self.__state.isClear:
                    self.clear()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear()
        return False


if __name__ == '__main__':
    task_a = Task(lambda: print("task_a"))
    task_b = Task(lambda: print("task_b"))
    task_c = Task(lambda: print("task_c"))
    task_b.set_parent_task(task_a)
    # task_b.clear()
    task_c.set_parent_task(task_a)
    print(task_a.stop_signal.__len__())
