"""工具类"""
from SubAPI.WallHaven.ImportPack import *
from SubAPI.WallHaven import Config
from typing import Optional


def add_search_history(key_word: str):
    """添加搜索搜索历史"""
    if len(Config.SEARCH_HISTORY) > Config.SEARCH_HISTORY_COUNT:
        del Config.SEARCH_HISTORY[-1]
    if key_word not in Config.SEARCH_HISTORY:
        Config.SEARCH_HISTORY.insert(0, key_word)


def load_bytesIO(target_path: str) -> BytesIO:
    """
    加载文件
    :param target_path:目标路径
    """
    if file.check_exist(target_path):
        with open(target_path, 'rb') as f:
            return BytesIO(f.read())


def save_bytesIO(save_path: str, target_file: BytesIO):
    """
    保存文件
    :param save_path: 保存路径
    :param target_file: 目标数据
    """
    file.ensure_exist(os.path.dirname(save_path))
    if isinstance(target_file, BytesIO):
        if not file.check_exist(save_path):
            with open(save_path, 'wb') as f:
                f.write(target_file.getvalue())


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
                    print(f'连接超时{self.task.name},正在重试... {get.now_time()}')
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


class ImageData:
    """
    图像数据类,以单个图像为单位进行管理
    通过图像id进行初始化
    """

    def __init__(self, image_id: str, file_type: str, key_word: str, work_pool: TaskManage):
        self.image_id = image_id  # 图像ID
        self.file_type = file_type  # 文件类型
        self.key_word = key_word  # 所属关键词
        self.__work_pool = work_pool  # 用于加载本地图片
        self.image_path = None  # 本地路径
        self.image_cache_path = os.path.join(
            GlobalValue.image_cache_dir, self.image_id + self.file_type)
        self.thumb_cache_path = os.path.join(
            GlobalValue.image_cache_dir, f'thumb_{self.image_id}{self.file_type}')  # 略缩图路径
        self.isExist = None  # 本地是否存在,None表示未知
        self.thumb_bytesio: BytesIO = None  # 略缩图的内存数据
        self.image_bytesio: BytesIO = None  # 原图内存数据
        self.thumb_load_time = 0  # 上次加载时间
        self.image_load_time = 0  # 上次加载时间
        self.lock = Lock()  # 数据访问锁
        self.get_image_info()  # 获取本地数据

    def del_image(self) -> bool:
        """删除本地文件"""
        if file.check_exist(self.image_path):
            with ImageInfo.lock:
                mask = ImageInfo.data()['id'] != self.image_id
                ImageInfo.del_data(mask, use_lock=False)
            self.get_image()
            self.get_image_info()
            file.del_file(self.image_path)
            return True
        return False

    def copy_image(self) -> bool:
        """将图片复制到剪切板中"""
        if self.get_image():
            if self.isExist:
                general.copy_files_to_clipboard(self.image_path)
            else:
                if not file.check_exist(self.image_cache_path):
                    save_bytesIO(self.image_cache_path, self.image_bytesio)
                general.copy_files_to_clipboard(self.image_cache_path)
            return True
        return False

    def generate_save_path(self, image_info: pd.DataFrame) -> str:
        """可以是搜索数据也可以是图像信息数据"""
        image_dir = os.path.join(Config.SAVE_DIR, image_info['分级'].values[0], image_info['类别'].values[0])
        file.ensure_exist(image_dir)
        image_path = os.path.join(image_dir, image_info['id'].values[0] + image_info['文件扩展名'].values[0])
        return image_path

    def save_image_info(self, image_info: pd.DataFrame):
        image_path = self.generate_save_path(image_info)
        with ImageInfo.lock:
            ImageInfo.data().loc[
                ImageInfo.data()['id'] == image_info['id'].values[0], '本地路径'
            ] = os.path.realpath(image_path)
        self.get_image_info()  # 更新文件信息状态

    def save_image(self, image_info: pd.DataFrame, cover=False) -> bool:
        """保存图像文件"""
        image_path = self.generate_save_path(image_info)
        self.save_image_info(image_info)
        if cover or not file.check_exist(image_path):
            image_data = self.get_image().getvalue()
            if image_data:
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                return True
        return False

    def get_image_info(self) -> pd.DataFrame | None:
        """从本地数据内获取图像详细信息"""
        while not ImageInfo.is_loaded(): time.sleep(1)
        with ImageInfo.lock:
            data = ImageInfo.data()[ImageInfo.data()['id'] == self.image_id].copy(deep=True)
        if not data.empty:
            if data['本地路径'].values[0] != '':
                self.image_path = data['本地路径'].values[0]
                self.isExist = True
            return data
        else:
            self.image_path = None
            self.isExist = False

    def get_image(self) -> BytesIO | None:
        """从本地数据内获取图像数据"""
        with self.lock:
            if self.image_bytesio is not None:
                self.image_load_time = time.time()
                return self.image_bytesio
            elif self.image_path is not None and self.isExist:
                task = Task(lambda value=self.image_path: load_bytesIO(value), self.__work_pool)
                self.image_bytesio = task.start(0)
            else:
                task = Task(lambda value=self.image_cache_path: load_bytesIO(value), self.__work_pool)
                self.image_bytesio = task.start(0)
            self.image_load_time = time.time()
            return self.image_bytesio

    def __load_thumb(self) -> BytesIO:
        """将本地图片转为略缩图加载"""
        image = Image_PIL(self.image_path)
        image.resize(Config.THUMB_SIZE)
        return image.get_BytesIO

    def get_thumb(self) -> BytesIO | None:
        """从本地加载略缩图"""
        with self.lock:
            if self.thumb_bytesio is not None:
                self.thumb_load_time = time.time()
                return self.thumb_bytesio
            elif file.check_exist(self.thumb_cache_path):
                task = Task(lambda value=self.thumb_cache_path: load_bytesIO(value), self.__work_pool)
                self.thumb_bytesio = task.start(0)
                self.thumb_load_time = time.time()
                return self.thumb_bytesio
            elif self.image_path is not None and self.isExist:
                task = Task(self.__load_thumb, self.__work_pool)
                self.thumb_bytesio = task.start(0)
                self.thumb_load_time = time.time()
                return self.thumb_bytesio


class ImageManage:
    """图像数据管理类,定时清理图像缓存,单例模式"""
    clear_time = 30  # 清理时间
    all_image_data: dict[str, ImageData] = {}  # 全部图像数据{image_id:ImageData}
    lock = Lock()  # 数据锁
    _instance = None

    def __new__(cls):
        with cls.lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.__load_image_pool = TaskManage(2)  # 用于处理本地图片
        self.__clear_timer = general.ReuseTimer(
            interval=self.__class__.clear_time, func=self.__clear_bytesIO)
        self.__clear_timer.start()

    def __clear_bytesIO(self):
        """清理图像数据缓存"""
        with self.__class__.lock:
            cur_time = time.time()
            for image_data in self.all_image_data.values():
                # 只有加载才会有加载时间
                if image_data.thumb_load_time != 0 and cur_time - image_data.thumb_load_time > self.__class__.clear_time:
                    save_bytesIO(image_data.thumb_cache_path, image_data.get_thumb())
                    with image_data.lock:
                        image_data.thumb_bytesio = None
                if image_data.image_load_time != 0 and cur_time - image_data.image_load_time > self.__class__.clear_time:
                    if image_data.isExist:
                        with image_data.lock:
                            image_data.image_bytesio = None
                    else:
                        save_bytesIO(image_data.image_cache_path, image_data.get_image())
                        with image_data.lock:
                            image_data.image_bytesio = None

    @classmethod
    def get_image_data(cls, image_id: str, file_type: str, key_word: str) -> ImageData:
        """
        获取图像数据类,如果不存在则创建一个新的
        :param image_id:图像id
        :param file_type:文件类型
        :param key_word:所属关键词
        """
        self = cls()
        with self.__class__.lock:
            if image_id not in self.__class__.all_image_data.keys():
                image_data = ImageData(image_id, file_type, key_word, self.__load_image_pool)
                self.__class__.all_image_data[image_id] = image_data
                return image_data
            return self.__class__.all_image_data[image_id]


class SearchTask(Task):

    def __init__(self, params: Config.SearchParams, task_manage: TaskManage,
                 search_all=False, use_network: bool = True, use_cache: bool = True,
                 add_history: bool = False, enable_tags_search=False):
        """
        :param params:搜索参数
        :param task_manage:任务管理类
        :param search_all:搜索全部
        :param use_network:是否使用网络,默认启用
        :param use_cache:是否使用缓存,默认启用
        :param add_history:是否添加到历史记录里
        :param enable_tags_search:启用标签搜索,默认为关键词检索
        """
        self.params = params
        self.task_manage = task_manage
        self.search_all = search_all
        self.use_network = use_network
        self.use_cache = use_cache
        self.enable_tags_search = enable_tags_search
        if add_history:
            add_search_history(params.q)
        func = self.__execute_all if search_all else self.__execute
        name = 'search_all' if search_all else 'search'
        super().__init__(
            func=func, task_manage=task_manage,
            name=f'{params.q}_{params.page}_{name}')

    def __execute(self) -> pd.DataFrame | None:
        """具体的任务函数"""
        if self.use_cache:
            while not SearchData.is_loaded(): time.sleep(1)
            with SearchData.lock:
                result = SearchData.data().loc[
                    (SearchData.data()['关键词'] == self.params.q) &
                    (SearchData.data()['当前页码'] == self.params.page) &
                    (SearchData.data()['类别码'] == self.params.categories) &
                    (SearchData.data()['分级码'] == self.params.purity)
                    ].copy(deep=True).reset_index(drop=True)
            if not result.empty: return result
        if self.use_network:  # 联网搜索
            response = RequestAPI(self, Config.SEARCH_URL, self.params.to_dict())
            if response.result is not None:
                data = response.get_search_data()
                if data is not None:
                    SearchData.add_data(data)
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
            while not ImageInfo.is_loaded(): time.sleep(1)
            # 创建空白pandas表
            with ImageInfo.lock:  # 筛选出本地符合搜索参数的数据
                # 筛选包含关键词的图像信息,case是否区分大小写
                col_name = Config.LOCAL_SEARCH_MODE_TAGS if self.enable_tags_search else Config.LOCAL_SEARCH_MODE_KEY
                case = False if self.enable_tags_search else True
                mask_key = ImageInfo.data()[col_name].str.contains(
                    self.params.q, case=case, na=False, regex=False)
                mask_purity = ImageInfo.data()['分级'].isin(purity)
                mask_categories = ImageInfo.data()['类别'].isin(categories)
                mask_local = ImageInfo.data()['本地路径'] != ''
                result = ImageInfo.data()[mask_key & mask_purity & mask_categories & mask_local].copy(deep=True)
            if not result.empty:
                result.drop(['标签', '本地路径'], axis=1, inplace=True)  # 删除多余列
                result.sort_values('日期', ascending=False, inplace=True)  # 按日期排序
                result.reindex(columns=GlobalValue.search_columns).astype(GlobalValue.search_dtype)
                total_page = int(result.shape[0] / 24) if result.shape[0] % 24 == 0 else int(result.shape[0] / 24) + 1
                result['关键词'] = self.params.q
                result['总页数'] = total_page
                result['总数'] = result.shape[0]
                result['类别码'] = self.params.categories
                result['分级码'] = self.params.purity
                result['当前页码'] = 1
                for page in range(1, total_page + 1):
                    result.iloc[(page - 1) * 24:page * 24, result.columns.get_loc('当前页码')] = page
                SearchData.add_data(result)
                return result[result['当前页码'] == self.params.page].reset_index(drop=True)

    def __execute_all(self) -> pd.DataFrame | None:
        """搜索全部"""

        def sub_task_slot(task: Optional['SearchTask']):
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
            while self.isRunning and self.progress.get_progress() < 100: time.sleep(0)
            if self.isRunning:
                for task in self.sub_task:
                    data = task.result()
                    if data is not None:
                        result = pd.concat([result, data]).drop_duplicates(
                            subset=['id'], keep='last', ignore_index=True)
                    else:
                        return None
                return result

    def stop(self) -> bool:
        if hasattr(self, 'sub_task'):
            for task in self.sub_task:
                task.stop()
        return super().stop()

    def result(self, wait=None) -> pd.DataFrame | None:
        return super().result(wait)


class DownloadTask(Task):

    def __init__(self, download_url: str, key_word: str, task_manage: TaskManage,
                 use_network: bool = True, use_cache: bool = True):
        """
        :param download_url:下载地址
        :param task_manage:任务管理类
        :param key_word:所属关键词
        :param use_network:是否使用网络,默认启用
        :param use_cache:是否使用缓存,默认启用
        """
        self.download_url = download_url
        self.key_word = key_word
        self.use_network = use_network
        self.use_cache = use_cache
        self.image_id, self.file_type = os.path.basename(download_url).split('.')
        self.file_type = f'.{self.file_type}'
        self.desc = 'thumb'
        if self.image_id.find('-') != -1:
            self.image_id = self.image_id.split('-')[1]
            self.desc = 'image'
        super().__init__(
            func=self.__execute, task_manage=task_manage,
            name=f'{self.image_id}_download')

    def __execute(self) -> ImageData | None:
        """返回ImageData类型数据"""
        image_data = ImageManage.get_image_data(
            self.image_id, self.file_type, self.key_word)  # 获取数据缓存
        # 如果本地有数据则会从本地加载,否则返回None
        if self.desc == 'thumb' and image_data.get_thumb():
            return image_data
        elif self.desc == 'image' and image_data.get_image():
            return image_data
        if self.use_network:  # 以上都不存在时发送网络请求
            response = RequestAPI(self, self.download_url)
            if response.result:
                self.progress.total = int(response.result.headers['content-length'])  # 单位字节(b)
                chunk_size = 1024 * 8 if self.progress.total >= 1024 * 100 else 1024 * 32
                data = BytesIO()
                up_time = time.time()
                # iter_content 按chunk_size分块读取
                # 这里会有可能出现读取超时,即request_api函数
                # 的time_out的第二个值是指,两次chunk之间的时间不能超过20秒
                try:
                    for count, chunk in enumerate(response.get_download_data(chunk_size)):
                        if self.isRunning:
                            if chunk:  # 过滤保持连接的chunk
                                data.write(chunk)
                                self.progress.finished += len(chunk)
                                if (count + 1) % 5 == 0:
                                    time_taken = 1024 * (time.time() - up_time)
                                    up_time = time.time()
                                    self.progress.rate = (chunk_size * 5) / time_taken if time_taken != 0 else 0
                                self.progress_signal.emit(self.progress)
                            else:
                                break
                        else:
                            break
                except Exception:
                    return None
                if self.progress.finished == self.progress.total:
                    with image_data.lock:
                        if self.desc == 'thumb':
                            image_data.thumb_bytesio = data
                        elif self.desc == 'image':
                            image_data.image_bytesio = data
                    return image_data

    def result(self, wait=None) -> ImageData | None:
        return super().result(wait)


class ImageInfoTask(Task):
    def __init__(self, image_id: str, key_word: str, task_manage: TaskManage,
                 use_network: bool = True, use_cache: bool = True):
        """
        :param image_id:图像id
        :param key_word:所属关键词
        :param task_manage:任务管理类
        :param use_network:是否使用网络,默认启用
        :param use_cache:是否使用缓存,默认启用
        """
        super().__init__(self.__execute, task_manage, f'{image_id}_tags')
        self.image_id = image_id
        self.key_word = key_word
        self.use_network = use_network
        self.use_cache = use_cache

    def __execute(self) -> pd.DataFrame | None:
        """具体的任务函数"""
        while not ImageInfo.is_loaded(): time.sleep(1)
        with ImageInfo.lock:
            mask = ImageInfo.data()['id'] == self.image_id
            # 添加所属关键词
            if isinstance(self.key_word, str) and self.key_word != '' and not ImageInfo.data().loc[
                mask, '关键词'].str.contains(self.key_word, case=True, na=False, regex=False).any():
                ImageInfo.data().loc[mask, '关键词'] += f';{self.key_word}'
            data = ImageInfo.data().loc[mask].copy(deep=True).reset_index(drop=True)
        if not data.empty: return data
        if self.use_network:
            response = RequestAPI(self, f'{Config.IMAGE_INFO_URL}/{self.image_id}')
            if response.result:
                data = response.get_tags_data()
                if data is not None:
                    data.loc[0, '关键词'] = self.key_word
                    ImageInfo.add_data(data)
                    return data

    def result(self, wait=None) -> pd.DataFrame | None:
        return super().result(wait)


class KeyWordTask(Task):
    def __init__(self, params: Config.SearchParams, task_manage: TaskManage,
                 use_network=True, use_cache=True):
        """
        :param params:搜索参数
        :param task_manage:任务管理类
        :param use_network:是否使用网络,默认启用
        :param use_cache:是否使用缓存,默认启用
        """
        self.params = params
        self.task_manage = task_manage
        self.use_network = use_network
        self.use_cache = use_cache
        super().__init__(self.__execute, task_manage, f'{params.q}_addKey')

    def __execute(self) -> pd.DataFrame | None:
        """具体的任务函数"""
        search_task = SearchTask(self.params, self.task_manage, use_network=self.use_network, use_cache=self.use_cache)
        result = search_task.start(1)
        if result is not None:
            key_data = pd.DataFrame(
                [[
                    self.params.q,
                    result.loc[0, '总页数'],
                    result.loc[0, '总数'],
                    result.loc[0, '日期'],
                    pd.to_datetime(get.now_time("%Y-%m-%d %H:%M:%S")),
                    self.params.categories,
                    self.params.purity
                ]], columns=GlobalValue.key_word_columns
            ).astype(GlobalValue.key_word_dtype)
            KeyWord.add_data(key_data)
            return key_data

    def result(self, wait=None) -> pd.DataFrame | None:
        return super().result(wait)


if __name__ == '__main__':
    from BaseClass import DataManage

    task_manage = TaskManage()
    params = Config.SearchParams()
    params.q = 'poppachan'
    params.purity = '111'
    params.categories = '001'
    local_task = SearchTask(params, task_manage, True, False, False)
    local_result = local_task.start(0)
    print(local_result.shape[0])
    remote_task = SearchTask(params, task_manage, True, True, False)
    remote_task.progress_signal.connect(lambda value: print(f'\r{value.progress.get_progress()}', end=''))
    remote_result = remote_task.start(0)
    print('\n', remote_result.shape[0])
    print(set(remote_result['id']) - set(local_result['id']))
    # info_task = ImageInfoTask('yq8zpl', 'Aleksandra Bodler', task_manage)
    # result = info_task.start(1)
    # download_task = DownloadTask(result.loc[0, '远程路径'], 'Aleksandra Bodler', task_manage)
    # image_file: ImageData = download_task.start(1)
    # Config.SAVE_DIR = './'
    # image_file.save_image(result)
    # DataManage.stop()
