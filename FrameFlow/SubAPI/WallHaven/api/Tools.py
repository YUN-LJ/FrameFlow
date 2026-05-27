"""WallHaven工具类"""
import pandas as pd

from SubAPI.WallHaven.ImportPack import *

logger = LogClass.get_logger(__name__, console_level='WARNING')


def load_config(config_data: dict = None):
    # 加载配置文件
    if config_data is None:
        if not CONFIG_DATA.is_loaded(5):
            logger.warning(f'{Config.PACK_NAME} 本地配置加载失败')
            return
        with CONFIG_DATA as data:
            value = data.get_values(section_name=Config.PACK_NAME).copy()
    else:
        value = config_data
    if value:
        Config.SAVE_DIR = value.get('save_dir', File.get_user_PicturesPath())
        Config.USE_NETWORK = value.get('use_network', Config.USE_NETWORK)
        Config.SearchParams.default_params['categories'] = value.get(
            'categories', Config.SearchParams.default_params['categories'])
        Config.SearchParams.default_params['purity'] = value.get(
            'purity', Config.SearchParams.default_params['purity'])
        Config.SearchParams.default_params['sorting'] = value.get(
            'sorting', Config.SearchParams.default_params['sorting'])
        Config.SearchParams.default_params['order'] = value.get(
            'order', Config.SearchParams.default_params['order'])
        Config.USE_TAGS = value.get('use_tags', Config.USE_TAGS)
        set_api_key(value.get('api_key', Config.API_KEY), False)
        set_proxies_url(value.get('proxies_url', Config.PROXIES_URL), False)
        Config.SEARCH_HISTORY = value.get('search_history', Config.SEARCH_HISTORY)
        Config.SEARCH_HISTORY_COUNT = value.get('search_history_count', Config.SEARCH_HISTORY_COUNT)


def save_config():
    data = get_search_params()
    data = data.to_dict()
    data.update({'save_dir': Config.SAVE_DIR,
                 'api_key': Config.API_KEY,
                 'search_history': Config.SEARCH_HISTORY,
                 'search_history_count': Config.SEARCH_HISTORY_COUNT,
                 'use_network': Config.USE_NETWORK,
                 'proxies_url': Config.PROXIES_URL,
                 'use_tags': Config.USE_TAGS
                 })
    del data['q'], data['page']
    CONFIG_DATA.data.add_values(data, Config.PACK_NAME)


def set_purity(purity):
    Config.SearchParams.default_params['purity'] = purity


def set_category(category):
    Config.SearchParams.default_params['categories'] = category


def add_search_history(key_word: str):
    """添加搜索搜索历史"""
    if len(Config.SEARCH_HISTORY) > Config.SEARCH_HISTORY_COUNT:
        del Config.SEARCH_HISTORY[-1]
    if key_word in Config.SEARCH_HISTORY:
        Config.SEARCH_HISTORY.remove(key_word)
    Config.SEARCH_HISTORY.insert(0, key_word)


def set_search_history_count(count):
    """设置搜索历史数量"""
    Config.SEARCH_HISTORY_COUNT = count
    Config.SEARCH_HISTORY = Config.SEARCH_HISTORY[:Config.SEARCH_HISTORY_COUNT]


def set_save_dir(save_dir):
    """设置保存目录"""
    Config.SAVE_DIR = save_dir


def set_api_key(api_key, check=True) -> bool:
    """设置API密钥,如192.168.42.129:8080"""
    if check:
        if not check_api(api_key):
            return False
    Config.API_KEY = api_key
    Config.HEADERS = {"X-API-Key": api_key}
    return True


def set_proxies_url(url, check=True) -> bool:
    if not url:
        Config.PROXIES_URL = url
        GlobalValue.GLOBAL_ASYNC_HTTP_MANAGE.set_proxies(None)
        return True
    if check:
        if not check_connect(url):
            return False
    Config.PROXIES_URL = url
    Config.PROXIES = {'http': f'http://{url}', 'https': f'http://{url}'}
    if GlobalValue.GLOBAL_ASYNC_HTTP_MANAGE is not None:
        GlobalValue.GLOBAL_ASYNC_HTTP_MANAGE.set_proxies(f'http://{url}')
        return True
    else:
        logger.warning(f'set_proxies_url 警告:线程池未初始化')
        return False


def check_connect(proxy=None) -> bool:
    """
    检查网络是否可连接
    :param proxy:代理服务器
    """
    header = Config.HEADERS if Config.API_KEY else None
    kwargs = {'headers': header, 'timeout': (3, 10)}
    proxy = kwargs.update({'proxies': {'http': f'http://{proxy}', 'https': f'http://{proxy}'}}) if proxy else None
    try:
        response = requests.get(Config.CONNECT_TEST_URL, **kwargs)
        if response.status_code == 200:
            return True
    except Exception:
        pass
    return False


def check_api(api) -> bool:
    """检查API是否可用"""
    header = {"X-API-Key": api} if api else None
    if header is None:
        return False
    kwargs = {'headers': header, 'timeout': (3, 10)}
    proxy = kwargs.update({'proxies': Config.PROXIES}) if Config.PROXIES_URL else None
    try:
        response = requests.get(Config.API_KEY_TEST_URL, **kwargs)
        if response.status_code == 200:
            return True
    except Exception as e:
        pass
    return False


def get_search_params() -> Config.SearchParams:
    """获取搜索参数模板"""
    return Config.SearchParams()


def get_search_history() -> list[str]:
    """获取搜索历史数据"""
    return Config.SEARCH_HISTORY.copy()


def _transformation_search_data(data: dict, params: dict) -> pd.DataFrame | None:
    """将搜索数据转为pd.DataFrame格式"""
    meta = data['meta']  # 元数据信息
    results = data['data']  # 搜索结果
    if results:
        # 处理搜索数据
        data = [[result['id'],  # id
                 params['q'],  # 关键词
                 Config.CATEGORY_DICT[result['category']],  # 分类
                 Config.PURITY_DICT[result['purity']],  # 分级
                 int(result['file_size']),  # 大小
                 Config.TYPE_DICT[result['file_type']],  # 扩张名
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
                 params['categories'],  # 类别码
                 params['purity'],  # 分级码
                 ] for result in results]
        return pd.DataFrame(data, columns=DataConfig.search_columns).astype(DataConfig.search_dtype)


def _transformation_image_info_data(data: dict) -> pd.DataFrame | None:
    """将图像数据转为pd.DataFrame格式"""
    result = data['data']
    if result:
        data = [[result['id'],  # id
                 '',  # 关键词
                 Config.CATEGORY_DICT[result['category']],  # 类别
                 Config.PURITY_DICT[result['purity']],  # 分类
                 int(result['file_size']),  # 大小
                 Config.TYPE_DICT[result['file_type']],  # 扩展名
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
        return pd.DataFrame(data, columns=DataConfig.image_info_columns).astype(DataConfig.image_info_dtype)


class ImageData(ImageDataBase):
    """
    图像数据
    image_id 为图像名（不含扩展名）
    略缩图为thumb+图像名
    数据来源：本地加载，网络下载（临时存放在image_cache_dir目录中）
    需要保存的图像必须已经下载过图像数据，否则会报错
    """

    def __init__(self, image_id: str, extension: str, is_thumb=False):
        super().__init__(image_id)
        self.is_thumb = is_thumb
        self.image_thumb: Optional[BytesIO] = None  # 略缩图
        self.extension = extension
        self.cache_path = FileBase(GlobalValue.IMAGE_CACHE_DIR).join(self.image_name).path

    @property
    def image_name(self) -> str:
        if self.is_thumb:
            return f'thumb_{self.image_id}{self.extension}'
        else:
            return self.image_id + self.extension

    @property
    def image_path(self) -> str:
        """
        获取本地路径，本地存在时返回不为空字符串
        """
        if FileBase(self.cache_path).exists:
            return self.cache_path
        IMAGE_INFO.is_loaded(0)
        with IMAGE_INFO as df:
            data = df.loc[df['id'] == self.image_id, '本地路径']
            if not data.empty:
                image_path = FileBase(data.values[0])
                if image_path.exists and image_path.is_file:
                    return image_path.path
        return ''

    @property
    def save_path(self) -> str:
        """获取保存路径,根据图像的分级和分类生成保存路径"""
        image_info = self.image_info
        if image_info is not None:
            image_dir = Path(Config.SAVE_DIR) / image_info['分级'].values[0] / image_info['类别'].values[0]
            image_dir.mkdir(parents=True, exist_ok=True)
            image_path = image_dir / f'{image_info['id'].values[0]}{image_info['文件扩展名'].values[0]}'
            return str(image_path)
        return ''

    @property
    def image_info(self) -> pd.DataFrame | None:
        """从本地数据内获取图像详细信息"""
        if IMAGE_INFO.data is not None:
            with IMAGE_INFO as df:
                data = df[df['id'] == self.image_id].copy(deep=True)
                if not data.empty:
                    return data
        return None

    def load_image(self):
        """图像加载方法"""
        image_path = self.image_path
        if image_path:
            return image_path
        raise FileNotFoundError(f'{self.__class__.__name__} {self.image_id} 图像不存在!')

    def del_image(self):
        """删除本地文件"""
        image_path = self.image_path
        if image_path:
            IMAGE_INFO.del_row(self.image_id)
            FileBase(image_path).delete()

    def save_image(self, save_path: str = None, cover=False) -> bool:
        """
        保存图像文件
        :param save_path: 保存路径,文件夹
        :param cover:是否覆盖,默认不覆盖
        :return 是否保存成功
        """
        if save_path is None:
            image_path = self.save_path
        else:
            FileBase(save_path).ensure_exists()
            save_path = os.path.realpath(save_path)
            image_info = self.image_info
            if image_info is None:
                raise ValueError(f'{self.__class__.__name__} {self.image_id} 图像信息不存在!')
            image_path = str(Path(save_path) / image_info['分级'].values[0] / image_info['类别'].values[0] /
                             f'{image_info['id'].values[0]}{image_info['文件扩展名'].values[0]}')
        if image_path:
            # 写入图像信息
            with IMAGE_INFO as df:
                df.loc[df['id'] == self.image_id, '本地路径'] = image_path
            if cover or not FileBase(image_path).exists:
                cache_path = FileBase(self.cache_path)
                if cache_path.exists:  # 将缓存文件移动至保存路径下
                    cache_path.move(image_path, True)
                else:
                    self.image.save(image_path)
            else:
                logger.warning(f'{self.__class__.__name__} {self.image_id} 文件已存在!')
            return True
        else:
            logger.warning(f'{self.__class__.__name__} {self.image_id} 保存路径获取失败!')
            return False

    def copy_to_clipboard(self) -> bool:
        """将图片复制到剪切板中"""
        image_path = self.image_path
        if image_path:
            FileBase(image_path).copy_to_clipboard()
            return True
        return False

    def set_thumb(self, thumb: BytesIO | str):
        if isinstance(thumb, BytesIO):
            self.image_thumb = thumb
        elif isinstance(thumb, str):
            self.image_thumb = ImageLoad(thumb).get_bytesIO()

    def generate_thumb(self, parent_task: Task = None) -> BytesIO | None:
        """
        生成图像略缩图
        :param parent_task:父任务,生成略缩图时阻塞生成,使用父任务用于及时终止
        """
        if self.image_thumb is None:
            image_path = self.image_path
            if image_path:
                # 检查缓存略缩图是否存在,图像加载轻量
                if FileBase(self.cache_path).exists:
                    func = GlobalValue.load_file
                    args = (image_path,)
                else:
                    func = GlobalValue.generate_thumb
                    args = (image_path, self.extension)
                # 等待任务池空闲,图像缩放重型任务
                if GlobalValue.GLOBAL_Task_PROCESS_MANAGE.wait_idle(parent_task):
                    task = Task(func, GlobalValue.GLOBAL_Task_PROCESS_MANAGE, args=args, parent_task=parent_task)
                    self.image_thumb = task.start(0, 3)
            else:
                raise FileNotFoundError(f'{self.__class__.__name__} {self.image_id} 图像不存在!')
        return self.image_thumb


class AsyncAPI:
    """
    异步请求API,
    一个实例在使用了get发放后内部的请求任务则会被固定
    即response_task每个实例只创建一次
    """
    retry_count = 3  # 最大重试次数,连接达到限制不计入重试次数,AsyncHTTPManage支持速率首先,一般不会触发重试

    def __init__(self, task: Task, url: str, params: dict = None):
        self.task = task
        self.url = url
        self.params = params
        self.headers = Config.HEADERS if Config.API_KEY else None
        self.response_task: Union[AsyncJson, AsyncChunkDownloader, None] = None  # 内部请求

    def _create_async_json(self, retry_should=None):
        self.response_task = AsyncJson(
            self.url, GlobalValue.GLOBAL_ASYNC_HTTP_MANAGE,
            self.params, self.headers)
        self.response_task.set_parent_task(self.task)  # 设置父任务
        self.response_task.set_retry_count(self.retry_count)  # 设置重试次数
        if retry_should is not None:
            self.response_task.set_retry_should(retry_should)  # 设置重试条件

    def _create_async_download(self, num_chunks=None, retry_should=None):
        num_chunks = num_chunks or 1
        self.response_task = AsyncChunkDownloader(
            self.url, GlobalValue.GLOBAL_ASYNC_HTTP_MANAGE,
            num_chunks=num_chunks, params=self.params,
            headers=self.headers, enable_limit=False)
        self.response_task.set_parent_task(self.task)  # 设置父任务
        self.response_task.set_retry_count(self.retry_count)  # 设置重试次数
        if retry_should is not None:
            self.response_task.set_retry_should(retry_should)  # 设置重试条件

    def _retry_should(self, result):
        if self.response_task.status_code == 429:
            logger.info(f'{self.task.name} 请求达到限制,正在重试...')
            return False
        elif result is None:
            logger.info(f'{self.task.name} 获取数据失败,正在重试...')
            return False
        else:
            return True

    def _start_async_json(self) -> dict | None:
        # 创建任务
        if self.response_task is None:
            self._create_async_json(self._retry_should)

        # 执行任务
        if not GlobalValue.GLOBAL_ASYNC_HTTP_MANAGE.wait_for_rate_limit_sync(self.task):
            return None
        data: Optional[dict] = self.response_task.start(
            timeout=0, priority=3)
        self.response_task.clear()
        return data

    def get_search_data(self) -> pd.DataFrame | None:
        """获取搜索数据"""
        data = self._start_async_json()
        # 处理任务结果
        if data:
            return _transformation_search_data(data, self.params)

    def get_download_data(self, progress_callback: Callable) -> BytesIO | None:
        """获取文件数据"""
        if self.response_task is None:
            self._create_async_download(retry_should=self._retry_should)

        self.response_task.signal.progress_signal.connect(progress_callback)

        if not GlobalValue.GLOBAL_ASYNC_HTTP_MANAGE.wait_for_rate_limit_sync(self.task):
            return None
        data: Optional[BytesIO] = self.response_task.start(
            timeout=0, priority=3)
        if data is not None:
            return data

    def get_image_info_data(self) -> pd.DataFrame | None:
        """获取图像信息数据"""
        data = self._start_async_json()

        if data is not None:
            return _transformation_image_info_data(data)


class RequestAPI:
    """请求类"""

    Timeout = (3, 10)  # 超时时间
    Retry = 3  # 重试次数
    Sleep_Time = 1  # 等待时间

    def __init__(self, task: Task, url: str, params: dict = None):
        self.task = task
        self.url = url
        self.params = params
        self.state_code = None
        self.result = self.request_api(
            url, params, self.__class__.Timeout, self.__class__.Retry
        )

    def request_api(self, url, params=None, timeout=(3, 10), retry=3) -> bool | requests.Response:
        """
        请求API结果
        :param url:请求链接
        :param params:参数
        :param timeout:设置超时(连接超时,读取超时)
        :param retry:重试次数
        :return 如果请求成功则返回requests.Response,否则返回Flase
        """
        header = Config.HEADERS if Config.API_KEY else None
        kwargs = {
            'params': params,  # 请求参数
            'headers': header,  # 头文件
            'timeout': (3, 10),  # 超时
        }
        if Config.PROXIES_URL:
            kwargs.update({'proxies': Config.PROXIES})  # 代理
        for _ in range(retry):
            while self.task.isRunning:
                try:
                    # verify=False,  # 忽略SSL证书验证
                    response = requests.get(url, stream=True,  # 允许流式获取
                                            **kwargs)
                except Exception:
                    logger.warning(f'连接超时{self.task.name},正在重试...')
                    time.sleep(self.__class__.Sleep_Time)
                    break
                self.status_code = response.status_code
                if self.status_code == 200:  # 正常状态
                    return response
                elif self.status_code == 429:  # 请求达到限制
                    time.sleep(self.__class__.Sleep_Time)
                    continue

    def get_search_data(self) -> pd.DataFrame | None:
        """获取搜索结果"""
        if self.result:
            response = self.result.json()
            meta = response['meta']
            results = response['data']
            if not results: return None
            # 处理搜索数据
            data = [[result['id'],  # id
                     self.params['q'],  # 关键词
                     Config.CATEGORY_DICT[result['category']],  # 分类
                     Config.PURITY_DICT[result['purity']],  # 分级
                     int(result['file_size']),  # 大小
                     Config.TYPE_DICT[result['file_type']],  # 扩张名
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
            return pd.DataFrame(data, columns=DataConfig.search_columns).astype(DataConfig.search_dtype)

    def get_tags_data(self) -> pd.DataFrame | None:
        """获取标签结果"""
        if self.result:
            result = self.result.json()['data']
            if not result: return None
            data = [[result['id'],  # id
                     '',  # 关键词
                     Config.CATEGORY_DICT[result['category']],  # 类别
                     Config.PURITY_DICT[result['purity']],  # 分类
                     int(result['file_size']),  # 大小
                     Config.TYPE_DICT[result['file_type']],  # 扩展名
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
            return pd.DataFrame(data, columns=DataConfig.image_info_columns).astype(DataConfig.image_info_dtype)

    def get_download_data(self, chunk_size):
        if self.result:
            return self.result.iter_content(chunk_size=chunk_size)


class TaskBase(Task):
    """WallHaven后端任务基类,全局任务器满载时可选是否提交到内部线程池"""

    def start(self, timeout: float | int = None, priority: int = 5,
              parent_task: Task = None, submit_to_internal=False) -> Any | bool:
        if submit_to_internal and self.manage.is_full:
            task_manage = self.manage.__class__
            self.set_manage(task_manage(GeneralConfig.INTERNAL_NUM_WORK), True)
        return super().start(timeout, priority, parent_task)

    async def start_async(self, timeout: float | int = None, priority: int = 5,
                          parent_task: Task = None, submit_to_internal=False) -> Any | bool:
        if submit_to_internal and self.manage.is_full:
            task_manage = self.manage.__class__
            self.set_manage(task_manage(GeneralConfig.INTERNAL_NUM_WORK), True)
        return await super().start_async(timeout, priority, parent_task)


class SearchTask(TaskBase):

    def __init__(self,
                 search_params: Config.SearchParams,
                 task_manage: TaskManageBase = None,
                 search_all=False,
                 use_network: bool = True,
                 use_cache: bool = True,
                 add_history: bool = False,
                 enable_tags_search=False):
        """
        搜索全部时,如果传入的任务池满载了则会创建一个临时的任务池用于完成子任务

        Args:
            search_params: 搜索参数字典
            task_manage: 任务管理实例，为 None 时使用全局实例
            search_all: 是否搜索全部页面，False 时仅搜索第一页
            use_network: 是否发起网络请求
            use_cache: 是否读取/写入缓存
            add_history: 是否将本次搜索加入历史记录
            enable_tags_search: 是否启用标签模式，False 时为关键词检索

        Returns:
            有结果 pd.DataFrame
            无结果 None
        """
        self.params = search_params.copy()
        self.search_all = search_all
        self.use_network = use_network
        self.use_cache = use_cache
        self.add_history = add_history
        self.enable_tags_search = enable_tags_search
        task_manage = task_manage or GlobalValue.GLOBAL_TASK_MANAGE
        func = self.__execute_all if self.search_all else self.__execute
        name = f'{hex(id(self))}_{self.__class__.__name__}_all' if self.search_all else f'{hex(id(self))}_{self.__class__.__name__}'
        super().__init__(func, task_manage, name)

    def __execute(self) -> pd.DataFrame | None:
        """具体的任务函数"""
        if self.add_history:
            add_search_history(self.params.q)
        if self.use_cache:
            SEARCH_DATA.is_loaded(0)
            with SEARCH_DATA as df:
                result = df.loc[
                    (df['关键词'] == self.params.q) &
                    (df['当前页码'] == self.params.page) &
                    (df['类别码'] == self.params.categories) &
                    (df['分级码'] == self.params.purity)
                    ].copy(deep=True).reset_index(drop=True)
            if not result.empty: return result
        if self.use_network:  # 联网搜索
            data = AsyncAPI(self, Config.SEARCH_URL, self.params.to_dict()).get_search_data()
            if data is not None:
                SEARCH_DATA.add_data(data)
                return data
        else:  # 本地搜索
            result = self.__search_local()
            if result is not None:
                return result[result['当前页码'] == self.params.page].reset_index(drop=True)

    def __execute_all(self) -> pd.DataFrame | None:
        """搜索全部"""
        if not self.use_network:
            result = self.__search_local()
            if result is not None:
                logger.info(f'{self.params.q} 搜索完成,数据量为{result.shape[0]}.')
            return result

        def sub_task_slot():
            """搜索全部时的返回函数,用于计数"""
            self.progress.finished += 1
            self.progress_signal.emit(self)

        # 获取第一页数据
        self.params.page = 1
        result = self.__execute()
        if result is not None:
            # 设置进度
            self.progress.total = int(result.loc[0, '总页数'])
            self.progress.finished = 1
            self.progress_signal.emit(self)
            # 提交全部子任务
            all_sub_task: list[SearchTask] = []
            for page in range(2, result.loc[0, '总页数'] + 1):
                self.params.page = page
                sub_task = SearchTask(
                    self.params, self.manage, search_all=False, use_network=self.use_network,
                    use_cache=self.use_cache, add_history=False, enable_tags_search=self.enable_tags_search)
                sub_task.finish_signal.connect(sub_task_slot)
                self.add_sub_task(sub_task)
                sub_task.start(priority=2)
                all_sub_task.append(sub_task)
            # 等待子任务完成
            while self.progress.finished < self.progress.total: time.sleep(0.1)
            if self.isRunning:
                for task in all_sub_task:
                    data = task.result()
                    if data is not None:
                        result = pd.concat([result, data]).drop_duplicates(
                            subset=['id'], keep='last', ignore_index=True)
                    else:
                        logger.warning(f'搜索失败的页码{task.params.page}')
                    task.clear()
                if self.use_network:
                    logger.info(f'{self.params.q} 全部搜索完成,'
                                f'服务器预计数据量为{result.loc[0, '总数']},'
                                f'实际数据量为{result.shape[0]}.')
                else:
                    logger.info(f'{self.params.q} 搜索完成,数据量为{result.shape[0]}.')
                return result

    def __search_local(self) -> pd.DataFrame | None:
        """本地搜索函数"""
        if not IMAGE_INFO.is_loaded(5):
            return None
        purity_list = list(Config.PURITY_DICT.values())
        purity = [
            purity_list[index]
            for index, checked in enumerate(self.params.purity)
            if checked == '1']
        categories_list = list(Config.CATEGORY_DICT.values())
        categories = [
            categories_list[index]
            for index, checked in enumerate(self.params.categories)
            if checked == '1']
        # 创建空白pandas表
        with IMAGE_INFO as df:  # 筛选出本地符合搜索参数的数据
            # 筛选包含关键词的图像信息,case是否区分大小写
            col_name = Config.LOCAL_SEARCH_MODE_TAGS if self.enable_tags_search else Config.LOCAL_SEARCH_MODE_KEY
            case = False if self.enable_tags_search else True
            mask_key = df[col_name].str.contains(self.params.q, case=case, na=False, regex=False)
            mask_purity = df['分级'].isin(purity)
            mask_categories = df['类别'].isin(categories)
            mask_local = df['本地路径'] != ''
            result = df[mask_key & mask_purity & mask_categories & mask_local].copy(deep=True)
        if not result.empty:
            result.drop(['标签', '本地路径'], axis=1, inplace=True)  # 删除多余列
            result.sort_values('日期', ascending=False, inplace=True)  # 按日期排序
            result.reindex(columns=DataConfig.search_columns).astype(DataConfig.search_dtype)
            total_page = int(result.shape[0] / 24) if result.shape[0] % 24 == 0 else int(result.shape[0] / 24) + 1
            result['关键词'] = self.params.q
            result['总页数'] = total_page
            result['总数'] = result.shape[0]
            result['类别码'] = self.params.categories
            result['分级码'] = self.params.purity
            result['当前页码'] = 1
            for page in range(1, total_page + 1):
                result.iloc[(page - 1) * 24:page * 24, result.columns.get_loc('当前页码')] = page
            result.reset_index(drop=True, inplace=True)
            SEARCH_DATA.add_data(result)
            return result


class DownloadTask(TaskBase):
    """
    下载任务,下载的图像数据将会存储在IMAGE_CACHE_DIR中
    返回ImageData类
    """

    def __init__(self,
                 download_url: str,
                 task_manage: TaskManageBase = None,
                 use_network: bool = True,
                 use_cache: bool = True):
        """
        :param download_url:下载地址
        :param task_manage:任务管理类,默认使用全局任务管理
        :param use_network:是否使用网络,默认启用
        :param use_cache:是否使用缓存,默认启用
        """
        self.download_url = download_url
        self.use_network = use_network
        self.use_cache = use_cache
        self.image_id, self.file_type = os.path.basename(download_url).split('.')
        self.file_type = f'.{self.file_type}'
        self.desc = 'thumb'
        if self.image_id.find('-') != -1:
            self.image_id = self.image_id.split('-')[1]
            self.desc = 'image'
        task_manage = task_manage or GlobalValue.GLOBAL_TASK_MANAGE
        super().__init__(self.__execute, task_manage, f'{hex(id(self))}_{self.__class__.__name__}')

    def __execute(self) -> ImageData | None:
        """返回ImageData类型数据"""
        try:
            image_data = ImageData(self.image_id, self.file_type, self.desc == 'thumb')
            # 如果本地有数据则会从本地加载,否则返回None
            if image_data.image_path:
                if self.desc == 'thumb':  # 请求的时略缩图的话提前生成略缩图
                    thumb = image_data.generate_thumb(self)
                    if thumb is None:
                        return None
                    ImageLoad(thumb).save(image_data.cache_path)
                return image_data
            if self.use_network:  # 不存在时发送网络请求
                data = AsyncAPI(self, self.download_url).get_download_data(self.progress_emit)
                if data is not None:
                    ImageLoad(data).save(image_data.cache_path)
                    if self.desc == 'thumb':
                        image_data.set_thumb(data)
                    return image_data
        except Exception as e:
            logger.exception(f'{self.__class__.__name__} {self.image_id} 下载错误:{e}')

    def result(self, timeout: float | int = None) -> ImageData | None:
        return super().result(timeout)


class ImageInfoTask(TaskBase):
    def __init__(self,
                 image_id: str,
                 key_word: str,
                 task_manage: TaskManageBase = None,
                 use_network: bool = True,
                 use_cache: bool = True):
        """
        :param image_id:图像id
        :param key_word:所属关键词
        :param task_manage:任务管理类,默认使用全局任务类
        :param use_network:是否使用网络,默认启用
        :param use_cache:是否使用缓存,默认启用
        """
        self.image_id = image_id
        self.key_word = key_word
        self.use_network = use_network
        self.use_cache = use_cache
        task_manage = GlobalValue.GLOBAL_TASK_MANAGE if task_manage is None else task_manage
        super().__init__(self.__execute, task_manage, f'{image_id}_tags')

    def __execute(self) -> pd.DataFrame | None:
        """具体的任务函数"""
        IMAGE_INFO.is_loaded(0)
        with IMAGE_INFO as df:
            mask = df['id'] == self.image_id
            # 添加所属关键词
            if df.loc[mask, '关键词'].str.contains(self.key_word, case=True, na=False, regex=False).any():
                df.loc[mask, '关键词'] += f';{self.key_word}'
            data = df.loc[mask].copy(deep=True).reset_index(drop=True)
        if not data.empty: return data
        if self.use_network:
            data = AsyncAPI(self, f'{Config.IMAGE_INFO_URL}/{self.image_id}').get_image_info_data()
            if data is not None:
                data.loc[0, '关键词'] = self.key_word
                IMAGE_INFO.add_data(data)
                return data

    def result(self, timeout: float | int = None) -> pd.DataFrame | None:
        result: Optional[pd.DataFrame] = super().result(timeout)
        return result


class KeyWordTask(TaskBase):
    def __init__(self,
                 params: Config.SearchParams,
                 task_manage: TaskAsyncManage = None,
                 use_network=True,
                 use_cache=True):
        """
        :param params:搜索参数
        :param task_manage:任务管理类
        :param use_network:是否使用网络,默认启用
        :param use_cache:是否使用缓存,默认启用
        """
        self.params = params.copy()
        self.params.page = 1
        self.use_network = use_network
        self.use_cache = use_cache
        task_manage = GlobalValue.GLOBAL_TASK_ASYNC_MANAGE if task_manage is None else task_manage
        super().__init__(self.__execute, task_manage, f'{params.q}_addKey', use_async=True)

    async def __execute(self) -> pd.DataFrame | None:
        """具体的任务函数"""
        with SearchTask(self.params, use_network=self.use_network,
                        use_cache=self.use_cache) as search_task:
            search_task.set_parent_task(self)
            result: Optional[pd.DataFrame] = await search_task.start_async(0, 3)
        if result is not None:
            key_data = pd.DataFrame(
                [[
                    self.params.q,
                    result.loc[0, '总页数'],
                    result.loc[0, '总数'],
                    result.loc[0, '日期'],
                    pd.to_datetime(Time.now_time("%Y-%m-%d %H:%M:%S")),
                    self.params.categories,
                    self.params.purity
                ]], columns=DataConfig.key_word_columns
            ).astype(DataConfig.key_word_dtype)
            KEY_WORD.add_data(key_data)
            return key_data

    def result(self, timeout: float | int = None) -> pd.DataFrame | None:
        result: Optional[pd.DataFrame] = super().result(timeout)
        return result
