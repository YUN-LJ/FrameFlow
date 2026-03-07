"""
任务管理
创建Task类的实例后
调用TaskManage.add_task方法即可执行任务
"""
import os
from concurrent.futures import ThreadPoolExecutor, Future
from threading import Lock
from typing import Callable


class TaskProgress:
    def __init__(self):
        self.total = 0  # 任务总量
        self.finished = 0  # 已完成数量
        self.rate = 0  # 速率

    def __str__(self):
        return f'已完成:{self.finished} 总计:{self.total} 速率:{self.rate}'

    def __repr__(self):
        return f'已完成:{self.finished} 总计:{self.total} 速率:{self.rate}'


class Task:
    """任务类"""

    def __init__(self, func: Callable = None, thread_pool: ThreadPoolExecutor = None,
                 callback_func: Callable = None, name=None, desc=None, *args, **kwargs):
        """
        :param func:待执行函数
        :param thread_pool:任务池
        :param callback_func:回调函数
        :param name:任务名称,默认使用func的名称
        :param desc:任务描述
        :param args: 如果该任务还有其它依赖参数可以存入args变量中
        :param kwargs:如果该任务还有其它依赖参数可以存入kwargs变量中
        """
        # 由于提交到线程池中的任务不能被直接取消
        # 可以在func函数中使用该变量来判断任务是否被取消,Flase表示未被取消
        self.isCancel = False
        self.__func = func  # 可执行函数
        self.__thread_pool = thread_pool  # 线程池
        self.__callback_func = [callback_func]
        self.__future: Future = None  # 任务提交后的Future对象
        self.progress = TaskProgress()  # 进度属性
        # 尝试获取对象的__name__属性,如果属性不存在则返回str(func)
        self.name = getattr(func, '__name__', str(func)) if name is None else name
        self.desc = desc  # 任务描述
        self.args = args  # 依赖参数
        self.kwargs = kwargs  # 依赖参数
        self.__result = None  # 用于重新设置返回值结果

    def start(self) -> bool:
        """执行任务"""
        if self.__thread_pool is None or self.__func is None:
            return False
        self.__future = self.__thread_pool.submit(self.__func)
        for callback in self.__callback_func:
            if callable(callback):
                self.add_done_callback(callback)
        return True

    def set_result(self, result):
        """重设任务结果"""
        self.__result = result

    def result(self):
        """获取任务结果"""
        if self.done():
            if self.__result is None:
                return self.__future.result()
            else:
                return self.__result
        else:
            return None

    def done(self) -> bool:
        """任务是否完成"""
        if self.__future is None:
            return False
        return self.__future.done()

    def cancelled(self) -> bool:
        """任务是否取消"""
        if self.__future is None:
            return False
        return self.__future.cancelled()

    def cancel(self) -> bool:
        """取消任务"""
        if self.__future is None:
            return False
        self.isCancel = True
        return self.__future.cancel()

    def running(self) -> bool:
        if self.__future is None:
            return False
        return self.__future.running()

    def exception(self) -> Exception | None:
        """获取异常"""
        if self.__future is None:
            return None
        return self.__future.exception()

    def set_func(self, func: Callable):
        self.__func = func

    def add_thread_pool(self, thread_pool: ThreadPoolExecutor) -> bool:
        """添加线程池"""
        if self.__thread_pool is None and isinstance(thread_pool, ThreadPoolExecutor):
            self.__thread_pool = thread_pool
            return True
        return False

    def add_done_callback(self, callback_func: Callable) -> bool:
        """添加回调函数,默认回传self"""

        def safe_callback(future):
            """安全的回调包装器"""
            # 检查future是否被取消
            if future.cancelled():
                # print("Future已被取消，跳过回调")
                return
            # 执行回调
            callback_func(self)

        if self.__future is None:
            self.__callback_func.append(callback_func)
            return True
        self.__future.add_done_callback(safe_callback)
        return True


class TaskManage:
    """任务管理类"""

    def __init__(self, num_work=os.cpu_count()):
        self.__thread_pool = ThreadPoolExecutor(max_workers=num_work)
        # 存储了全部未完成的Task任务,可通过name属性获取到任务名称
        self.cur_all_tasks: set[Task] = set()

    def add_task(self, task: Task) -> bool:
        """添加任务"""
        if task.add_thread_pool(self.__thread_pool):
            self.cur_all_tasks.add(task)
            task.add_done_callback(lambda value: self.cur_all_tasks.remove(value))
            task.start()
            return True
        return False

    def stop(self):
        """
        停止
        注意当前正在执行的任务将不会被终止
        未开始的任务将全部被取消
        即使Task任务被取消仍然会调用返回函数
        """
        self.__thread_pool.shutdown(wait=False, cancel_futures=True)


if __name__ == '__main__':
    pass
