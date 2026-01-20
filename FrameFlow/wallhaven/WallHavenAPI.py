"""
该文件为wallhaven后端API
程序运行时的数据存在在DataManager类中
图像缓存中如果是本地不存在的文件则是BytesIO类型,否则为str(本地路径)
"""
from wallhaven.Tools import *


class WallHavenAPI:
    """
    主控进程
    可以通过get方法获取任务类,调用start方法即可阻塞执行任务
    若不需要阻塞执行则将任务类传入submit方法

    搜索任务关键词:关键词.页码.分类码.分级码
    略缩图任务关键词:图像id.png/图像id.jpg
    下载任务关键词:图像id
    标签任务关键词:图像id_tags
    """
    key_word_path = KEY_WORD_PATH  # 收藏夹路径
    image_info_path = IMAGE_INFO_PATH  # 图像信息路径

    def __init__(self, download_dir=None, num_work=NUM_WORK):
        self.num_work = num_work
        self.api_key = API_KEY
        self.download_dir = SAVE_DIR if download_dir is None else download_dir
        self.isRunning = False  # 运行状态
        # 任务字典name:TaskWorker
        self.__task_dict = ThreadSafe.Dict()
        # 执行任务的线程池
        self.__executor_download = ThreadPoolExecutor(num_work)  # 下载线程池
        self.__executor_json = ThreadPoolExecutor(num_work)  # 文本线程池
        self.data_manager = DataManager()

    def add_key_like(self, key_word) -> pd.DataFrame:
        """添加收藏"""
        # 筛选数据(case是否区分大小写,na空值是否匹配,regex禁用正则表达式)
        with self.data_manager.SEARCH_INFO_LOCK:
            data = self.data_manager.SEARCH_INFO[
                self.data_manager.SEARCH_INFO['关键词'].str.contains(key_word, case=True, na=False, regex=False) &
                self.data_manager.SEARCH_INFO['当前页码'] == 1
                ].copy(deep=True)
        if not data.empty:
            key_data = pd.DataFrame(
                [[key_word,
                  data.iloc[0]['总页数'],
                  data.iloc[0]['总数'],
                  data['日期'].max(),
                  get.now_time('%Y-%m-%d %H:%M:%S')]
                 ],
                columns=KEY_WORD_COLUMNS
            ).astype(KEY_WORD_DTYPE)
            self.data_manager.add_key_word(key_data)
            return key_data
        else:
            return pd.DataFrame([])

    def set_download_dir(self, dir_path: str):
        if dir_path != '':
            self.download_dir = os.path.realpath(dir_path)

    def set_api_key(self, api_key):
        header = {'X-Api-Key': api_key}
        if request_api(f'{IMAGE_INFO_URL}/7p373o', header=header):
            self.api_key = api_key
            return True
        else:
            return False

    def set_num_work(self, num_work):
        """工作线程"""
        self.num_work = num_work

    @staticmethod
    def set_purity(purity: str):
        """设置分级码,支持字符串形式的001/010/111"""
        if (isinstance(purity, str) and
                purity.isdigit() and
                len(purity) == 3):
            SEARCH_PARAMS['purity'] = purity
        else:
            raise ValueError('set_purity 错误:不支持的分级码')

    @staticmethod
    def set_categories(categories: str):
        """设置类别码:100/101/111/等,三位数字每位上的意思(常规/动漫/人物)"""
        if (isinstance(categories, str) and
                categories.isdigit() and
                len(categories) == 3):
            SEARCH_PARAMS['categories'] = categories
        else:
            raise ValueError('set_categories 错误:不支持的类别码')

    @staticmethod
    def set_sort(sort: str):
        SEARCH_PARAMS['sorting'] = sort

    @staticmethod
    def get_purity():
        return SEARCH_PARAMS['purity']

    @staticmethod
    def get_categories():
        return SEARCH_PARAMS['categories']

    @property
    def get_task_names(self):
        """获取当前全部任务的名称"""
        with self.__task_dict.get_lock:
            keys = self.__task_dict.get_dict.copy()
            return list(keys.keys())

    def get_tags_task(self, image_id: str, result_callback=None) -> TaskEnum.Task.Tags:
        """
        获取标签任务
        :param image_id:图像ID
        :param result_callback: 回调函数{'name','state','data'}
        """
        return TaskEnum.Task.Tags(
            f'{image_id}_tags',
            f'{IMAGE_INFO_URL}/{image_id}',
            self.data_manager,
            Signal(result_callback))

    def get_search_task(self, key_word: str, page: int, result_callback=None) -> TaskEnum.Task.Search:
        """
        获取搜索任务
        :param key_word: 关键词
        :param page: 页码
        :param result_callback: 回调函数{'name','state','data'}
        """
        params = SEARCH_PARAMS.copy()
        params['q'] = key_word
        params['page'] = page
        name = f'{params['q']}.{params['page']}.{params['categories']}.{params['purity']}'
        return TaskEnum.Task.Search(
            name, SEARCH_URL, params,
            self.data_manager,
            Signal(result_callback))

    def get_thumbs_task(self, url: str, result_callback=None) -> TaskEnum.Task.Download:
        """
        获取略缩图任务
        :param url:略缩图地址
        :param result_callback:回调函数{'name','state','progress','total','rate','data'}
        """
        name = os.path.basename(url)
        return TaskEnum.Task.Download(
            name, url, self.data_manager, Signal(result_callback))

    def get_download_task(self, tags: pd.DataFrame, key_word: str, result_callback=None) -> TaskEnum.Task.Download:
        """
        获取下载任务
        :param tags : 图像标签
        :param key_word:图像关键词
        :param result_callback:回调函数{'name','state','progress','total','rate','data'}
        """
        tags = tags.iloc[0]
        image_id = tags['id']
        url = tags['远程路径']
        save_dir = os.path.join(self.download_dir, tags['分级'], tags['类别'])
        save_path = os.path.realpath(
            os.path.join(save_dir, tags['id'] + tags['文件扩展名'])
        )
        # 保存数据
        with self.data_manager.IMAGE_INFO_LOCK:
            # 该关键词不存在时添加
            if isinstance(key_word, str) and key_word != '':
                if not self.data_manager.IMAGE_INFO.loc[
                    self.data_manager.IMAGE_INFO['id'] == image_id, '关键词'
                ].str.contains(key_word, case=True, na=False, regex=False).any():
                    self.data_manager.IMAGE_INFO.loc[
                        self.data_manager.IMAGE_INFO['id'] == image_id, '关键词'
                    ] += f';{key_word}'
            # 设置本地路径的值
            self.data_manager.IMAGE_INFO.loc[
                self.data_manager.IMAGE_INFO['id'] == image_id, '本地路径'
            ] = save_path
        if file.check_exist(save_path):
            # with open(save_path, 'rb') as f:
            #     byte_arr = BytesIO(f.read())
            # self.data_manager.IMAGE_CACHE[image_id] = byte_arr
            self.data_manager.IMAGE_CACHE[image_id] = save_path
        return TaskEnum.Task.Download(
            image_id, url, self.data_manager, Signal(result_callback))

    def submit_download(self, image_id: str, key_word: str, result_callback=None):
        """
        提交下载任务
        :param image_id : 图像ID
        :param result_callback:回调函数{'name','state','progress','total','rate','data'}
        """

        def tags_callback(result: dict):
            if result['state'] == TaskEnum.State.success:
                self.submit(self.get_download_task(result['data'], key_word, result_callback))
            else:
                result_callback({'name': image_id,
                                 'state': result['state'],
                                 'progress': 0, 'total': 0, 'rate': 0,
                                 'data': None})

        self.submit(self.get_tags_task(image_id, tags_callback))

    def submit(self, task: TaskEnum.Task.Download | TaskEnum.Task.Search | TaskEnum.Task.Tags) -> bool:
        """
        提交任务
        :param task:任务枚举值
        """
        if self.isRunning:
            TaskWorker(self.__executor_download,
                       self.__executor_json,
                       self.__task_dict,
                       task)
            return True
        else:
            print(f'{self.__class__.__name__}.submit error:未启动')
            return False

    def cancel_task(self, names: str | list):
        """删除任务"""
        with self.__task_dict.get_lock:
            if isinstance(names, str):
                names = [names]
            for name in names:
                task_work: TaskWorker = self.__task_dict.get_dict.pop(name, None)
                if task_work is not None:
                    task_work.stop()

    def start(self):
        self.isRunning = True
        self.data_manager.auto_save_timer.start()  # 启动定时保存

    def stop(self):
        self.isRunning = False
        # 停止全部任务
        with self.__task_dict.get_lock:
            names = self.__task_dict.get_dict.copy()
        self.cancel_task(names)
        self.__executor_download.shutdown(wait=True)
        self.__executor_json.shutdown(wait=True)
        self.data_manager.stop()
        # 保存数据文件
        print('保存数据...')
        self.data_manager.save(self.image_info_path, self.data_manager.IMAGE_INFO)
        self.data_manager.save(self.key_word_path, self.data_manager.KEY_WORD)
        print('数据保存成功')
        # 保存配置文件
        print('保存配置文件')
        save_config(self.download_dir,
                    self.get_categories(),
                    self.get_purity(),
                    self.num_work,
                    self.api_key
                    )

    def save_image(self, image_id: str, cover=False) -> bool:
        """
        保存文件
        :param image_id: 图像id
        :param cover: 是否覆盖,默认不覆盖
        """
        with self.data_manager.IMAGE_INFO_LOCK:
            save_path = self.data_manager.IMAGE_INFO.loc[
                self.data_manager.IMAGE_INFO['id'] == image_id, '本地路径'
            ].copy(deep=True)
        if not save_path.empty:
            save_path = save_path.values[0]
            data = self.data_manager.IMAGE_CACHE.get(image_id, None)
            # if data is not None:
            # 文件是BytesIO类型就代表本地不存在
            if cover or isinstance(data, BytesIO):
                file.ensure_exist(os.path.dirname(save_path))
                with open(save_path, 'wb') as f:
                    f.write(data.getvalue())
            self.data_manager.IMAGE_CACHE.pop(image_id, None)
            return True
        return False
