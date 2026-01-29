"""该文件主要是API配套的工具类"""
import pandas as pd

# 导入全局配置
from wallhaven.Config import *


class Signal:
    """信号类,用于线程之间通信"""

    def __init__(self, func=None):
        self.func = ThreadSafe.List()  # 可调用对象列表
        if func is not None:
            self.connect(func)

    def emit(self, value):
        """发送信号"""
        for func in self.func:
            if callable(func):
                func(value)

    def connect(self, func):
        """连接槽函数"""
        if callable(func):
            self.func.append(func)

    def disconnect(self, func=None):
        if func is None:
            self.func.clear()
        else:
            self.func.remove(func)


class DataManager:
    """数据管理:获取锁后再操作表数据"""
    # DatatFrame数据
    IMAGE_INFO = pd.DataFrame(columns=IMAGE_COLUMNS).astype(IMAGE_DTYPE)  # 图像信息
    SEARCH_INFO = pd.DataFrame(columns=SEARCH_COLUMNS).astype(SEARCH_DTYPE)  # 搜索信息
    KEY_WORD = pd.DataFrame(columns=KEY_WORD_COLUMNS).astype(KEY_WORD_DTYPE)  # 收藏夹信息
    # 对应表的锁,无论是读取\修改\新增都需要在锁内完成
    IMAGE_INFO_LOCK = Lock()
    SEARCH_INFO_LOCK = Lock()
    KEY_WORD_LOCK = Lock()
    IMAGE_CACHE = ThreadSafe.Dict()  # {image_id:io.BytesIO} 说明:原图是image_id,略缩图是image_id+扩展名

    def __init__(self, num_work=NUM_WORK):
        self.isRunning = True  # 是否运行
        self.isSave = False  # 是否正在保存
        self.isAutoSave = False  # 自动保存是否正在执行
        self.auto_save_time = 60  # 自动保存间隔
        self.auto_save_timer = Timer(self.auto_save_time, self.auto_save)  # 自动保存定时器
        self.auto_save_timer.daemon = True  # 设置为守护线程,确保主线程退出时,改子线程立即退出

    def load_pd(self, file_path, dtpye, check=False) -> pd.DataFrame:
        extension = file.get_file_extension(file_path)
        # 读取文件
        if extension == '.csv':
            load_pd = pd.read_csv(file_path).astype(dtpye)
        elif extension == '.xlsx':
            load_pd = pd.read_excel(file_path).astype(dtpye)
        elif extension == '.feather':
            load_pd = pd.read_feather(file_path).astype(dtpye)
        if check:
            # load_pd.dropna(how='any', inplace=True)  # 删除有缺失值的行
            # reset_index->删除索引
            load_pd = load_pd[~(load_pd == '').any(axis=1)].reset_index(drop=True)  # 删除有''的行
            # 检查本地路径的文件是否存在,将不存在的路径改为''
            mask = pd.Series(file.check_exist(load_pd['本地路径']))
            load_pd.loc[~mask, '本地路径'] = ''
        return load_pd

    @general.timer_decorator
    def load_data(self, callback):
        state = False
        if file.check_exist(IMAGE_INFO_PATH):
            self.add_image_info(self.load_pd(IMAGE_INFO_PATH, IMAGE_DTYPE, True))
            state = True
            # Thread(target=lambda: self.add_image_info(
            #     self.load_pd(IMAGE_INFO_PATH, IMAGE_DTYPE, True)), daemon=True).start()
        if file.check_exist(KEY_WORD_PATH):
            self.add_key_word(self.load_pd(KEY_WORD_PATH, KEY_WORD_DTYPE))
            state = True
            # Thread(target=lambda: self.add_key_word(
            #     self.load_pd(KEY_WORD_PATH, KEY_WORD_DTYPE)), daemon=True).start()
        Signal(callback).emit(state)

    def add_image_info(self, data):
        """添加图像数据"""
        with self.IMAGE_INFO_LOCK:
            # 表合并+数据去重(链式操作pandas内部有优化且避免线程安全问题)
            self.IMAGE_INFO = pd.concat(
                [self.IMAGE_INFO, data]).drop_duplicates(
                subset=['id'], keep='last', ignore_index=True)

    def add_serach_info(self, data):
        """添加搜索数据"""
        with self.SEARCH_INFO_LOCK:
            self.SEARCH_INFO = pd.concat(
                [self.SEARCH_INFO, data]).drop_duplicates(
                subset=['id', '关键词', '类别码', '分级码'],
                keep='last', ignore_index=True)

    def add_key_word(self, data):
        """添加关键词数据"""
        with self.KEY_WORD_LOCK:
            self.KEY_WORD = pd.concat(
                [self.KEY_WORD, data]).drop_duplicates(
                subset=['关键词'], keep='last').sort_values(
                by='关键词', key=lambda col: col.str.lower(), ignore_index=True)

    def auto_save(self):
        """自动保存"""
        if self.isRunning:
            print(f'\n{self.__class__.__name__}.auto_save :正在保存,当前时间:{get.now_time('%Y-%m-%d %H:%M:%S')}')
            self.isAutoSave = True
            with self.IMAGE_INFO_LOCK:
                self.save(IMAGE_INFO_PATH, self.IMAGE_INFO)
            with self.KEY_WORD_LOCK:
                self.save(KEY_WORD_PATH, self.KEY_WORD)
            self.isAutoSave = False
            # 重新设置定时器
            if self.isRunning:
                self.auto_save_timer = Timer(self.auto_save_time, self.auto_save)
                self.auto_save_timer.daemon = True
                self.auto_save_timer.start()

    def stop(self):
        self.isRunning = False
        # 定时器只有在start()方法后到等待执行的这段时间is_alive的返回值是True
        if self.auto_save_timer.is_alive():
            self.auto_save_timer.cancel()
        while self.isSave or self.isAutoSave:
            time.sleep(1)

    def save(self, file_path: str, df: pd.DataFrame):
        try:
            self.isSave = True
            extension = os.path.splitext(file_path)[1]
            file.ensure_exist(os.path.dirname(file_path))
            if df.empty:
                return True
            if extension == '.xlsx':
                df.to_excel(file_path, index=False)
            elif extension == '.csv':
                df.to_csv(file_path, index=False, encoding='utf-8')
            elif extension == '.feather':
                df.to_feather(file_path)
            self.isSave = False
            return True
        except Exception as e:
            print(f'{self.__class__.__name__}.save error:\n\t{e}')
            return False


class TaskEnum:
    """任务/状态枚举值"""

    class State:
        """任务状态枚举值"""
        notrun = '未开始'
        running = '运行中'
        success = '成功'  # 请求成功并有数据
        fail = '失败'  # 请求成功但没有数据
        cancel = '取消'  # 取消的任务不一定没有数据
        error = '错误'  # 请求失败
        finished = [success, fail, cancel, error]

    class Task:
        """任务枚举值"""

        class Download:
            """
            文件下载
            文件下载与信号发送分开进行
            文件下载由调用start方法的线程负责
            信号的发送由内部创建的子线程发送
            发送的数据结构
            {'name','state','progress','total','rate','data'}
            """

            def __init__(self, name: str, url: str, data_manager: DataManager, signal: Signal):
                self.isRunning = False
                self.signal = signal  # 信号
                self.url = url  # 下载路径
                self.data_manager = data_manager
                # 数据发送线程
                self.signal_thread = Thread(target=self.__signal, daemon=True)
                # 以下为待发送数据
                self.name = name  # 任务名称
                self.state = TaskEnum.State.notrun
                self.progress = 0
                self.total = 0
                self.rate = 0  # 单位kb/s
                self.data = BytesIO()

            def __signal(self):
                """信号发送"""
                while True:
                    value = {
                        'name': self.name,
                        'state': self.state,
                        'progress': self.progress,
                        'total': self.total,
                        'rate': self.rate,
                        'data': self.data
                    }
                    if self.state in TaskEnum.State.finished:
                        self.signal.emit(value)
                        break
                    elif self.state == TaskEnum.State.running:
                        self.signal.emit(value)
                    time.sleep(0.2)

            def __execute(self):
                """任务执行函数"""
                response = request_api(self.url)
                if not response:
                    self.state = TaskEnum.State.error
                    return False
                try:
                    self.total = int(response.headers['content-length'])  # 单位字节(b)
                    chunk_size = 1024 * 8 if self.total >= 1024 * 100 else 1024 * 32
                    up_time = time.time()
                    # iter_content 按chunk_size分块读取
                    # 这里会有可能出现读取超时,即request_api函数
                    # 的time_out的第二个值是指,两次chunk之间的时间不能超过20秒
                    for count, chunk in enumerate(response.iter_content(chunk_size=chunk_size)):
                        if self.isRunning:
                            if chunk:  # 过滤保持连接的chunk
                                self.state = TaskEnum.State.running
                                self.data.write(chunk)
                                self.progress += len(chunk)
                                if (count + 1) % 5 == 0:
                                    time_taken = 1024 * (time.time() - up_time)
                                    up_time = time.time()
                                    self.rate = (chunk_size * 5) / time_taken if time_taken != 0 else 0
                            else:
                                self.state = TaskEnum.State.fail
                                return False
                        else:
                            self.state = TaskEnum.State.cancel
                            return False
                    self.state = TaskEnum.State.success
                    return True
                except Exception as e:
                    print(f'下载任务{self.name} error:\n\t{e}')
                    self.state = TaskEnum.State.error
                    return False

            def stop(self):
                """停止任务"""
                self.isRunning = False

            def start(self):
                """开始任务"""
                self.isRunning = True
                self.state = TaskEnum.State.running
                self.signal_thread.start()
                result = self.data_manager.IMAGE_CACHE.get(self.name)
                if result is None:
                    self.__execute()  # 启动任务
                    if self.state == TaskEnum.State.success:
                        self.data_manager.IMAGE_CACHE[self.name] = self.data
                else:
                    self.data = result
                    self.state = TaskEnum.State.success
                self.isRunning = False

        class Search:
            """
            搜索类任务
            发送的数据结构{'name','state','data'}
            """

            def __init__(self, name: str, url: str, params: dict, data_manager: DataManager, signal: Signal):
                self.isRunning = False
                self.data_manager = data_manager
                self.signal = signal  # 信号
                self.params = params  # 请求参数
                self.url = url  # 下载路径
                # 数据发送线程
                self.signal_thread = Thread(target=self.__signal, daemon=True)
                # 以下为待发送数据
                self.name = name  # 任务名称
                self.state = TaskEnum.State.notrun
                self.data = None  # pd.DataFrame类型

            def __signal(self):
                """信号发送"""
                while True:
                    value = {
                        'name': self.name,
                        'state': self.state,
                        'data': self.data
                    }
                    if self.state in TaskEnum.State.finished:
                        self.signal.emit(value)
                        break
                    elif self.state == TaskEnum.State.running:
                        self.signal.emit(value)
                    time.sleep(0.2)

            def __execute(self):
                """任务执行函数"""
                response = request_api(self.url, self.params)
                if not response:
                    self.state = TaskEnum.State.error
                    return False
                response = response.json()
                meta = response['meta']
                results = response['data']
                if results == []:
                    self.state = TaskEnum.State.fail
                    return False
                # 处理搜索数据
                data = [[result['id'],  # id
                         self.name,  # 关键词
                         CATEGORY_DICT[result['category']],  # 类别
                         PURITY_DICT[result['purity']],  # 分类
                         int(result['file_size']),  # 大小
                         FILE_TYPE[result['file_type']],  # 扩张名
                         int(result['dimension_x']),  # 长
                         int(result['dimension_y']),  # 宽
                         float(result['ratio']),  # 比例
                         int(result['views']),  # 预览量
                         int(result['favorites']),  # 收藏量
                         result['path'],  # 远程路径
                         result['thumbs']["original"],  # 略缩图_原
                         result['thumbs']["large"],  # 略缩图_大
                         result['thumbs']["small"],  # 略缩图_小
                         pd.to_datetime(result['created_at']),  # 日期
                         int(meta['current_page']),  # 当前页码
                         int(meta['last_page']),  # 总页数
                         int(meta['total']),  # 总数
                         self.params['categories'],  # 类别码
                         self.params['purity'],  # 分级码
                         ] for result in results]
                self.data = pd.DataFrame(data, columns=SEARCH_COLUMNS)
                self.state = TaskEnum.State.success

            def stop(self):
                """停止任务"""
                self.isRunning = False

            def start(self):
                """开始任务"""
                self.isRunning = True
                self.state = TaskEnum.State.running
                self.signal_thread.start()
                with self.data_manager.SEARCH_INFO_LOCK:
                    result = self.data_manager.SEARCH_INFO[
                        self.data_manager.SEARCH_INFO['关键词'] == self.name
                        ].copy(deep=True)
                if result.empty:
                    self.__execute()
                    if self.state == TaskEnum.State.success:
                        self.data_manager.add_serach_info(self.data)
                else:
                    self.data = result
                    self.state = TaskEnum.State.success
                self.isRunning = False

        class Tags:
            """
            标签类任务
            发送的数据结构{'name','state','data'}
            """

            def __init__(self, name: str, url: str, data_manager: DataManager, signal: Signal):
                self.isRunning = False
                self.data_manager = data_manager
                self.signal = signal  # 信号
                self.url = url  # 下载路径
                # 数据发送线程
                self.signal_thread = Thread(target=self.__signal, daemon=True)
                # 以下为待发送数据
                self.name = name  # 任务名称
                self.state = TaskEnum.State.notrun
                self.data = None  # pd.DataFrame类型

            def __signal(self):
                """信号发送"""
                while True:
                    value = {
                        'name': self.name,
                        'state': self.state,
                        'data': self.data
                    }
                    if self.state in TaskEnum.State.finished:
                        self.signal.emit(value)
                        break
                    elif self.state == TaskEnum.State.running:
                        self.signal.emit(value)
                    time.sleep(0.2)

            def __execute(self):
                """任务执行函数"""
                response = request_api(self.url)
                if not response:
                    self.state = TaskEnum.State.error
                    return False
                result = response.json()['data']
                if not result:
                    self.state = TaskEnum.State.fail
                    return False
                data = [[result['id'],  # id
                         '',  # 关键词
                         CATEGORY_DICT[result['category']],  # 类别
                         PURITY_DICT[result['purity']],  # 分类
                         int(result['file_size']),  # 大小
                         FILE_TYPE[result['file_type']],  # 扩展名
                         int(result['dimension_x']),  # 长
                         int(result['dimension_y']),  # 宽
                         float(result['ratio']),  # 比例
                         int(result['views']),  # 预览量
                         int(result['favorites']),  # 收藏量
                         '',  # 本地路径
                         result['path'],  # 远程路径
                         result['thumbs']["original"],  # 略缩图_原
                         result['thumbs']["large"],  # 略缩图_大
                         result['thumbs']["small"],  # 略缩图_小
                         pd.to_datetime(result['created_at']),  # 日期
                         ';'.join([tag['name'] for tag in result['tags']])  # 文件的标签信息,  # 标签
                         ]]
                self.data = pd.DataFrame(data, columns=IMAGE_COLUMNS)
                self.state = TaskEnum.State.success

            def stop(self):
                """停止任务"""
                self.isRunning = False

            def start(self):
                """开始任务"""
                self.isRunning = True
                self.state = TaskEnum.State.running
                self.signal_thread.start()
                with self.data_manager.IMAGE_INFO_LOCK:
                    result = self.data_manager.IMAGE_INFO[
                        self.data_manager.IMAGE_INFO['id'] == self.name.split('_')[0]
                        ].copy(deep=True)
                if result.empty:  # 无缓存时发起网络请求
                    self.__execute()
                    if self.state == TaskEnum.State.success:
                        self.data_manager.add_image_info(self.data)
                else:
                    self.data = result
                    self.state = TaskEnum.State.success
                self.isRunning = False


class TaskWorker:
    """任务线程"""

    def __init__(self,
                 executor_download: ThreadPoolExecutor,
                 executor_json: ThreadPoolExecutor,
                 task_dict: ThreadSafe.Dict,
                 task: TaskEnum.Task.Download
                 ):
        """
        :param executor_download:下载池
        :param executor_json:json请求池
        :param data_manager:数据管理类
        :param task_dict:任务字典
        :param task:任务类
        """
        self.task_dict = task_dict
        self.task = task
        self.isRunning = False  # 是否正在运行
        self.task_enum = TaskEnum.Task
        self.state_enum = TaskEnum.State
        self.task_dict[task.name] = self
        if isinstance(task, self.task_enum.Download):
            self.future = executor_download.submit(self.start)  # 实际任务线程,提交任务
        else:
            self.future = executor_json.submit(self.start)

    def stop(self):
        # 线程未开始的情况下直接取消线程,开始了则取消任务
        if not self.future.running():
            self.future.cancel()
        else:
            self.task.stop()

    def start(self):
        """执行任务"""
        try:
            self.isRunning = True
            self.task.start()
            self.task_dict.pop(self.task.name)
        except Exception as e:
            print(f'子线程任务{self.task.name} -> 出错了\n\t{e}')
