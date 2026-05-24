"""
任务工作流,工作流由异步池管理
"""
from SubAPI.WallHaven.api.Tools import *

logger = LogClass.get_logger(__name__, console_level='WARNING')


class ThumbWorkFlow(Task):
    """略缩图加载任务"""

    def __init__(self, url: str, use_network: bool = True, use_cache: bool = True):
        self.url = url
        self.use_network = use_network
        self.use_cache = use_cache
        self.image_id = None
        super().__init__(self.__execute, GlobalValue.GLOBAL_TASK_ASYNC_MANAGE,
                         name='ThumbWorkFlow', use_async=True)

    async def __execute(self) -> ImageData | None:
        task = DownloadTask(self.url, GlobalValue.GLOBAL_TASK_MANAGE, self.use_network, self.use_cache)
        self.image_id = task.image_id
        task.start_signal.bridge_signal(self.start_signal)
        task.progress_signal.bridge_signal(self.progress_signal)
        task.finish_signal.bridge_signal(self.finish_signal)
        task.stop_signal.bridge_signal(self.stop_signal)
        return await task.start_async(0, 2, self)


class DownloadWorkFlowManage:
    """
    下载任务工作流管理
    新增工作流时发送新增信号,工作流的生命周期可连接工作流的信号获取
    任务成功完成后会从All_Work_Flow中删除,失败的任务则不会删除,方便重试
    """
    # 图像id:工作流,采用弱引用值字典,值被gc回收时自定删除对应的键
    All_Work_Flow: dict[str, 'DownloadWorkFlow'] = {}
    __lock = RLock()

    # 信号
    appendWorkFlowSignal = TaskSignal()  # 发送新增的DownloadWorkFlow对象
    removeWorkFlowSignal = TaskSignal()  # 发送删除的DownloadWorkFlow对象

    @classmethod
    def append_work_flow(cls, work_flow: 'DownloadWorkFlow') -> bool:
        """添加工作流"""
        with cls.__lock:
            if work_flow.params.image_id not in cls.All_Work_Flow:
                # 成功完成任务时清理引用
                work_flow.add_done_callback(cls.__work_flow_end)
                # 添加工作流
                cls.All_Work_Flow[work_flow.params.image_id] = work_flow
                cls.appendWorkFlowSignal.emit(work_flow)
                return True
            return False

    @classmethod
    def get_work_flow(cls, image_id: str) -> 'DownloadWorkFlow':
        """获取工作流"""
        with cls.__lock:
            return cls.All_Work_Flow.get(image_id, None)

    @classmethod
    def get_all_work_flow(cls) -> dict[str, 'DownloadWorkFlow']:
        """获取所有工作流,返回副本"""
        with cls.__lock:
            return cls.All_Work_Flow.copy()

    @classmethod
    def get_all_work_flow_by_sorted(cls) -> list['DownloadWorkFlow']:
        """获取所有工作流,返回按添加时间进行排序的副本"""
        return sorted(cls.get_all_work_flow().values(), key=lambda x: x.append_time)

    @classmethod
    def __work_flow_end(cls, work_flow: 'DownloadWorkFlow'):
        """任务结束时,删除成功完成的任务"""
        if work_flow.result() is not None:
            with cls.__lock:
                cls.All_Work_Flow.pop(work_flow.params.image_id, None)
            cls.removeWorkFlowSignal.emit(work_flow)

    @classmethod
    def start_all_work_flow(cls):
        """开始所有任务"""
        with cls.__lock:
            for work_flow in cls.All_Work_Flow.values():
                work_flow.start()

    @classmethod
    def stop_all_work_flow(cls):
        """停止所有任务"""
        with cls.__lock:
            for work_flow in cls.All_Work_Flow.values():
                work_flow.stop()

    @classmethod
    def clear_all_work_flow(cls):
        """清空全部任务"""
        with cls.__lock:
            for work_flow in cls.All_Work_Flow.values():
                work_flow.stop()
                cls.removeWorkFlowSignal.emit(work_flow)
            cls.All_Work_Flow.clear()

    @classmethod
    def del_work_flow(cls, image_id: str):
        """删除任务"""
        with cls.__lock:
            work_flow = cls.All_Work_Flow.pop(image_id, None)
            cls.removeWorkFlowSignal.emit(work_flow)
            if work_flow is not None:
                work_flow.stop()


class DownloadWorkFlow(Task):
    """
    下载任务流(重构版)
    使用TaskOrchestrator简化任务链管理
    """

    class Params:
        """下载参数"""

        def __init__(self, image_id: str, key_word: str, save=True, cover=False,
                     url: str = None, image_info: pd.DataFrame = None, save_path=None, extension=None):
            self.image_id = image_id
            self.key_word = key_word
            self.save = save
            self.cover = cover
            self.save_path = save_path
            self.__image_info = image_info
            self.__url = url
            self.extension = extension
            self.image_info_task = ImageInfoTask(self.image_id, self.key_word)

        @property
        def url(self) -> str | None:
            return self.__url

        @property
        def image_info(self) -> pd.DataFrame | None:
            return self.__image_info

        @image_info.setter
        def image_info(self, image_info: pd.DataFrame):
            self.__image_info = image_info
            self.extension = image_info['文件扩展名'].values[0]
            self.__url = image_info['远程路径'].values[0]

        def copy(self) -> 'DownloadWorkFlow.Params':
            return self.__class__(
                self.image_id,
                self.key_word,
                self.save,
                self.cover,
                self.url,
                self.image_info,
                self.save_path,
                self.extension
            )

        def __eq__(self, other):
            if not isinstance(other, self.__class__):
                return False
            attrs = ['image_id', 'key_word']
            return all(getattr(self, attr) == getattr(other, attr) for attr in attrs)

    def __new__(cls, params: Params):
        existing_workflow = DownloadWorkFlowManage.get_work_flow(params.image_id)
        if existing_workflow is not None:
            return existing_workflow
        instance = super().__new__(cls)
        return instance

    def __init__(self, params: Params):
        if DownloadWorkFlowManage.get_work_flow(params.image_id) is None:
            super().__init__(self.__execute, GlobalValue.GLOBAL_TASK_ASYNC_MANAGE,
                             name='DownloadWorkFlow', use_async=True)
            self.params = params
            self.image_data = None
            self.append_time = time.time()
            DownloadWorkFlowManage.append_work_flow(self)

    async def __execute(self) -> ImageData | None:
        """
        使用编排器简化的执行逻辑
        """

        def step_one():
            return self.params.image_info_task

        try:
            orchestrator = TaskOrchestrator(f"Download_{self.params.image_id}", max_retries=3)

            # 第一步:获取图像信息
            orchestrator.chain(step_one)

            # 第二步:下载图像
            orchestrator.chain(self._create_download_task)

            # 第三步:保存图像(如果需要)
            if self.params.save:
                orchestrator.chain(self._create_save_task)
            # 连接信号
            orchestrator.sub_task_signal.progress_signal.connect(
                lambda task: self.progress_emit(task.progress))

            # 执行编排
            result = await orchestrator.execute(parent_task=self, chain_break=True)

            # 清理编排器
            orchestrator.clear()

            return result if isinstance(result, ImageData) else self.image_data

        except Exception as e:
            logger.exception(f'{self.__class__.__name__} {self.params.image_id} 执行失败 {e}')
            return None

    def _create_download_task(self, image_info):
        """创建下载任务的工厂函数"""
        if image_info is not None:
            self.params.image_info = image_info
        download_task = DownloadTask(self.params.url)
        return download_task

    def _create_save_task(self, image_data):
        """创建保存任务的工厂函数"""
        if image_data is not None:
            self.image_data = image_data
            local_path = self.params.image_info['本地路径'].values[0]
            if not local_path or not FileBase(local_path).exists:
                save_task = Task(
                    image_data.save_image,
                    GlobalValue.GLOBAL_TASK_MANAGE,
                    args=(self.params.save_path, self.params.cover)
                )
                return save_task
        return None

    def setSignal(self, start_signal, progress_signal, finish_signal, stop_signal=None):
        self.start_signal.connect(start_signal.emit)
        self.progress_signal.connect(progress_signal.emit)
        self.finish_signal.connect(finish_signal.emit)
        if stop_signal is not None:
            self.stop_signal.connect(stop_signal.emit)

    def disSignal(self):
        self.start_signal.disconnect()
        self.progress_signal.disconnect()
        self.finish_signal.disconnect()


class DownloadBatchWorkFlow(Task):
    """批量下载"""

    def __init__(self,
                 params: Iterable[DownloadWorkFlow.Params],
                 create_func: Callable = None,
                 max_concurrent: int = 4,
                 max_retries: int = 3):
        """
        :param params:下载参数列表
        :param create_func:指定创建函数,传入DownloadWorkFlow(用于精细化控制每个下载)
        :param max_concurrent: 最大并发数量,默认为4
        :param max_retries:最大重试次数,默认为3
        """
        super().__init__(self.__execute, GlobalValue.GLOBAL_TASK_ASYNC_MANAGE,
                         name='DownloadBatchWorkFlow', use_async=True)
        self.params = params
        self.create_func = create_func
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries

    async def __execute(self):
        orchestrator = TaskOrchestrator(self.name, self.max_concurrent)
        if self.create_func is None:
            orchestrator.parallel([
                (lambda p=param: DownloadWorkFlow(p)) for param in self.params
            ], self.max_concurrent)
        else:
            orchestrator.parallel([
                (lambda p=param: self.create_func(DownloadWorkFlow(p))) for param in self.params
            ], self.max_concurrent)
        orchestrator.sub_task_signal.progress_signal.bridge_signal(self.progress_signal)
        return await orchestrator.execute(parent_task=self)


class UpdateWorkFlow(Task):
    """
    更新单个关键词任务流
    开始信号首次发送UpdateWorkFlow
    开始信号第二次发送KeyWordTask
    进度信号发送UpdateWorkFlow
    完成和停止信号发送UpdateWorkFlow
    """
    TIME_OUT = 75  # 超时时间,当前下载任务长时间不活跃时触发超时信号
    SEARCH_STATE = 0
    DOWNLOAD_STATE = 1

    def __init__(self, key_word, purity, categories):
        """
        :param key_word: 关键词
        :param purity:分级
        :param categories:分类
        """
        self.key_word = key_word
        self.purity = purity
        self.categories = categories
        self.local_key_data = None
        super().__init__(self.__execute, GlobalValue.GLOBAL_TASK_ASYNC_MANAGE,
                         name=f'UpdateWorkFlow_关键词:{self.key_word}_分级:{self.purity}_分类:{self.categories}',
                         use_async=True)
        # 搜索参数
        self.search_params = get_search_params()
        self.search_params.q = self.key_word
        self.search_params.purity = self.purity
        self.search_params.categories = self.categories
        # 任务结果
        self.remote_first_result: Optional[pd.DataFrame] = None  # 全程第一页结果
        self.local_all_result: Optional[pd.DataFrame] = None  # 本地全部结果
        self.__remote_all_result: Optional[pd.DataFrame] = None  # 远程全部结果
        # 属性
        self.timeout = None  # 上一个下载任务完成的时间
        self.all_work_flow: list[DownloadWorkFlow] = []
        self.__lock = Lock()
        # 外部桥接的信号
        self._start_signal_set: set[Signal] = set()
        self._progress_signal_set: set[Signal] = set()
        self._finish_signal_set: set[Signal] = set()
        self._stop_signal_set: set[Signal] = set()

    def setParams(self, purity, categories):
        """修改搜索参数"""
        self.purity = purity
        self.categories = categories
        self.search_params.purity = purity
        self.search_params.categories = categories

    @property
    def remote_all_result(self) -> pd.DataFrame | None:
        def progress_emit(value: SearchTask):
            self.progress.finished = value.progress.finished
            self.progress.total = value.progress.total
            self.progress_signal.emit(self)

        if self.__remote_all_result is None:
            # 获取远程全部数据
            remote_all = SearchTask(self.search_params, search_all=True, use_network=True, use_cache=False)
            remote_all.progress_signal.connect(progress_emit)
            self.__remote_all_result = remote_all.start(0, parent_task=self)
        return self.__remote_all_result

    @property
    def get_progress_state(self) -> int:
        with self.__lock:
            if len(self.all_work_flow) > 0:
                return self.DOWNLOAD_STATE
        return self.SEARCH_STATE

    async def __execute(self) -> bool:

        def step_two() -> pd.DataFrame | None:
            """比对云端数据筛选出需要下载的图像,返回None表示不需要更新"""
            if self.local_all_result is not None:  # 本地存在数据
                # 对比云端数据与本地数据数量和日期是否对的上,云端可能会有图片被删除的情况
                if (self.remote_first_result.loc[0, '日期'] > self.local_all_result.loc[0, '日期'] or
                        self.remote_first_result.loc[0, '总数'] > self.local_all_result.loc[0, '总数']):
                    if self.remote_all_result is not None:
                        # 选出差异图像搜索结果
                        diff_image_search_result = self.remote_all_result[
                            ~self.remote_all_result['id'].isin(self.local_all_result['id'])]
                        return diff_image_search_result
                    else:
                        return pd.DataFrame()
            else:
                if self.remote_first_result is not None:
                    return self.remote_first_result

        async def step_three(diff_image_search_result: pd.DataFrame) -> bool:
            """提交下载任务并等待完成"""
            with self.__lock:
                self.all_work_flow.clear()
            logger.debug(f'{self.__class__.__name__} 提交下载任务:{self.key_word}')
            # 提交下载任务
            download_batch_work_flow = DownloadBatchWorkFlow(
                [DownloadWorkFlow.Params(row['id'], self.key_word, url=row['远程路径'])
                 for index, row in diff_image_search_result.iterrows()],  # 下载参数
                self._create_func  # 创建下载任务函数
            )
            with self.__lock:
                self.progress.finished = 1
            self.progress.total = len(diff_image_search_result)
            self.progress_signal.emit(self)  # 通知外部进入下载阶段
            # 等待下载任务完成
            logger.debug(f'{self.__class__.__name__} 等待下载任务:{self.name}')
            results = await download_batch_work_flow.start_async(0, parent_task=self)
            self.__clear_all_work_flow()
            return all(results)

        logger.info(f'{self.__class__.__name__} 开始更新:{self.name}')
        # 获取远程第一页数据已经更新本地关键词数据和本地全部数据
        orchestrator = TaskOrchestrator(self.name)
        orchestrator.parallel([
            # 更新关键词数据,不使用本地数据,确保数据准确性
            lambda: KeyWordTask(self.search_params, use_cache=False),
            # 搜索远程第一页数据
            lambda: SearchTask(self.search_params, use_cache=False),
            # 获取本地全部数据
            lambda: SearchTask(self.search_params, search_all=True, use_network=False, use_cache=False),
        ])
        results = await orchestrator.execute(parent_task=self)
        orchestrator.clear()
        if results[0] is None or results[1] is None:
            return False
        self.remote_first_result = results[1]
        self.local_all_result = results[2]
        self.progress_signal.emit(self)
        # 第二步筛选出需要下载的文件
        diff_result = step_two()
        if diff_result is not None:
            if not diff_result.empty:
                # 提交下载任务
                return await step_three(diff_result)
        logger.info(f'{self.__class__.__name__} 更新成功:{self.name}')
        return True

    def setSignal(self, start_signal: Signal, progress_signal: Signal, finish_signal: Signal, stop_signal: Signal):
        """设置信号连接"""
        self.start_signal.connect(start_signal.emit)
        self.progress_signal.connect(progress_signal.emit)
        self.finish_signal.connect(finish_signal.emit)
        self.stop_signal.connect(stop_signal.emit)
        # 保留记录
        self._start_signal_set.add(start_signal)
        self._progress_signal_set.add(progress_signal)
        self._finish_signal_set.add(finish_signal)
        self._stop_signal_set.add(stop_signal)

    def disSignal(self):
        """断开信号连接"""
        for start_signal in self._start_signal_set:
            self.start_signal.disconnect(start_signal.emit)
        for progress_signal in self._progress_signal_set:
            self.progress_signal.disconnect(progress_signal.emit)
        for finish_signal in self._finish_signal_set:
            self.finish_signal.disconnect(finish_signal.emit)
        for stop_signal in self._stop_signal_set:
            self.stop_signal.disconnect(stop_signal.emit)

        # 清空集合
        self._start_signal_set.clear()
        self._progress_signal_set.clear()
        self._finish_signal_set.clear()
        self._stop_signal_set.clear()

    def _create_func(self, work_flow: DownloadWorkFlow) -> DownloadWorkFlow:
        """创建一个下载工作流"""
        work_flow.signal.progress_signal.connect(self.__download_progress)
        work_flow.signal.finish_signal.connect(self.__download_finished)
        with self.__lock:
            self.all_work_flow.append(work_flow)
        return work_flow

    @throttle_reuse_timer_decorator(timeout=5)
    def __download_progress(self):
        """任务进度更新代表任务活跃中"""
        self.timeout = time.time()

    def __download_finished(self, work_flow: DownloadWorkFlow):
        """任务完成后如果成功则会计数,如果失败则会重试,同一任务重试次数超过3次则会终止本次更新"""
        if self.isRunning:
            if work_flow.result() is not None:
                self.timeout = time.time()
                self.progress.finished += 1
                self.progress_signal.emit(self)
                with self.__lock:
                    self.all_work_flow.remove(work_flow)
            elif work_flow.countRun < 3:
                work_flow.start()
            else:
                self.stop()

    def __clear_all_work_flow(self):
        """清除所有任务"""
        for work_flow in self.all_work_flow:
            DownloadWorkFlowManage.del_work_flow(work_flow.params.image_id)
            work_flow.clear()
        self.all_work_flow.clear()

    def stop(self) -> bool:
        self.__clear_all_work_flow()
        return super().stop()


class SerialUpdateWorkFlow(Task):
    """串行更新任务"""

    def __init__(self):
        super().__init__(self.__execute, GlobalValue.GLOBAL_TASK_ASYNC_MANAGE,
                         name='SerialUpdateWorkFlow', use_async=True)
        self.task_list: list[tuple[str, str, str]] = []
        # 子类任务信号
        self.sub_task_signal = TaskSignalParams(is_shared=True)
        self.current_task = None  # 当前正在执行的任务
        self.__lock = Lock()

    def add_task(self, key_word: str, purity: str, categories: str):
        """添加任务"""
        with self.__lock:
            params = (key_word, purity, categories)
            if params not in self.task_list:
                self.task_list.append(params)

    def del_task(self, key_word: str, purity: str, categories: str):
        """删除任务"""
        with self.__lock:
            params = (key_word, purity, categories)
            if params in self.task_list:
                self.task_list.remove(params)

    def sort_task(self):
        """任务排序"""
        self.task_list.sort(key=lambda x: x[0])

    async def __execute(self) -> bool:
        logger.info(f'{self.__class__.__name__} 批量更新任务开始执行 队列长度{len(self.task_list)}')
        while self.isRunning:
            try:
                # 取出任务
                if self.current_task is None:
                    with self.__lock:
                        self.progress.total = len(self.task_list) + self.progress.finished
                        key_word, purity, categories = self.task_list[0]
                    self.current_task = UpdateWorkFlow(key_word, purity, categories)
                    self.current_task.set_signal(self.sub_task_signal)
                # 同一任务重试三次后则删除并继续
                elif self.current_task.executor.run_count >= 3:
                    self.del_task(self.current_task.key_word, self.current_task.purity, self.current_task.categories)
                    self.current_task.clear()
                    self.current_task = None
                    await asyncio.sleep(0.1)
                    continue
                # 执行任务,任务完成后,如果成功则计数并从任务队列中移除
                elif await self.current_task.start_async(0, parent_task=self):
                    self.progress.finished += 1
                    self.progress_signal.emit(self.progress)
                    self.del_task(self.current_task.key_word, self.current_task.purity, self.current_task.categories)
                    self.current_task.clear()
                    self.current_task = None
            except IndexError:
                logger.info(f'{self.__class__.__name__} 队列已空,任务执行完毕')
                return True
        return False

    def stop(self) -> bool:
        if self.current_task is not None:
            self.current_task.clear()
        self.current_task = None
        return super().stop()


if __name__ == '__main__':
    from Fun.BaseTools import LogManager

    LogManager().set_console_output(console_level='DEBUG')

    # 批量更新任务示例
    # task_test = UpdateWorkFlow('Potato Godzilla', '111', '001')
    task_test = UpdateWorkFlow('Windows 11', '100', '010')
    task_test.progress_signal.connect(lambda x: print(x.progress, x.name))
    task_test.start(0)

    # 串行批量更新任务示例
    # serial_task = SerialUpdateWorkFlow()
    # serial_task.progress_signal.connect(print)
    # serial_task.add_task('chengzimiaoj', '111', '001')
    # serial_task.add_task('Momo Kawaii', '111', '001')
    # serial_task.start(0)
    # DATA_MANAGE.stop()
