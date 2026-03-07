"""
wallhaven外部接口
"""
from wallhaven.ImportPack import *


class ImageData:
    """图像数据类"""
    Clear_Time = 30  # 清理时间

    def __init__(self, image_id: str, type: str):
        self.image_id = image_id  # 图像ID
        self.type = type  # 文件类型
        self.cache_path = os.path.join(GlobalValue.image_cache_dir, image_id + type)  # 缓存地址
        self.image_path = None  # 本地路径
        self.thumb_bytesio: BytesIO = None  # 略缩图的内存数据
        self.image_bytesio: BytesIO = None  # 原图内存数据
        self.__lock = Lock()
        self.__clear_bytesio = general.ReuseTimer(
            self.__class__.Clear_Time, self.__clear_image, is_while=False)

    def get_thumb(self) -> BytesIO | None:
        if self.thumb_bytesio is not None:
            return self.thumb_bytesio

    def get_image(self) -> BytesIO | None:
        with self.__lock:
            if self.image_bytesio is not None:
                data = self.image_bytesio
            elif self.image_path is not None:
                data = self.load_bytesIO(self.image_path)
            else:
                data = self.load_bytesIO(self.cache_path)
            self.__clear_bytesio.start()
            return data

    def set_image(self, data):
        with self.__lock:
            self.image_bytesio = data
        self.__clear_bytesio.start()

    def __clear_image(self):
        with self.__lock:
            if self.image_path is None and not file.check_exist(self.cache_path):
                self.save_bytesIO(self.cache_path, self.image_bytesio)
            self.image_bytesio = None

    @staticmethod
    def load_bytesIO(file_path) -> BytesIO:
        """加载文件"""
        if file.check_exist(file_path):
            with open(file_path, 'rb') as f:
                return BytesIO(f.read())

    def save_bytesIO(self, save_path: str, save_file: BytesIO):
        """保存文件"""
        file.ensure_exist(os.path.dirname(save_path))
        if isinstance(save_file, BytesIO):
            with open(save_path, 'wb') as f:
                f.write(save_file.getvalue())
            self.image_path = save_path


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
            url, params, self.__class__.Timeout, retry=self.__class__.Retry
        )

    def request_api(self, url, params=None, timeout=(3, 10), header=None, retry=3) -> bool | requests.Response:
        """
        请求API结果
        :param url:请求链接
        :param params:参数
        :param timeout:设置超时(连接超时,读取超时)
        :param header:请求头
        :param retry:重试次数
        :return 如果请求成功则返回requests.Response,否则返回Flase
        """
        header = Config.HEADERS if header is None else header
        for _ in range(retry):
            while not self.task.isCancel:
                try:
                    response = requests.get(url,
                                            stream=True,  # 允许流式获取
                                            params=params,  # 请求参数
                                            headers=header,  # 头文件
                                            timeout=timeout,  # 超时
                                            # verify=False,  # 忽略SSL证书验证
                                            )
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


class WallHavenAPI:
    """wallhavenAPI"""
    json_task = 'json_task'  # json任务
    file_task = 'file_task'  # 原图下载任务
    thumb_task = 'thumb_task'  # 略缩图下载任务

    def __init__(self):
        """
        初始化
        """
        self.isRunning = True
        self.image_cache = ThreadSafe.Dict()  # 图像缓存{download_url:BytesIO}
        self.search_params = Config.SearchParams(Config.SEARCH_PARAMS)
        self.__thread_pool_json = TaskManage(Config.THREAD_NUM)
        self.__thread_pool_file = TaskManage(Config.THREAD_NUM)
        self.__thread_pool_thumb = TaskManage(Config.THREAD_NUM)

    @property
    def get_search_params(self) -> Config.SearchParams:
        return self.search_params

    def get_search_task(self, search_params: Config.SearchParams) -> Task:
        """
        获取搜索任务
        :param search_params:搜索参数
        """

        def sub_func() -> pd.DataFrame | None:
            nonlocal search_params, task
            with search_data.lock:  # 获取数据缓存
                result = search_data.data.loc[
                    (search_data.data['关键词'] == search_params.q) &
                    (search_data.data['当前页码'] == search_params.page) &
                    (search_data.data['类别码'] == search_params.categories) &
                    (search_data.data['分级码'] == search_params.purity)
                    ].copy(deep=True)
            if not result.empty: return result
            response = RequestAPI(task, Config.SEARCH_URL, search_params.to_dict())
            if response.result is not None:
                data = response.get_search_data()
                if data is not None:
                    search_data.add_data(data)
                return data

        task = Task(func=sub_func,
                    name=f'{search_params.q}_{search_params.page}',
                    desc=self.__class__.json_task)
        return task

    def get_search_all_task(self, search_params: Config.SearchParams) -> Task:
        """获取搜索全部的任务"""

    def get_download_task(self, download_url: str) -> Task:
        """
        获取下载任务
        :param download_url:下载地址
        """

        def sub_func() -> ImageData | None:
            """如果本地存在的文件则返回的是str即文件路径,否则从网络上下载BytesIO类型文件"""
            nonlocal task, download_url, image_id, image_type
            image_data: ImageData = self.image_cache.get(image_id)  # 获取数据缓存
            if image_data is None:
                image_data = ImageData(image_id, f'.{image_type}')
            else:
                if task.desc == self.__class__.thumb_task and image_data.get_thumb():
                    return image_data
                elif task.desc == self.__class__.file_task and image_data.get_image():
                    return image_data
            # 如果是原图下载检查本地是否已经存在
            if task.desc == self.__class__.file_task:
                while not image_info_task.done(): time.sleep(1)
                with image_info.lock:
                    image_path = image_info.data.loc[
                        image_info.data['id'] == image_id, '本地路径'
                    ].copy(deep=True)
                if not image_path.empty and image_path.iloc[0]:
                    image_data.image_path = image_path.iloc[0]
                    image_data.get_image()  # 加载本地文件
                    self.image_cache[image_id] = image_data
                    return image_data
            # 以上都不存在时发送网络请求
            response = RequestAPI(task, download_url)
            if response.result:
                task.progress.total = int(response.result.headers['content-length'])  # 单位字节(b)
                chunk_size = 1024 * 8 if task.progress.total >= 1024 * 100 else 1024 * 32
                data = BytesIO()
                up_time = time.time()
                # iter_content 按chunk_size分块读取
                # 这里会有可能出现读取超时,即request_api函数
                # 的time_out的第二个值是指,两次chunk之间的时间不能超过20秒
                for count, chunk in enumerate(response.get_download_data(chunk_size)):
                    if self.isRunning and not task.isCancel:
                        if chunk:  # 过滤保持连接的chunk
                            data.write(chunk)
                            task.progress.finished += len(chunk)
                            if (count + 1) % 5 == 0:
                                time_taken = 1024 * (time.time() - up_time)
                                up_time = time.time()
                                task.progress.rate = (chunk_size * 5) / time_taken if time_taken != 0 else 0
                        else:
                            break
                    else:
                        break
                if task.progress.finished == task.progress.total:
                    if task.desc == self.__class__.file_task:
                        image_data.set_image(data)  # 设置内存数据,将在一段时间后自动保存到缓存文件夹中
                    elif task.desc == self.__class__.thumb_task:
                        image_data.thumb_bytesio = data  # 设置内存数据
                    self.image_cache[image_id] = image_data
                    return image_data

        image_id, image_type = os.path.basename(download_url).split('.')
        # 确定是原图下载还是略缩图下载
        if '-' in image_id:
            image_id = image_id.split('-')[1]
            desc = self.__class__.file_task
        else:
            desc = self.__class__.thumb_task
        task = Task(func=sub_func, name=f'{image_id}_download', desc=desc)
        return task

    def get_tags_task(self, image_id: str) -> Task:
        def sub_func() -> pd.DataFrame | None:
            nonlocal image_id
            while not image_info_task.done(): time.sleep(1)
            with image_info.lock:
                data = image_info.data[image_info.data['id'] == image_id].copy(deep=True)
            if not data.empty: return data
            response = RequestAPI(task, f'{Config.IMAGE_INFO_URL}/{image_id}')
            if response.result:
                data = response.get_tags_data()
                if data is not None:
                    image_info.add_data(data)
                return data

        task = Task(sub_func, name=f'{image_id}_tags', desc=self.__class__.json_task)
        return task

    def add_task(self, task: Task):
        if task.desc == self.__class__.file_task:
            return self.__thread_pool_file.add_task(task)
        elif task.desc == self.__class__.json_task:
            return self.__thread_pool_json.add_task(task)
        elif task.desc == self.__class__.thumb_task:
            return self.__thread_pool_thumb.add_task(task)
        else:
            return self.__thread_pool_json.add_task(task)

    def close_thumb_pool(self):
        self.__thread_pool_thumb.stop()
        self.__thread_pool_thumb = TaskManage(Config.THREAD_NUM)

    def stop(self):
        self.isRunning = False
        self.__thread_pool_json.stop()
        self.__thread_pool_file.stop()
        self.__thread_pool_thumb.stop()
        data = self.search_params.to_dict()
        data.update({'save_dir': Config.SAVE_DIR, 'num_work': Config.THREAD_NUM, 'api_key': Config.API_KEY})
        del data['q'], data['page']
        config_data.data.add_values(data, Config.PACK_NAME)


if __name__ == '__main__':
    from wallhaven.WallHavenAPI import WallHavenAPI

    # requet_limit = WallHavenAPI()
    # search_params = requet_limit.get_search_params
    # search_params.q = 'Fantasy Factory'
    # search_params.purity = '111'
    # search_params.categories = '001'
    # task = requet_limit.get_search_task(search_params)
    # requet_limit.add_task(task)
    # while not task.done():
    #     time.sleep(1)
    # print(task.result())
