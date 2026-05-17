"""工具类"""
from SubAPI.WallHaven.ImportPack import *

logger = LogClass.get_logger(__name__, console_level='WARNING')


def load_config():
    # 加载配置文件
    CONFIG_DATA.is_loaded(0)
    with CONFIG_DATA as data:
        value = data.get_values(section_name=Config.PACK_NAME)
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
    if GlobalValue.GLOBAL_ASYNC_HTTP_MANAGE is None:
        from SubAPI import global_value_init
        global_value_init()
    GlobalValue.GLOBAL_ASYNC_HTTP_MANAGE.set_proxies(f'http://{url}')
    return True


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
        self.image_thumb: BytesIO = None  # 略缩图
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

    def save_image(self, save_path: str = None, cover=False):
        """
        保存图像文件
        :param save_path: 保存路径,文件夹
        :param cover:是否覆盖,默认不覆盖
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
            raise FileNotFoundError(f'{self.__class__.__name__} {self.image_id} 保存路径获取失败!')

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
                    task = Task(func, GlobalValue.GLOBAL_Task_PROCESS_MANAGE, args=args)
                    self.image_thumb = task.start(0, 3, parent_task)
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
        self.response_task: AsyncJson | AsyncChunkDownloader = None  # 内部请求

    def get_search_data(self) -> pd.DataFrame | None:
        """获取搜索数据"""
        retry_count = 0
        if self.response_task is None:
            self.response_task = AsyncJson(
                self.url, GlobalValue.GLOBAL_ASYNC_HTTP_MANAGE,
                self.params, self.headers, retry_count=self.retry_count)
        while self.task.isRunning and retry_count < self.__class__.retry_count:
            data = self.response_task.start(0, 3, self.task)
            if data:
                break
            elif self.response_task.status_code == 429:
                logger.info(f'{self.task.name} 请求达到限制,正在重试...')
                time.sleep(3)
                continue
            else:
                return None
        if not data: return None
        meta = data['meta']
        results = data['data']
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

    def get_download_data(self, progress_signal: TaskSignal) -> BytesIO | None:
        """获取文件数据"""
        retry_count = 0
        if self.response_task is None:
            self.response_task = AsyncChunkDownloader(
                self.url, GlobalValue.GLOBAL_ASYNC_HTTP_MANAGE, num_chunks=1,
                params=self.params, headers=self.headers)
        self.response_task.progress_signal.connect(progress_signal.emit)
        while self.task.isRunning and retry_count < self.__class__.retry_count:
            if not GlobalValue.GLOBAL_ASYNC_HTTP_MANAGE.wait_for_rate_limit_sync(self.task):
                return None
            data = self.response_task.start(0, 3, self.task)
            if data is not None:
                return data
            elif self.response_task.status_code == 429:
                logger.info(f'{self.task.name} 请求达到限制,正在重试...')
                time.sleep(3)
                continue
            else:
                return None

    def get_image_info_data(self) -> pd.DataFrame | None:
        """获取图像信息数据"""
        retry_count = 0
        if self.response_task is None:
            self.response_task = AsyncJson(
                self.url, GlobalValue.GLOBAL_ASYNC_HTTP_MANAGE, self.params, self.headers)
        while self.task.isRunning and retry_count < self.__class__.retry_count:
            data = self.response_task.start(0, 3, self.task)
            if data: break
            if self.response_task.status_code == 429:
                logger.info(f'{self.task.name} 请求达到限制,正在重试...')
                time.sleep(3)
                continue
            else:
                return None
        if not data: return None
        result = data['data']
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
            return pd.DataFrame(data, columns=GlobalValue.search_columns).astype(GlobalValue.search_dtype)

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
            return pd.DataFrame(data, columns=GlobalValue.image_info_columns).astype(GlobalValue.image_info_dtype)

    def get_download_data(self, chunk_size):
        if self.result:
            return self.result.iter_content(chunk_size=chunk_size)


class SearchTask(Task):

    def __init__(self, params: Config.SearchParams, task_manage: TaskManageBase = None,
                 search_all=False, use_network: bool = True, use_cache: bool = True,
                 add_history: bool = False, enable_tags_search=False):
        """
        :param params:搜索参数
        :param task_manage:任务管理类,默认使用全局任务管理类
        :param search_all:是否搜索全部,默认只搜索单页
        :param use_network:是否使用网络,默认启用
        :param use_cache:是否使用缓存,默认启用
        :param add_history:是否添加到历史记录里
        :param enable_tags_search:启用标签搜索,默认为关键词检索
        """
        self.params = params
        self.task_manage = GlobalValue.GLOBAL_TASK_MANAGE if task_manage is None else task_manage
        self.search_all = search_all
        self.use_network = use_network
        self.use_cache = use_cache
        self.add_history = add_history
        self.enable_tags_search = enable_tags_search
        func = self.__execute_all if search_all else self.__execute
        name = 'search_all' if search_all else 'search'
        super().__init__(
            func=func, task_manage=task_manage,
            name=f'{params.q}_{params.page}_{name}')

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
            IMAGE_INFO.is_loaded(0)
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
                SEARCH_DATA.add_data(result)
                return result[result['当前页码'] == self.params.page].reset_index(drop=True)

    def __execute_all(self) -> pd.DataFrame | None:
        """搜索全部"""

        def sub_task_slot(task: 'SearchTask'):
            """搜索全部时的返回函数,用于计数"""
            self.progress.finished += 1
            self.progress_signal.emit(self)

        # 获取第一页数据
        self.params.page = 1
        result = self.__execute()
        if result is not None:
            self.progress.total = result.loc[0, '总页数']
            self.progress.finished = 1
            self.progress_signal.emit(self)
            self.sub_task: list[SearchTask] = []
            # 提交全部子任务
            for page in range(2, result.loc[0, '总页数'] + 1):
                self.params.page = page
                sub_task = SearchTask(self.params.copy(), self.task_manage, False, self.use_network, self.use_cache)
                sub_task.finish_signal.connect(sub_task_slot)
                sub_task.start()
                self.sub_task.append(sub_task)
            while self.progress.finished < self.progress.total: time.sleep(1)
            if self.isRunning:
                for task in self.sub_task:
                    data = task.result()
                    if data is not None:
                        result = pd.concat([result, data]).drop_duplicates(
                            subset=['id'], keep='last', ignore_index=True)
                    else:
                        logger.warning(f'失败的页码{task.params.page}')
                if self.use_network:
                    logger.info(f'{self.params.q} 全部搜索完成,'
                                f'服务器预计数据量为{result.loc[0, '总数']},'
                                f'实际数据量为{result.shape[0]}.')
                else:
                    logger.info(f'{self.params.q} 搜索完成,'
                                f'数据量为{result.shape[0]}.')
                return result

    def stop(self) -> bool:
        if hasattr(self, 'sub_task'):
            for task in self.sub_task:
                task.stop()
        return super().stop()

    def result(self, timeout: float | int = None, parent_task: 'Task' = None) -> pd.DataFrame | None:
        return super().result(timeout, parent_task)


class DownloadTask(Task):
    """
    下载任务,下载的图像数据将会存储在IMAGE_CACHE_DIR中
    返回ImageData类
    """

    def __init__(self, download_url: str, task_manage: TaskManageBase = None,
                 use_network: bool = True, use_cache: bool = True):
        """
        :param download_url:下载地址
        :param task_manage:任务管理类,默认使用全局任务管理
        :param use_network:是否使用网络,默认启用
        :param use_cache:是否使用缓存,默认启用
        """
        self.download_url = download_url
        self.use_network = use_network
        self.use_cache = use_cache
        self.task_manage = GlobalValue.GLOBAL_TASK_MANAGE if task_manage is None else task_manage
        self.image_id, self.file_type = os.path.basename(download_url).split('.')
        self.file_type = f'.{self.file_type}'
        self.desc = 'thumb'
        if self.image_id.find('-') != -1:
            self.image_id = self.image_id.split('-')[1]
            self.desc = 'image'
        super().__init__(
            func=self.__execute, task_manage=self.task_manage,
            name=f'{self.image_id}_download')

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
                data = AsyncAPI(self, self.download_url).get_download_data(self.progress_signal)
                if data is not None:
                    ImageLoad(data).save(image_data.cache_path)
                    if self.desc == 'thumb':
                        image_data.set_thumb(data)
                    return image_data
        except Exception as e:
            logger.exception(f'{self.__class__.__name__} {self.image_id} 下载错误:{e}')

    def result(self, timeout: float | int = None, parent_task: 'Task' = None) -> ImageData | None:
        return super().result(timeout, parent_task)


class ImageInfoTask(Task):
    def __init__(self, image_id: str, key_word: str, task_manage: TaskManageBase = None,
                 use_network: bool = True, use_cache: bool = True):
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
        self.task_manage = GlobalValue.GLOBAL_TASK_MANAGE if task_manage is None else task_manage
        super().__init__(self.__execute, self.task_manage, f'{image_id}_tags')

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

    def result(self, timeout: float | int = None, parent_task: 'Task' = None) -> pd.DataFrame | None:
        return super().result(timeout, parent_task)


class KeyWordTask(Task):
    def __init__(self, params: Config.SearchParams, task_manage: TaskManageBase = None,
                 use_network=True, use_cache=True):
        """
        :param params:搜索参数
        :param task_manage:任务管理类
        :param use_network:是否使用网络,默认启用
        :param use_cache:是否使用缓存,默认启用
        """
        self.params = params.copy()
        self.params.page = 1
        self.task_manage = task_manage
        self.use_network = use_network
        self.use_cache = use_cache
        self.task_manage = GlobalValue.GLOBAL_TASK_MANAGE if task_manage is None else task_manage
        super().__init__(self.__execute, self.task_manage, f'{params.q}_addKey')

    def __execute(self) -> pd.DataFrame | None:
        """具体的任务函数"""
        search_task = SearchTask(self.params, self.task_manage, use_network=self.use_network, use_cache=self.use_cache)
        result: pd.DataFrame = search_task.start(0, 3, self)
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

    def result(self, timeout: float | int = None, parent_task: 'Task' = None) -> pd.DataFrame | None:
        return super().result(timeout, parent_task)


if __name__ == '__main__':
    # 单元测试
    params_test = get_search_params()
    params_test.q = 'Abaoyeshitunia'
    params_test.purity = '111'
    params_test.categories = '001'
    task_test = DownloadTask('https://w.wallhaven.cc/full/qr/wallhaven-qrgl87.jpg')
    result_test = task_test.start(0)
    print(result_test)
    if isinstance(result_test, ImageData):
        print(f'当前文件路径: {result_test.image_path}')
        image_load = ImageLoad(result_test.image_path)
        image_load.show()
