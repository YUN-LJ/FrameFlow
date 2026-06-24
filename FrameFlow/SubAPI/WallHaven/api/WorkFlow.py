"""
任务工作流,工作流由异步池管理
"""
import pandas as pd

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
        task.set_retry_count(3)  # 设置重试次数
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
    下载任务流,任务成功后返回ImageData实例,否则返回None
    使用TaskOrchestrator简化任务链管理
    注意:完成信号发射每个子任务的完成
        即按顺序发射ImageInfoTask->DownloadTask->DownloadWorkFlow
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
            self.image_data: Optional[ImageData] = None
            self.append_time = time.time()
            DownloadWorkFlowManage.append_work_flow(self)

    async def __execute(self) -> ImageData | None:
        """
        使用编排器简化的执行逻辑
        """
        try:
            orchestrator = TaskChain(f"{self.__class__.name}_{self.params.image_id}")

            # 第一步:获取图像信息
            orchestrator.add(self.params.image_info_task)

            # 第二步:下载图像
            orchestrator.add_factories(self._create_download_task)

            # 第三步:保存图像(如果需要)
            if self.params.save:
                orchestrator.add_factories(self._create_save_task)

            # 连接信号
            orchestrator.sub_task_signal.start_signal.connect(
                lambda task: self.start_signal.emit(task)
            )  # 开始信号
            orchestrator.sub_task_signal.progress_signal.connect(
                lambda task: self.progress_emit(task.progress)
            )  # 进度信号
            orchestrator.sub_task_signal.finish_signal.connect(
                lambda task: self.finish_signal.emit(task)
            )  # 完成信号

            # 执行编排
            result = await orchestrator.execute(parent_task=self, chain_break=True)

            # 清理编排器
            orchestrator.clear()

            # 返回结果
            if isinstance(result, ImageData):
                return result
            elif isinstance(result, bool):
                if result:
                    return self.image_data
                else:
                    return None

        except Exception as e:
            logger.exception(f'{self.__class__.__name__} {self.params.image_id} 执行失败 {e}')
            return None

    def _create_download_task(self, image_info):
        """创建下载任务的工厂函数"""
        if image_info is not None:
            self.params.image_info = image_info
        download_task = DownloadTask(self.params.url)
        return download_task

    def _create_save_task(self, image_data: ImageData):
        """创建保存任务的工厂函数"""
        if image_data is not None:
            self.image_data = image_data
            local_path = self.params.image_info['本地路径'].values[0]
            if not local_path or not FileBase(local_path).exists:
                save_task = Task(
                    self.image_data.save_image,
                    GlobalValue.GLOBAL_TASK_MANAGE,
                    args=(self.params.save_path, self.params.cover, self.params.image_info))
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
                 create_func: Callable[[DownloadWorkFlow], DownloadWorkFlow] = None,
                 max_concurrent: int = 4,
                 max_retries: int = 3,
                 lazy_create: bool = True):
        """
        :param params:下载参数列表
        :param create_func:指定创建函数,传入DownloadWorkFlow(用于精细化控制每个下载)
        :param max_concurrent: 最大并发数量,默认为4
        :param max_retries:最大重试次数,默认为3
        :param lazy_create:惰性创建,默认开启
        """
        super().__init__(self.__execute, GlobalValue.GLOBAL_TASK_ASYNC_MANAGE,
                         name='DownloadBatchWorkFlow', use_async=True)
        self.params = params
        self.create_func = create_func
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.lazy_create = lazy_create

    async def __execute(self):
        orchestrator = ParallelTaskGroup(f'{self.__class__.__name__}_{self.name}', self.max_concurrent)

        # 提交执行函数
        if self.create_func is None:
            if self.lazy_create:
                orchestrator.add_factories(*[
                    lambda p=param: DownloadWorkFlow(p) for param in self.params
                ])
            else:
                orchestrator.add_tasks([
                    DownloadWorkFlow(param) for param in self.params
                ])
        else:
            if self.lazy_create:
                orchestrator.add_factories(*[
                    lambda p=param: self.create_func(DownloadWorkFlow(p)) for param in self.params
                ])
            else:
                orchestrator.add_tasks([
                    self.create_func(DownloadWorkFlow(param)) for param in self.params
                ])

        # 连接信号
        orchestrator.sub_task_signal.progress_signal.bridge_signal(self.progress_signal)

        # 等待执行结果
        result = await orchestrator.execute(parent_task=self)

        # 清理
        orchestrator.clear()

        return result


class UpdateWorkFlow(Task):
    """
    更新单个关键词任务流
        任务流程:判断是否需要更新->依次下载每一页数据->检查数据是否齐全->更新下一页
        内部搜索数据采用按时间升序排序(这样如果以后有新增数据,只需要更新后续页即可)
    开始信号首次发送UpdateWorkFlow
    开始信号第二次发送KeyWordTask
    进度信号发送UpdateWorkFlow
    完成和停止信号发送UpdateWorkFlow
    """
    TIME_OUT = 75  # 超时时间,当前下载任务长时间不活跃时触发超时信号
    SEARCH_STATE = 0  # 搜索数据状态
    DOWNLOAD_STATE = 1  # 下载数据状态

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
        self._state = self.SEARCH_STATE

    def setParams(self, purity, categories):
        """修改搜索参数"""
        self.purity = purity
        self.categories = categories
        self.search_params.purity = purity
        self.search_params.categories = categories

    async def _check_update(self) -> bool:
        """检查是否需要更新"""
        # 获取新旧数据
        params = self.search_params.copy()
        params.page = 1
        params.sorting = 'desc'
        with SearchTask(params, use_network=False, use_cache=False) as search_task:
            old_key_word_data: Optional[pd.DataFrame] = await search_task.start_async(0, parent_task=self)
        with KeyWordTask(params, use_cache=False) as key_word_task:
            new_key_word_data: Optional[pd.DataFrame] = await key_word_task.start_async(0, parent_task=self)

        # 判断是否需要更新
        if old_key_word_data is None or new_key_word_data is None:
            return True
        elif any((new_key_word_data['最新日期'].iloc[0] > old_key_word_data['日期'].iloc[0],
                  new_key_word_data['总数'].iloc[0] > old_key_word_data['总数'].iloc[0])):
            return True
        else:
            return False

    async def _update_page(self, page: int) -> bool:
        """下载某一页数据,内容按照升序排序"""
        params = self.search_params.copy()
        params.page = page
        params.sorting = 'asc'  # 升序

        # 获取数据
        self._state = self.SEARCH_STATE
        with SearchTask(params, use_cache=False) as search_task:
            result: Optional[pd.DataFrame] = await search_task.start_async(0, parent_task=self)

        # 筛选后的数据
        if result is None:
            return False

        result = self._filter_search_data(result)

        # 下载数据
        return await self._batch_download(result)

    async def _batch_download(self, search_result: pd.DataFrame) -> bool:
        """批量下载图像"""
        # 提交下载任务
        self._state = self.DOWNLOAD_STATE
        download_batch_work_flow = DownloadBatchWorkFlow(
            [DownloadWorkFlow.Params(row['id'], self.key_word, url=row['远程路径'])
             for index, row in search_result.iterrows()],  # 下载参数
            self._create_func, lazy_create=False  # 创建下载任务函数
        )
        self.progress.finished = 0
        self.progress.total = len(search_result)
        results: Optional[list] = await download_batch_work_flow.start_async(0, parent_task=self)
        self.progress_signal.emit(self)

        download_batch_work_flow.clear()

        if results is None:
            return False
        else:
            return all(results)

    @staticmethod
    def _filter_search_data(search_result: pd.DataFrame) -> pd.DataFrame:
        """筛选搜索后的数据,剔除掉已经存在的数据"""
        with IMAGE_INFO as df:
            # 筛选出search_result中不在IMAGE_INFO的数据
            filter_search_result = search_result[~search_result['id'].isin(df['id'])]
            return filter_search_result

    @property
    def isSearch(self) -> bool:
        return self._state == self.SEARCH_STATE

    @property
    def isDownload(self) -> bool:
        return self._state == self.DOWNLOAD_STATE

    async def __execute(self) -> bool:
        logger.info(f'{self.__class__.__name__} 开始更新:{self.name}')

        # 获取上次更新页码和最大页码
        with KEY_WORD as df:
            last_update_page = df.loc[df['关键词'] == self.key_word, '上次更新页码'].copy(deep=True)
            max_page = df.loc[df['关键词'] == self.key_word, '总页数'].copy(deep=True)

            if last_update_page.empty:
                last_update_page = 1
            else:
                last_update_page = int(last_update_page.iloc[0])

            if max_page.empty:
                logger.warning(f'{self.__class__.__name__} 更新失败:{self.name} 无最大页码')
                return False
            else:
                max_page = int(max_page.iloc[0])

            if last_update_page >= max_page:  # 如果上次更新页码大于等于最大页码则等于最大页码减1
                last_update_page = max_page - 1

        # 检查是否需要更新
        if not await self._check_update():
            KEY_WORD.set_update_page(self.key_word, max_page)
            logger.info(f'{self.__class__.__name__} 更新成功:{self.name}')
            return True

        if not self.isRunning:
            logger.info(f'{self.__class__.__name__} 更新取消:{self.name}')
            return False

        # 逐页更新
        for page in range(max(1, last_update_page), max_page + 1):
            if not self.isRunning:
                logger.info(f'{self.__class__.__name__} 更新取消:{self.name}')
                return False
            state = await self._update_page(page)

            # 发送进度
            self._state = self.SEARCH_STATE
            self.progress.finished = page
            self.progress.total = max_page
            self.progress_signal.emit(self)

            if state:
                KEY_WORD.set_update_page(self.key_word, page)
            else:
                logger.warning(f'{self.__class__.__name__} 更新失败:{self.name} 第{page}页')
                return False
        if not await self._check_update():
            logger.info(f'{self.__class__.__name__} 更新成功:{self.name}')
            return True
        else:
            KEY_WORD.set_update_page(self.key_word, 1)
            logger.warning(f'{self.__class__.__name__} 更新失败:{self.name} 数据不完整')
            return False

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
        """任务完成后如果成功则会计数,如果失败则会终止本次更新"""
        if self.isRunning and isinstance(work_flow, DownloadWorkFlow):
            self.progress.finished += 1
            self.progress_signal.emit(self)
            with self.__lock:
                if work_flow in self.all_work_flow:
                    self.all_work_flow.remove(work_flow)
            DownloadWorkFlowManage.del_work_flow(work_flow.params.image_id)

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

    @staticmethod
    def __retry_should(result):
        return result

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
                    self.current_task.set_retry_count(3)  # 设置重试次数3次
                    self.current_task.set_retry_should(self.__retry_should)  # 设置重试判断条件

                # 执行任务,任务完成后,如果成功则计数并从任务队列中移除
                await self.current_task.start_async(0, parent_task=self)
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
    def progress_slot(task: UpdateWorkFlow):
        text = '更新页' if task.isSearch else '下载中'
        print(f'{text}:{task.progress.finished}/{task.progress.total}')


    from Fun.BaseTools import LogManager

    LogManager().set_console_output(console_level='DEBUG')

    # 批量更新任务示例
    # task_test = UpdateWorkFlow('Potato Godzilla', '111', '001')
    task_test = UpdateWorkFlow('Windows 11', '100', '010')
    task_test.progress_signal.connect(progress_slot)
    task_test.start(0)

    # 串行批量更新任务示例
    # serial_task = SerialUpdateWorkFlow()
    # serial_task.progress_signal.connect(print)
    # serial_task.add_task('chengzimiaoj', '111', '001')
    # serial_task.add_task('Momo Kawaii', '111', '001')
    # serial_task.start(0)
    # DATA_MANAGE.stop()
