"""UI工作流"""
from SubWidget.ImportPack import *
from typing import Optional


class SearchWorkFlow(Task):
    """搜索任务工作流"""

    def __init__(self, params: WH.Config.SearchParams,
                 start_signal: Signal, progress_signal: Signal, finish_signal: Signal,
                 search_all=False, use_network=True, use_cache=True, use_tags=False):
        super().__init__(self.__execute, AppCore().getWorkFlowPoolNowait, name='SearchWorkFlow')
        self.clear_callback()
        self.task = WHAPI.search_task(params, search_all, use_network, use_cache, True, use_tags)
        self.task.start_signal.connect(start_signal.emit)
        self.task.progress_signal.connect(progress_signal.emit)
        self.task.finish_signal.connect(finish_signal.emit)

    def __execute(self) -> pd.DataFrame | None:
        self.task.start()
        # WHAPI.stop_thumb_task()

    def stop(self) -> bool:
        self.task.stop()
        return super().stop()

    def result(self, wait=None) -> pd.DataFrame | None:
        return super().result(wait)


class ThumbWorkFlow(Task):
    """略缩图任务工作流"""

    def __init__(self, thumb_url, key_word, start_signal: Signal, finished_signal: Signal, ):
        super().__init__(self.__execute, AppCore().getWorkFlowPoolNowait, name='ThumbWorkFlow')
        self.clear_callback()
        self.task = WHAPI.thumb_task(thumb_url, key_word)
        self.task.start_signal.connect(start_signal.emit)
        self.task.finish_signal.connect(finished_signal.emit)

    def __execute(self):
        self.task.start()

    def stop(self) -> bool:
        self.task.stop()
        return super().stop()


class DownloadWorkFlow(Task):
    """下载任务流"""
    All_Work_Flow = {}  # 依照url存储了全部实例
    __lock = Lock()

    def __init__(self, key_word, url, save=True):
        super().__init__(self.__execute, AppCore().getWorkFlowPool, name='DownloadWorkFlow')
        self.clear_callback()  # 清空自带的finish_signal回调
        self.key_word = key_word
        self.url = url
        self.save = save
        # 下载任务
        self.download_task = WHAPI.download_task(url, key_word)
        self.download_task.progress_signal.connect(self.progress_signal.emit)
        # 图像信息任务
        self.info_task = WHAPI.image_info_task(self.download_task.image_id, key_word)
        self.info_task.start_signal.connect(self.start_signal.emit)
        # 图像数据
        self.image_data = WH.ImageManage.get_image_data(
            self.download_task.image_id, self.download_task.file_type, key_word)
        with self.__class__.__lock:
            if url not in self.__class__.All_Work_Flow:
                self.__class__.All_Work_Flow[url] = self

    def __execute(self):
        state = True
        self.info_task.start(0)  # 获取图像信息数据,防止图像存在但归属于多个关键词时信息不记录
        # 本地图像数据不存在时提交下载
        if not self.image_data.isExist:
            state = False
            if self.info_task.result() is not None:
                save_path = self.image_data.generate_save_path(self.info_task.result())
                # 本地文件存在则不下载只保存图像信息
                if not FileBase(save_path).exists and self.isRunning:
                    self.download_task.start(0)
                    state = self.image_data.save_image(self.info_task.result()) if self.save else True
                else:
                    self.image_data.save_image_info(self.info_task.result())
                    state = True
        if self.isRunning:
            self.isRunning = False
            self.finish_signal.emit(state)
        with self.__class__.__lock:
            self.__class__.All_Work_Flow.pop(self.url, None)
        gc.collect()

    def setSignal(self, start_signal: Signal, progress_signal: Signal,
                  finish_signal: Signal, stop_singnal: Signal = None):
        """设置信号连接"""
        self.start_signal.connect(start_signal.emit)
        self.progress_signal.connect(progress_signal.emit)
        self.finish_signal.connect(finish_signal.emit)
        if stop_singnal is not None:
            self.stop_signal.connect(stop_singnal.emit)

    def disSignal(self):
        """断开信号连接"""
        self.start_signal.disconnect()
        self.progress_signal.disconnect()
        self.finish_signal.disconnect()

    @classmethod
    def get_work_flow_instance(cls, url: str) -> Optional['DownloadWorkFlow'] | None:
        """获取工作流实例"""
        with cls.__lock:
            return cls.All_Work_Flow.get(url, None)

    def stop(self) -> bool:
        self.info_task.stop()
        self.download_task.stop()
        with self.__class__.__lock:
            self.__class__.All_Work_Flow.pop(self.url, None)
        gc.collect()
        return super().stop()


class UpdateWorkFlow(Task):
    """更新单个关键词任务流"""
    TIME_OUT = 120  # 超时时间,两个文件之间的间隔下载时间超过120秒时停止程序

    def __init__(self, key_word, purity, categories):
        """
        :param key_word: 关键词
        :param purity:分级
        :param categories:分类
        """
        super().__init__(self.__execute, AppCore().getWorkFlowPool, name='UpdateWorkFlow')
        self.clear_callback()
        self.key_word = key_word
        self.purity = purity
        self.categories = categories
        self.local_key_data = None
        self.__lock = Lock()  # 进度计数锁
        self.all_download_work_flow: list[DownloadWorkFlow] = []  # 全部的下载任务工作流
        # 搜索参数
        self.params = WH.get_search_params()
        self.params.q = self.key_word
        self.params.purity = self.purity
        self.params.categories = self.categories
        # 子任务
        # 获取远程第一页数据
        self.remote_first = WHAPI.search_task(self.params, use_network=True, use_cache=False)
        self.remote_first.start_signal.connect(self.start_signal.emit)
        # 获取远程全部数据
        self.remote_all = WHAPI.search_task(self.params, search_all=True, use_network=True, use_cache=False)
        self.remote_all.progress_signal.connect(self.progress_signal.emit)
        # 获取本地全部数据
        self.local_all = WHAPI.search_task(self.params, search_all=True, use_network=False, use_cache=False)

    def __execute(self):
        self.isRunning = True
        state = False
        print(f'{self.key_word} 执行更新中')
        # 获取远程第一页数据和全部本地数据
        if self.__step_one():
            # 更新关键词数据,不使用本地数据,step_one已经搜索了本地数据
            key_task = WHAPI.key_word_task(self.params, use_cache=False)
            self.local_key_data = key_task.start(0)
            # 筛选出需要下载的文件
            image_url = self.__step_two()
            state = True
            if image_url:
                self.progress_signal.emit(image_url)
                self.progress.total = len(image_url)
                # 监听下载进度
                state = self.__step_three(image_url)
        if self.isRunning:
            self.finish_signal.emit(state)

    def setSignal(self, start_signal: Signal, progress_signal: Signal, finish_signal: Signal, stop_signal: Signal):
        """设置信号连接"""
        self.start_signal.connect(start_signal.emit)
        self.progress_signal.connect(progress_signal.emit)
        self.finish_signal.connect(finish_signal.emit)
        self.stop_signal.connect(stop_signal.emit)

    def disSignal(self):
        """断开信号连接"""
        self.start_signal.disconnect()
        self.progress_signal.disconnect()
        self.finish_signal.disconnect()
        self.stop_signal.disconnect()

    def stop(self):
        self.remote_first.stop()
        self.remote_all.stop()
        self.local_all.stop()
        for work_flow in self.all_download_work_flow:
            work_flow.stop()
        return super().stop()

    def __download_finished(self, value, work_flow: DownloadWorkFlow):
        if self.isRunning:
            if value:
                with self.__lock:
                    self.start_time = time.time()
                    self.progress.finished += 1
                self.progress_signal.emit(self.progress)
            else:
                if work_flow.countRun < 3:
                    work_flow.start()

    def __step_one(self) -> bool:
        if self.isRunning:
            self.remote_first.start(0)
            self.local_all.start(0)
            if self.remote_first.result() is not None:
                return True
        return False

    def __step_two(self) -> list | None:
        """比对云端数据筛选出需要下载的图像"""
        if self.isRunning:
            # 对比本地数据和远程数据是否一致
            result = self.remote_first.result()
            local_result = self.local_all.result()
            if local_result is not None:
                # 对比云端数据与本地数据数量和日期是否对的上,云端可能会有图片被删除的情况
                if (result.loc[0, '日期'] > local_result.loc[0, '日期'] or
                        result.loc[0, '总数'] > local_result.loc[0, '总数']):
                    # 搜索全部云端文件,如果已经搜索过则直接使用
                    remote_result = self.remote_all.result()
                    if remote_result is None:
                        remote_result = self.remote_all.start(0)
                    if remote_result is not None:
                        # 选出差异文件
                        image_url = remote_result.loc[~remote_result['远程路径'].isin(
                            local_result['远程路径']), ['关键词', '远程路径']].values.tolist()
                        return image_url
            else:
                # 搜索全部云端文件,如果已经搜索过则直接使用
                remote_result = self.remote_all.result()
                if remote_result is None:
                    remote_result = self.remote_all.start(0)
                if remote_result is not None:
                    # 选出差异文件
                    image_url = remote_result[['关键词', '远程路径']].values.tolist()
                    return image_url

    def __step_three(self, image_url: list):
        """监听下载是否完成"""
        # 添加下载任务的回调函数
        for key_word, url in image_url:
            while self.isRunning:
                work_flow = DownloadWorkFlow.get_work_flow_instance(url)
                if work_flow is not None:
                    self.all_download_work_flow.append(work_flow)
                    work_flow.finish_signal.connect(
                        lambda value, work=work_flow: self.__download_finished(value, work))
                    work_flow.stop_signal.connect(
                        lambda value, work=work_flow: self.__download_finished(value, work))
                    work_flow.start()
                    break
                else:
                    time.sleep(0)
        # 等待下载任务完成
        with self.__lock:
            self.start_time = time.time()
        while self.isRunning:
            if self.progress.get_progress() == 100:
                return True
            else:
                with self.__lock:
                    if self.start_time + self.__class__.TIME_OUT <= time.time():
                        break
                time.sleep(1)
        self.stop()
        return False


class SerialWorkFlow(Task):
    """串行工作流"""

    def __init__(self, task_list: list[Task] = None):
        super().__init__(self.__execute, AppCore().getWorkFlowPool, name='SerialWorkFlow')
        self.task_list = task_list if task_list is not None else []
        self.current_task: Task = None  # 当前正在执行的任务
        self.__lock = Lock()

    def add_task(self, task: Task | list[Task]):
        with self.__lock:
            if isinstance(task, Task) and task not in self.task_list:
                self.task_list.append(task)
            else:
                task = list(filter(lambda x: x not in self.task_list, task))
                self.task_list.extend(task)

    def del_task(self, task: Task | list[Task]):
        with self.__lock:
            if isinstance(task, Task):
                if task in self.task_list:
                    self.task_list.remove(task)
            else:
                for t in task:
                    if task in self.task_list:
                        self.task_list.remove(t)

    def __execute(self):
        while self.isRunning:
            try:
                gc.collect()
                with self.__lock:
                    self.progress.total = len(self.task_list) + self.progress.finished
                    self.current_task = self.task_list.pop(0)
                self.current_task.start(0)
                self.progress.finished += 1
                self.progress_signal.emit(self.progress)
            except IndexError:
                if self.isRunning:
                    self.finish_signal.emit(True)  # 执行完成
                self.isRunning = False
                self.progress = TaskProgress()
                return
        self.isRunning = False
        self.finish_signal.emit(False)  # 任务中断

    def stop(self) -> bool:
        state = super().stop()
        self.current_task.stop()
        self.progress = TaskProgress()
        self.task_list.clear()
        return state
