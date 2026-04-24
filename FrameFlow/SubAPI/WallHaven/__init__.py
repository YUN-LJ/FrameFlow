"""
wallhavenAPI集成
面向对象编程方式
"""
from SubAPI.WallHaven.ImportPack import *
from SubAPI.WallHaven import Config
from SubAPI.WallHaven.Tools import *


def load_config():
    # 加载配置文件
    while not ConfigData.is_loaded(): time.sleep(0.1)
    with ConfigData.lock:
        value = ConfigData.data().get_values(section_name=Config.PACK_NAME)
        if value:
            Config.THREAD_NUM = value.get('num_work', Config.THREAD_NUM)
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
        return True
    if check:
        if not check_connect(url):
            return False
    Config.PROXIES_URL = url
    Config.PROXIES = {'http': f'http://{url}', 'https': f'http://{url}'}
    AsyncAPI.set_proxies(f'http://{url}')
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


def save_config(purity, categories):
    data = get_search_params()
    data.purity = purity
    data.categories = categories
    data = data.to_dict()
    data.update({'save_dir': Config.SAVE_DIR,
                 'num_work': Config.THREAD_NUM,
                 'api_key': Config.API_KEY,
                 'search_history': Config.SEARCH_HISTORY,
                 'SEARCH_HISTORY_COUNT': Config.SEARCH_HISTORY_COUNT,
                 'use_network': Config.USE_NETWORK,
                 'proxies_url': Config.PROXIES_URL,
                 'use_tags': Config.USE_TAGS
                 })
    del data['q'], data['page']
    ConfigData.data().add_values(data, Config.PACK_NAME)


def del_image_file(image_id: list) -> Task | None:
    """删除图像及其图像信息"""

    def sub_func():
        nonlocal task, del_info, mask
        try:
            for index, row in del_info.iterrows():
                FileBase(row['本地路径']).delete()
                task.progress.finished += 1
                task.progress_signal.emit(task.progress)
            with ImageInfo.lock:
                ImageInfo.del_data(~mask, use_lock=False)
            return True
        except Exception as e:
            return False

    with ImageInfo.lock:
        mask = ImageInfo.data()['id'].isin(image_id)
        del_info = ImageInfo.data()[mask].copy().reset_index(drop=True)
    task = Task(sub_func, WallHavenAPI.get_thread_pool_thumb())
    task.progress.total = del_info.shape[0]
    return task


class WallHavenAPI:
    """API接口,单例模式,所有任务共享同一批线程池"""
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.__thread_pool_json = TaskManage(Config.THREAD_NUM)
        self.__thread_pool_file = TaskManage(Config.THREAD_NUM)
        self.__thread_pool_thumb = TaskManage(Config.THREAD_NUM)

    @classmethod
    def get_thread_pool_json(cls) -> Task:
        return cls().__thread_pool_json

    @classmethod
    def get_thread_pool_file(cls) -> Task:
        return cls().__thread_pool_file

    @classmethod
    def get_thread_pool_thumb(cls) -> Task:
        return cls().__thread_pool_thumb

    @classmethod
    def set_thread_num(cls, num):
        self = cls()
        Config.THREAD_NUM = num
        self.__thread_pool_json.set_thread_num(num)
        self.__thread_pool_file.set_thread_num(num)
        self.__thread_pool_thumb.set_thread_num(num)

    @classmethod
    def search_task(cls, params: Config.SearchParams, search_all=False,
                    use_network: bool = True, use_cache: bool = True,
                    add_history: bool = False, use_tags=False) -> SearchTask:
        """
        :param params:搜索参数
        :param search_all:搜索全部
        :param use_network:是否使用网络,默认启用
        :param use_cache:是否使用缓存,默认启用
        :param add_history:是否添加到历史记录中,默认不添加
        """
        return SearchTask(params, cls().__thread_pool_json, search_all, use_network, use_cache, add_history, use_tags)

    @classmethod
    def key_word_task(cls, params: Config.SearchParams, use_network: bool = True, use_cache: bool = True) -> SearchTask:
        """
        :param params:搜索参数
        :param use_network:是否使用网络,默认启用
        :param use_cache:是否使用缓存,默认启用
        """
        return KeyWordTask(params, cls().__thread_pool_json, use_network, use_cache)

    @classmethod
    def download_task(cls, download_url: str, key_word: str,
                      use_network: bool = True, use_cache: bool = True) -> DownloadTask:
        """
        :param download_url:下载地址
        :param key_word:所属关键词
        :param use_network:是否使用网络,默认启用
        :param use_cache:是否使用缓存,默认启用
        """
        return DownloadTask(download_url, key_word, cls().__thread_pool_file, use_network, use_cache)

    @classmethod
    def thumb_task(cls, thumb_url: str, key_word: str,
                   use_network: bool = True, use_cache: bool = True) -> DownloadTask:
        """
        :param thumb_url:下载地址
        :param key_word:所属关键词
        :param use_network:是否使用网络,默认启用
        :param use_cache:是否使用缓存,默认启用
        """
        return DownloadTask(thumb_url, key_word, cls().__thread_pool_thumb, use_network, use_cache)

    @classmethod
    def image_info_task(cls, image_id: str, key_word: str,
                        use_network: bool = True, use_cache: bool = True) -> ImageInfoTask:
        return ImageInfoTask(image_id, key_word, cls().__thread_pool_json, use_network, use_cache)

    @classmethod
    def stop_thumb_task(cls):
        self = cls()
        self.__thread_pool_thumb.stop()
        self.__thread_pool_thumb = TaskManage(Config.THREAD_NUM)

    @classmethod
    def stop_download_task(cls):
        self = cls()
        self.__thread_pool_file.stop()
        self.__thread_pool_file = TaskManage(Config.THREAD_NUM)

    @classmethod
    def stop_json_task(cls):
        self = cls()
        self.__thread_pool_json.stop()
        self.__thread_pool_json = TaskManage(Config.THREAD_NUM)

    @classmethod
    def stop(cls):
        self = cls()
        self.__thread_pool_json.stop()
        self.__thread_pool_file.stop()
        self.__thread_pool_thumb.stop()
        AsyncAPI.stop()


load_config()

if __name__ == '__main__':
    pass
    # test_api = WallHavenAPI()
    # test_params = get_search_params()
    # test_params.q = 'Kitagawa Marin'
    # test_params.categories = '001'
    # test_params.purity = '111'
    # test_task = test_api.search_task(test_params, use_network=True, use_cache=False, search_all=True)
    # test_task.progress_signal.connect(print)
    # test_result: pd.DataFrame = test_task.start(0)
    # if test_result is not None:
    #     test_task_local = test_api.search_task(test_params, use_network=False, use_cache=False, search_all=True)
    #     result_local = test_task_local.start(0)
    #     if result_local is not None:
    #         image_url = test_result.loc[~test_result['远程路径'].isin(
    #             result_local['远程路径']), ['关键词', '远程路径']].values.tolist()
    #         print(image_url)
