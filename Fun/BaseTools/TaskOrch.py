"""任务编排器"""
import asyncio
from abc import ABC, abstractmethod
from typing import Callable, Any, Optional, List, Union

from Fun.BaseTools.TaskClass import Task, TaskSignalParams
from Fun.BaseTools import LogClass

logger = LogClass.get_logger(__name__, console_level='WARNING')

# 定义工厂函数类型
ChainFactory = Callable[[Optional[Any]], Task]  # 串行链：可接收参数
ParallelFactory = Callable[[], Task]  # 并行组：不接受参数
TaskItem = Union[Task, ChainFactory, ParallelFactory]  # 统一任务项类型


class BaseTaskGroup(ABC):
    """
    任务组基类 - 提取公共逻辑

    公共特性:
    - 共享信号管理
    - 父任务取消传播
    """

    def __init__(self, name: str):
        """
        初始化任务组基类

        :param name: 任务组名称
        """
        self.name = name
        self.__sub_task_signal = TaskSignalParams(is_shared=True)

    @property
    def sub_task_signal(self) -> TaskSignalParams:
        """获取共享信号"""
        return self.__sub_task_signal

    @staticmethod
    def _should_stop(parent_task: Optional[Task]) -> bool:
        """检查是否应停止执行"""
        return parent_task and not parent_task.isRunning

    async def _execute_task(self, task: Task, parent_task: Task) -> Any | None:
        """
        任务执行（公共逻辑）

        :param task: 要执行的任务
        :param parent_task: 父任务
        :return: 任务执行结果，失败返回None
        """
        if self._should_stop(parent_task):
            logger.debug(f"任务 {task.name} 因父任务取消而终止")
            return None

        # 添加为父任务的子任务
        if parent_task:
            parent_task.add_sub_task(task)

        # 设置共享信号
        task.set_signal(self.sub_task_signal)

        try:
            if not task.state.isUsable:
                logger.debug(f"任务 {task.name} 不可用, 跳过")
                return None

            result = await task.start_async(timeout=0)

            if result is not None:
                return result

        except Exception as e:
            logger.exception(f"任务 {task.name} 失败 错误: {e}")

        return None

    def _bridge_signal_to(self, target: 'BaseTaskGroup') -> None:
        """桥接信号到目标任务组"""
        self.__sub_task_signal.bridge_other_signal(target.__sub_task_signal)

    @staticmethod
    def _resolve_task(item: TaskItem, input_value: Any = None) -> Optional[Task]:
        """
        解析任务项，如果是工厂函数则调用创建Task实例

        :param item: Task实例或工厂函数
        :param input_value: 传递给工厂函数的输入值（仅串行链使用）
        :return: Task实例或None
        """
        if isinstance(item, Task):
            return item
        elif callable(item):
            try:
                # 尝试判断参数个数来决定如何调用
                # 串行链：有input_value时尝试传递参数
                if input_value is not None:
                    task = item(input_value)
                else:
                    task = item()

                if isinstance(task, Task):
                    return task
                else:
                    logger.warning(f"工厂函数返回值不是Task实例: {item}, 返回类型: {type(task)}")
            except Exception as e:
                logger.exception(f"执行工厂函数失败: {e}")
        return None

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
    - 支持直接添加Task实例或工厂函数（运行时动态创建）

    使用示例:
        chain = TaskChain()

        # 方式1: 直接添加Task实例
        chain.add(task1).add(task2)

        # 方式2: 批量添加Task实例
        chain.add_tasks([task1, task2, task3])

        # 方式3: 添加工厂函数（支持参数传递）
        chain.add_factories(
            lambda: CreateTask(),                           # 第一个任务无参数
            lambda last: ProcessTask(last),                 # 接收上一步结果
            lambda data: SaveTask(data)                     # 接收上一步结果
        )

        result = await chain.execute(parent_task)
    """

    def __init__(self, name: str = "TaskChain"):
        """
        初始化任务链

        :param name: 任务链名称
        """
        super().__init__(name)
        self._items: List[TaskItem] = []  # 存储Task实例或工厂函数
        self.results: list[Any] = []
        self._parent_task: Optional[Task] = None

    def add(self, task: Task) -> 'TaskChain':
        """
        添加任务到链中

        :param task: 要添加的任务对象
        :return: self (支持链式调用)
        """
        self._items.append(task)
        return self

    def add_tasks(self, tasks: List[Task]) -> 'TaskChain':
        """
        批量添加任务

        :param tasks: 任务对象列表
        :return: self (支持链式调用)
        """
        self._items.extend(tasks)
        return self

    def add_factories(self, *factories: ChainFactory) -> 'TaskChain':
        """
        批量添加工厂函数（执行时动态创建Task）

        :param factories: 工厂函数列表，每个函数接收上一个任务的结果，返回Task实例
        :return: self (支持链式调用)

        示例:
            chain.add_factories(
                lambda: CreateTask(),                           # 第一个任务无参数
                lambda last_result: ProcessTask(last_result),   # 接收上一个结果
                lambda data: SaveTask(data)                     # 接收上一个结果
            )
        """
        self._items.extend(factories)
        return self

    async def execute(self,
                      parent_task: Optional[Task] = None,
                      last_result=None,
                      chain_break: bool = False) -> Any:
        """
        执行任务链

        :param parent_task: 父任务,用于传递取消信号
        :param last_result: 上一次任务执行结果
        :param chain_break: 有任务失败时中断执行,默认不中断
        :return: 最后一个任务的执行结果
        """
        self._parent_task = parent_task

        for index, item in enumerate(self._items):
            if self._should_stop(parent_task):
                logger.debug(f"任务链 {self.name} 被父任务取消")
                break

            try:
                # 解析任务项（如果是工厂函数则动态创建，传入上一个结果）
                task = self._resolve_task(item, last_result)

                if task is None:
                    logger.warning(f"任务链 {self.name} 第{index + 1}个项无效，跳过")
                    continue

                # 执行任务
                result = await self._execute_task(task, parent_task)

                # 立即清理已执行完的任务资源
                task.clear()

                self.results.append(result)
                last_result = result

                # 如果任务失败（返回None），中断整个任务链
                if result is None and chain_break:
                    logger.warning(f"任务链 {self.name} 第{index + 1}个任务失败，中断执行")
                    break

            except Exception as e:
                logger.exception(f"任务链 {self.name} 第{index + 1}个任务异常: {e}")
                self.results.append(None)
                break

        return last_result

    def clear(self) -> None:
        """
        清理任务链
        注意:即使任务已经执行并清理过,这里也会确保所有资源被释放
        """
        for item in self._items:
            if isinstance(item, Task):
                try:
                    item.clear()
                except Exception as e:
                    logger.warning(f"清理任务 {item.name} 时出错: {e}")

        self.sub_task_signal.clear(compulsory=True)
        self._items.clear()
        self.results.clear()

    def reset(self) -> None:
        """
        重置任务链状态但保留任务列表
        用于重新执行相同的任务链
        """
        self.results.clear()
        self._parent_task = None

    @property
    def total_tasks(self) -> int:
        """获取任务总数"""
        return len(self._items)

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
    - 支持直接添加Task实例或工厂函数（运行时动态创建）

    使用示例:
        group = ParallelTaskGroup(max_concurrent=5)

        # 方式1: 直接添加Task实例
        group.add(task1).add(task2)

        # 方式2: 批量添加Task实例
        group.add_tasks([task1, task2, task3])

        # 方式3: 添加工厂函数（不接受参数）
        group.add_factories(
            lambda: DownloadTask("url1"),
            lambda: DownloadTask("url2"),
            lambda: DownloadTask("url3")
        )

        results = await group.execute(parent_task)
    """

    def __init__(self, name: str = "ParallelGroup", max_concurrent: int = None):
        """
        初始化并行任务组

        :param name: 任务组名称
        :param max_concurrent: 最大并发数,None表示无限制
        """
        super().__init__(name)
        self._items: List[TaskItem] = []  # 存储Task实例或工厂函数
        self.max_concurrent = max_concurrent
        self._semaphore: Optional[asyncio.Semaphore] = asyncio.Semaphore(max_concurrent) if max_concurrent else None

    def add(self, task: Task) -> 'ParallelTaskGroup':
        """
        添加任务到并行组

        :param task: 要添加的任务对象
        :return: self (支持链式调用)
        """
        self._items.append(task)
        return self

    def add_tasks(self, tasks: List[Task]) -> 'ParallelTaskGroup':
        """
        批量添加任务

        :param tasks: 任务对象列表
        :return: self (支持链式调用)
        """
        self._items.extend(tasks)
        return self

    def add_factories(self, *factories: ParallelFactory) -> 'ParallelTaskGroup':
        """
        批量添加工厂函数（执行时动态创建Task）

        :param factories: 工厂函数列表，每个函数返回Task实例（不接受参数）
        :return: self (支持链式调用)

        示例:
            group.add_factories(
                lambda: DownloadTask("url1"),
                lambda: DownloadTask("url2"),
                lambda: DownloadTask("url3")
            )
        """
        self._items.extend(factories)
        return self

    async def execute(self, parent_task: Optional[Task] = None) -> List[Any]:
        """
        并行执行所有任务

        :param parent_task: 父任务
        :return: 所有任务的结果列表
        """
        results = [None] * len(self._items)

        async def run_single_task(index: int, item: TaskItem) -> None:
            """执行单个任务（带并发控制）"""

            async def _execute() -> None:
                try:
                    # 解析任务项（并行组不需要传递输入参数）
                    task = self._resolve_task(item)

                    if task is None:
                        logger.warning(f"并行任务 {self.name}[{index}] 项无效")
                        results[index] = None
                        return

                    # 执行任务
                    result = await self._execute_task(task, parent_task)

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
        tasks_coroutines = [run_single_task(i, item) for i, item in enumerate(self._items)]
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
        for item in self._items:
            if isinstance(item, Task):
                try:
                    item.clear()
                except Exception as e:
                    logger.warning(f"清理任务 {item.name} 时出错: {e}")

        self.sub_task_signal.clear(compulsory=True)
        self._items.clear()


class TaskOrchestrator(BaseTaskGroup):
    """
    任务编排器 - 统一管理复杂的任务链

    特性:
    - 支持串行、并行、条件分支
    - 统一的资源清理
    - 共享信号管理
        注意父任务的停止和清除信号不要桥接到sub_task_signal,否则导致子任务执行出错
        原因为子任务执行完成后,内部会清理子任务,此时子任务发射清理信号,如果父任务的清理信号连接
        到了sub_task_signal上，则会导致父任务发送清理信号进而关闭全部子任务

    使用示例:
        orchestrator = TaskOrchestrator("下载流程")

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

    def __init__(self, name: str = "Orchestrator"):
        """
        初始化任务编排器

        :param name: 编排器名称
        """
        super().__init__(name)
        self.operations: List[dict] = []
        self._parent_task: Optional[Task] = None

    def chain(self, *task_factories: ChainFactory) -> 'TaskOrchestrator':
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

    def parallel(self, task_factories: List[ParallelFactory], max_concurrent: int = None) -> 'TaskOrchestrator':
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
                        parent_task,
                        last_result,
                        chain_break
                    )
                    if chain_break and last_result is None:
                        break
                elif operation['type'] == 'parallel':
                    last_result = await self._execute_parallel(
                        operation['factories'],
                        parent_task,
                        operation.get('max_concurrent'),
                    )

            except Exception as e:
                logger.exception(f"编排器 {self.name} 第{op_index + 1}步异常: {e}")
                break

        return last_result

    async def _execute_chain(self,
                             factories: List[ChainFactory],
                             parent_task: Optional[Task],
                             last_result: Any,
                             chain_break: bool) -> Any:
        """
        执行串行链（使用TaskChain实现）
        """
        chain = TaskChain(name=f"{self.name}_chain")

        # 桥接信号
        chain.sub_task_signal.bridge_other_signal(self.sub_task_signal)

        # 添加工厂函数
        chain.add_factories(*factories)

        # 执行
        result = await chain.execute(parent_task, last_result, chain_break)

        # 清理
        chain.clear()

        return result

    async def _execute_parallel(self,
                                factories: List[ParallelFactory],
                                parent_task: Optional[Task],
                                max_concurrent: int) -> List[Any]:
        """
        执行并行组（使用ParallelTaskGroup实现）
        """
        group = ParallelTaskGroup(
            name=f"{self.name}_parallel",
            max_concurrent=max_concurrent
        )

        # 桥接信号
        group.sub_task_signal.bridge_other_signal(self.sub_task_signal)

        # 添加工厂函数
        group.add_factories(*factories)

        # 执行
        results = await group.execute(parent_task)

        # 清理
        group.clear()

        return results

    def clear(self) -> None:
        """
        清理编排器

        功能:
        - 清理全局共享信号连接
        - 清空所有操作记录
        """
        self.sub_task_signal.clear(compulsory=True)
        self.operations.clear()
