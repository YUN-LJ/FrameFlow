"""任务编排器"""
import asyncio
from abc import ABC, abstractmethod
from typing import Callable, Any, Optional, List
from Fun.BaseTools.TaskClass import Task, TaskSignalParams
from Fun.BaseTools import LogClass

logger = LogClass.get_logger(__name__, console_level='WARNING')


class BaseTaskGroup(ABC):
    """
    任务组基类 - 提取公共逻辑

    公共特性:
    - 共享信号管理
    - 重试机制
    - 父任务取消传播
    """

    def __init__(self, name: str, max_retries: int = 0):
        """
        初始化任务组基类

        :param name: 任务组名称
        :param max_retries: 每个任务的最大重试次数(默认0不重试)
        """
        self.name = name
        self.max_retries = max_retries
        self.__sub_task_signal = TaskSignalParams(is_shared=True)

    @property
    def sub_task_signal(self) -> TaskSignalParams:
        """获取共享信号"""
        return self.__sub_task_signal

    def _should_stop(self, parent_task: Optional[Task]) -> bool:
        """检查是否应停止执行"""
        return parent_task and not parent_task.isRunning

    async def _execute_with_retry(self, task: Task, parent_task: Optional[Task]) -> Optional[Any]:
        """
        带重试的任务执行（公共逻辑）

        :param task: 要执行的任务
        :param parent_task: 父任务
        :return: 任务执行结果，失败返回None
        """
        last_exception = None

        # 添加为父任务的子任务
        if parent_task:
            parent_task.add_sub_task(task)

        for attempt in range(1, self.max_retries + 2):
            if self._should_stop(parent_task):
                logger.debug(f"任务 {task.name} 因父任务取消而终止")
                return None

            try:
                if not task.state.isUsable:
                    logger.debug(f"任务 {task.name} 不可用, 跳过")
                    return None

                result = await task.start_async(timeout=0)

                if result is not None:
                    return result

                logger.warning(f"任务 {task.name} 第{attempt}次尝试返回None")

            except Exception as e:
                last_exception = e
                logger.exception(f"任务 {task.name} 第{attempt}次尝试异常: {e}")

            if attempt <= self.max_retries:
                delay = 0.1 * attempt
                await asyncio.sleep(delay)

        if last_exception:
            logger.error(f"任务 {task.name} 经过{self.max_retries + 1}次尝试后仍然失败")
        return None

    def _bridge_signal_to(self, target: 'BaseTaskGroup') -> None:
        """桥接信号到目标任务组"""
        self.__sub_task_signal.bridge_other_signal(target.__sub_task_signal)

    @abstractmethod
    async def execute(self, parent_task: Optional[Task] = None) -> Any:
        """执行任务组"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """清理资源"""
        pass


class TaskChain(BaseTaskGroup):
    """
    任务链 - 串行执行多个任务，支持结果传递

    特性:
    - 支持共享信号传递
    - 支持失败重试机制
    - 自动资源清理
    - 父任务取消传播
    - 上一个任务的结果自动传递给下一个任务

    使用示例:
        chain = TaskChain(max_retries=3)
        result = await chain.add(task1).add(task2).add(task3).execute(parent_task)
    """

    def __init__(self, name: str = "TaskChain", max_retries: int = 0):
        """
        初始化任务链

        :param name: 任务链名称
        :param max_retries: 每个任务的最大重试次数(默认0不重试)
        """
        super().__init__(name, max_retries)
        self.tasks: List[Task] = []
        self.results: List[Any] = []
        self._parent_task: Optional[Task] = None

    def add(self, task: Task) -> 'TaskChain':
        """
        添加任务到链中

        :param task: 要添加的任务对象
        :return: self (支持链式调用)
        """
        self.tasks.append(task)
        return self

    async def execute(self, parent_task: Optional[Task] = None) -> Any:
        """
        执行任务链

        :param parent_task: 父任务,用于传递取消信号
        :return: 最后一个任务的执行结果（如果任务支持结果传递）
        """
        self._parent_task = parent_task
        self.results = []
        last_result = None  # 存储上一个任务的结果，用于传递给下一个任务

        for index, task in enumerate(self.tasks):
            if self._should_stop(parent_task):
                logger.debug(f"任务链 {self.name} 被父任务取消")
                break

            try:
                # 设置父任务关系
                if parent_task:
                    task.set_parent_task(parent_task)

                # 设置共享信号
                task.set_signal(self.sub_task_signal)

                # 如果任务支持接收输入且上一个结果不为None，则传递结果
                if hasattr(task, 'set_input') and last_result is not None:
                    task.set_input(last_result)

                # 执行任务(带重试机制)
                result = await self._execute_with_retry(task, parent_task)

                # 立即清理已执行完的任务资源
                task.clear()

                self.results.append(result)
                last_result = result  # 传递给下一个任务

                # 如果任务失败（返回None），中断整个任务链
                if result is None:
                    logger.warning(f"任务链 {self.name} 第{index + 1}个任务失败，中断执行")
                    break

            except Exception as e:
                logger.exception(f"任务链 {self.name} 第{index + 1}个任务异常: {e}")
                self.results.append(None)
                break  # 异常时中断链

        return last_result

    def clear(self) -> None:
        """
        清理任务链
        注意:即使任务已经执行并清理过,这里也会确保所有资源被释放
        """
        # 清理所有任务的信号连接
        for task in self.tasks:
            try:
                task.clear()
            except Exception as e:
                logger.warning(f"清理任务 {task.name} 时出错: {e}")

        # 清空共享信号的连接(如果是共享信号,需要强制清理)
        self.sub_task_signal.clear(compulsory=True)

        # 清空任务列表和结果
        self.tasks.clear()
        self.results.clear()

    def reset(self) -> None:
        """
        重置任务链状态但保留任务列表
        用于重新执行相同的任务链
        """
        self.results.clear()
        self._parent_task = None
        # 重新创建共享信号
        self._BaseTaskGroup__sub_task_signal = TaskSignalParams(is_shared=True)

    @property
    def total_tasks(self) -> int:
        """获取任务总数"""
        return len(self.tasks)

    @property
    def completed_tasks(self) -> int:
        """获取已完成任务数"""
        return len([r for r in self.results if r is not None])

    @property
    def success_rate(self) -> float:
        """获取成功率(0-100)"""
        if not self.results:
            return 0.0
        success_count = len([r for r in self.results if r is not None])
        return (success_count / len(self.results)) * 100


class ParallelTaskGroup(BaseTaskGroup):
    """
    并行任务组 - 并发执行多个任务

    特性:
    - 支持共享信号传递
    - 支持并发控制（使用信号量）
    - 自动资源清理

    使用示例:
        group = ParallelTaskGroup(max_concurrent=5)
        results = await group.add(task1).add(task2).execute(parent_task)
    """

    def __init__(self, name: str = "ParallelGroup", max_concurrent: int = None, max_retries: int = 0):
        """
        初始化并行任务组

        :param name: 任务组名称
        :param max_concurrent: 最大并发数,None表示无限制
        :param max_retries: 每个任务的最大重试次数
        """
        super().__init__(name, max_retries)
        self.tasks: List[Task] = []
        self.max_concurrent = max_concurrent
        self._semaphore: Optional[asyncio.Semaphore] = asyncio.Semaphore(max_concurrent) if max_concurrent else None

    def add(self, task: Task) -> 'ParallelTaskGroup':
        """
        添加任务到并行组

        :param task: 要添加的任务对象
        :return: self (支持链式调用)
        """
        self.tasks.append(task)
        return self

    async def execute(self, parent_task: Optional[Task] = None) -> List[Any]:
        """
        并行执行所有任务

        :param parent_task: 父任务
        :return: 所有任务的结果列表
        """
        results = [None] * len(self.tasks)

        async def run_single_task(index: int, task: Task) -> None:
            """执行单个任务（带并发控制）"""

            async def _execute() -> None:
                try:
                    # 设置共享信号
                    task.set_signal(self.sub_task_signal)

                    # 添加为父任务的子任务
                    if parent_task:
                        parent_task.add_sub_task(task)

                    # 执行任务(带重试)
                    result = await self._execute_with_retry(task, parent_task)
                    # 清理任务资源
                    task.clear()

                    results[index] = result
                except Exception as e:
                    logger.exception(f"并行任务 {self.name}[{index}] 异常: {e}")
                    results[index] = None

            # 使用信号量控制并发
            if self._semaphore:
                async with self._semaphore:
                    await _execute()
            else:
                await _execute()

        # 创建并执行所有任务
        tasks_coroutines = [run_single_task(i, task) for i, task in enumerate(self.tasks)]
        await asyncio.gather(*tasks_coroutines)

        return results

    def clear(self) -> None:
        """
        清理任务组

        功能:
        - 清理所有任务的资源
        - 强制清理共享信号连接
        - 清空任务列表
        """
        for task in self.tasks:
            try:
                task.clear()
            except Exception as e:
                logger.warning(f"清理任务 {task.name} 时出错: {e}")

        # 清理共享信号
        self.sub_task_signal.clear(compulsory=True)

        self.tasks.clear()


class TaskOrchestrator(BaseTaskGroup):
    """
    任务编排器 - 统一管理复杂的任务链

    特性:
    - 支持串行、并行、条件分支
    - 自动错误处理和重试
    - 统一的资源清理
    - 共享信号管理
        注意父任务的停止和清除信号不要桥接到sub_task_signal,否则导致子任务执行出错
        原因为子任务执行完成后,内部会清理子任务,此时子任务发射清理信号,如果父任务的清理信号连接
        到了sub_task_signal上，则会导致父任务发送清理信号进而关闭全部子任务

    使用示例:
        orchestrator = TaskOrchestrator("下载流程", max_retries=3)

        # 串行执行
        orchestrator.chain(
            lambda: ImageInfoTask(image_id),
            lambda info: DownloadTask(info.url),
            lambda data: SaveTask(data)
        )

        # 并行执行
        orchestrator.parallel([
            lambda: ThumbTask(url1),
            lambda: ThumbTask(url2),
        ])

        result = await orchestrator.execute(parent_task)
    """

    def __init__(self, name: str = "Orchestrator", max_retries: int = 3):
        """
        初始化任务编排器

        :param name: 编排器名称
        :param max_retries: 每个任务的最大重试次数(默认3次)
        """
        super().__init__(name, max_retries)
        self.operations: List[dict] = []
        self._parent_task: Optional[Task] = None

    def chain(self, *task_factories: Callable) -> 'TaskOrchestrator':
        """
        添加串行任务链

        :param task_factories: 任务工厂函数列表,函数如果返回的不是Task将不会执行
        :return: self
        """
        self.operations.append({
            'type': 'chain',
            'factories': task_factories
        })
        return self

    def parallel(self, task_factories: List[Callable], max_concurrent: int = None) -> 'TaskOrchestrator':
        """
        添加并行任务组

        :param task_factories: 任务工厂函数列表,函数如果返回的不是Task将不会执行
        :param max_concurrent: 最大并发数
        :return: self
        """
        self.operations.append({
            'type': 'parallel',
            'factories': task_factories,
            'max_concurrent': max_concurrent
        })
        return self

    async def execute(self, parent_task: Optional[Task] = None, chain_break: bool = False) -> Any:
        """
        执行编排的所有操作

        :param parent_task: 父任务
        :param chain_break: 串行有任务失败时是否中断,默认不中断
        :return: 最后一步的结果

        说明:
        - 进度通知统一通过 sub_task_signal.progress_signal 发送
        - 外部可通过连接该信号接收进度更新
        """
        self._parent_task = parent_task
        last_result = None

        for op_index, operation in enumerate(self.operations):
            if self._should_stop(parent_task):
                logger.debug(f"编排器 {self.name} 被取消")
                break

            try:
                if operation['type'] == 'chain':
                    last_result = await self._execute_chain(
                        operation['factories'],
                        last_result,
                        parent_task,
                        chain_break
                    )
                    if chain_break and last_result is None:
                        break
                elif operation['type'] == 'parallel':
                    last_result = await self._execute_parallel(
                        operation['factories'],
                        operation.get('max_concurrent'),
                        parent_task
                    )

            except Exception as e:
                logger.exception(f"编排器 {self.name} 第{op_index + 1}步异常: {e}")
                break

        return last_result

    async def _execute_chain(self, factories: List[Callable], initial_input: Any,
                             parent_task: Optional[Task], chain_break: bool) -> Any:
        """
        执行串行链

        :param factories: 任务工厂函数列表
        :param initial_input: 初始输入值(传递给第一个工厂函数)
        :param parent_task: 父任务
        :param chain_break: 串行有任务失败时是否中断
        :return: 最后一个任务的执行结果
        """
        current_input = initial_input

        for factory in factories:
            if self._should_stop(parent_task):
                break

            # 创建任务(可能依赖上一步的结果)
            task = factory(current_input) if current_input is not None else factory()

            if not isinstance(task, Task):
                logger.debug(f"工厂函数未返回Task对象: {factory},返回类型为: {type(task)}")
                if chain_break:
                    return None
                else:
                    continue

            # 设置共享信号
            task.set_signal(self.sub_task_signal)

            # 执行任务(带重试)
            result = await self._execute_with_retry(task, parent_task)

            # 清理任务
            task.clear()

            # 如果任务失败，中断链
            if result is None and chain_break:
                logger.warning(f"串行链任务失败，中断执行")
                return None

            current_input = result

        return current_input

    async def _execute_parallel(self, factories: List[Callable], max_concurrent: int,
                                parent_task: Optional[Task]) -> List[Any]:
        """
        执行并行组

        :param factories: 任务工厂函数列表
        :param max_concurrent: 最大并发数,None表示无限制
        :param parent_task: 父任务
        :return: 所有任务的执行结果列表
        """
        tasks = []
        for factory in factories:
            task = factory()
            if isinstance(task, Task):
                tasks.append(task)

        if not tasks:
            return []

        # 创建并行任务组
        group = ParallelTaskGroup(
            name=f"{self.name}_sub_parallel",
            max_concurrent=max_concurrent,
            max_retries=self.max_retries
        )

        # 桥接信号：将组的共享信号连接到编排器的共享信号
        group.sub_task_signal.bridge_other_signal(self.sub_task_signal)

        # 添加任务并执行
        for task in tasks:
            group.add(task)

        results = await group.execute(parent_task)
        group.clear()

        return results

    def clear(self) -> None:
        """
        清理编排器

        功能:
        - 清理全局共享信号连接
        - 清空所有操作记录
        """
        # 清理共享信号
        self.sub_task_signal.clear(compulsory=True)

        self.operations.clear()
