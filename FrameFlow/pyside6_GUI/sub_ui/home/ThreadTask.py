"""后台任务线程"""
from pyside6_GUI.sub_ui.home.widgetUI.Config import *


class ThreadTask(QThread):
    """多任务后台线程"""
    # 任务枚举值
    SEARCH = 'search'  # 搜索任务采用->关键词.页码.分类码.分级码
    DOWNLOAD = 'download'  # 下载任务采用->图像ID
    VIEW = 'view'  # 显示原图任务->图像ID
    THUMB = 'thumb'  # 略缩图任务采用->图像ID+扩展名
    LOADUI = 'loadui'  # UI加载任务->loadui
    UPDATEKEY = 'updatekey'  # 关键词更新任务->关键词
    task_enum = [SEARCH, DOWNLOAD, THUMB, LOADUI, UPDATEKEY]

    # 任务信号
    start = Signal(tuple)  # 任务开始信号(任务名称,任务枚举值)
    finished = Signal(tuple)  # 任务结束信号(任务名称,任务枚举值,任务是否成功)
    done = Signal(tuple)  # 任务进行信号(任务名称,任务枚举值,一些描述任务进度的参数)

    def __init__(self, wallhaven_api: WallHavenAPI, parent, num_work=NUM_WORK):
        super().__init__()
        self.num_work = num_work
        self.parent = parent
        self.isRunning = False
        self.wallhaven_api = wallhaven_api
        self.task_dict = Dict()  # 任务字典{任务枚举值:[]}
        self.task_queue = Queue()  # 任务队列
        self.update_key_executor = ThreadPoolExecutor(1)  # 更新关键词的线程池
        self.load_thumbs_executor = ThreadPoolExecutor(num_work)  # 加载本地略缩图线程池

    def add_task(self, task_name, task_enum, task_args):
        """提交任务(任务名称,任务枚举值,任务所需参数)"""
        try:
            self.task_queue.put((task_name, task_enum, task_args))
            with self.task_dict.get_lock:
                enum_list = self.task_dict.get_dict.get(task_enum, None)
                if enum_list is None:
                    self.task_dict.get_dict[task_enum] = List(initial_data=[task_name])
                else:
                    enum_list.append(task_name)
            if not self.isRunning:
                self.start()
        except Exception as e:
            print(f'{self.__class__.__name__}.add_task({task_name}) error: {e}')

    def task_search(self, task_name: str, key_word: str, page: int = None, callback=None):
        """
        搜索任务
        :param key_word:搜索关键词
        :param page:指定搜索页码,默认搜索全部
        :param callback:用于搜索全部页时指定返回函数

        该任务发送done和finished两个信号
        done发送的最后一个参数为pd.DataFrame类型
        如果是搜索全部页,可能会为空pd.DataFrame
        发送finished时代表任务已经结束
        """

        def callback_page(result: dict):
            nonlocal search_all, last_page, page, count, callback
            if search_all:
                if result['state'] == TaskEnum.State.success:
                    search_all = False
                    last_page = result['data'].iloc[0]['总页数']
                    for page in range(1, last_page + 1):
                        if callback is None:
                            self.wallhaven_api.submit(self.wallhaven_api.get_search_task(key_word, page, callback_page))
                        else:
                            self.wallhaven_api.submit(self.wallhaven_api.get_search_task(key_word, page, callback))
                elif result['state'] in TaskEnum.State.finished:
                    self.finished_task(task_name, self.SEARCH, False, page)
            else:
                if result['state'] == TaskEnum.State.success:
                    count += 1
                    self.done.emit((task_name, self.SEARCH, result['data']))
                    if count == last_page:
                        self.finished_task(task_name, self.SEARCH, True, page)
                elif result['state'] in TaskEnum.State.finished:
                    self.finished_task(task_name, self.SEARCH, False, page)

        count = 0
        last_page = 1
        self.start_task(task_name, self.SEARCH)  # 发送任务一开始信号
        search_all = True if page is None else False  # 是否搜索全部页
        page = page if page is not None else 1
        self.wallhaven_api.submit(self.wallhaven_api.get_search_task(key_word, page, callback_page))

    def task_thumb(self, task_name: str, url: str, image_widget: ImageWidget):
        """略缩图加载任务"""

        def result_callback(result: dict):
            if result['state'] == TaskEnum.State.success:
                if not image_widget.is_same_image(result['data']):
                    self.done.emit((task_name, self.THUMB, (result['data'], image_widget)))
                self.finished_task(task_name, self.THUMB, True)
            elif result['state'] in TaskEnum.State.finished:
                self.finished_task(task_name, self.THUMB, False)

        def result_load():
            nonlocal save_path
            if self.isRunning and not image_widget.is_same_image(save_path):
                name = os.path.basename(save_path)
                image = self.wallhaven_api.data_manager.IMAGE_CACHE.get(name, None)
                if image is None:
                    image = Image_PIL(save_path).zip(0.1)
                    self.wallhaven_api.data_manager.IMAGE_CACHE[name] = image
                self.done.emit((task_name, self.THUMB, (image, image_widget)))
                self.finished_task(task_name, self.THUMB, True)

        # 检查本地是否存在原图,如果存在则不请求略缩图加载
        image_id = os.path.basename(url).split('.')[0]
        with self.wallhaven_api.data_manager.IMAGE_INFO_LOCK:
            save_path = self.wallhaven_api.data_manager.IMAGE_INFO.loc[
                self.wallhaven_api.data_manager.IMAGE_INFO['id'] == image_id, '本地路径'
            ].copy(deep=True)
        if save_path.empty:
            self.wallhaven_api.submit(self.wallhaven_api.get_thumbs_task(url, result_callback))
        else:
            save_path = save_path.iloc[0]
            self.load_thumbs_executor.submit(result_load)

    def task_download(self, task_name: str, image_id: str, key_word: str):
        """下载任务"""

        def result_callback(result: dict):
            """结果回调"""
            nonlocal task_name, image_id
            if self.isRunning:
                if result['state'] == TaskEnum.State.success:
                    self.wallhaven_api.save_image(image_id)
                    self.finished_task(task_name, self.DOWNLOAD, TaskEnum, key_word)
                elif result['state'] == TaskEnum.State.running:
                    self.done.emit((task_name, self.DOWNLOAD, result))
                elif result['state'] in TaskEnum.State.finished:
                    self.finished_task(task_name, self.DOWNLOAD, False, key_word)

        self.start_task(task_name, self.DOWNLOAD)
        self.wallhaven_api.submit_download(image_id, key_word, result_callback)

    def task_view(self, task_name: str, image_id: str, key_word: str, image_dialog):

        def tags_callback(result: dict):
            nonlocal image_dialog
            if self.isRunning:
                if result['state'] == TaskEnum.State.success:
                    self.done.emit((task_name, self.VIEW, (result['data'], image_dialog)))
                    # 提交下载
                    self.wallhaven_api.submit(
                        self.wallhaven_api.get_download_task(result['data'], key_word, result_callback))
                elif result['state'] in TaskEnum.State.finished:
                    self.finished_task(task_name, self.VIEW, False, image_dialog)

        def result_callback(result: dict):
            """结果回调"""
            nonlocal task_name, image_id, image_dialog
            if self.isRunning:
                if result['state'] == TaskEnum.State.success:
                    self.done.emit((task_name, self.VIEW, (result['data'], image_dialog)))
                    self.finished_task(task_name, self.VIEW, True, image_dialog)
                elif result['state'] == TaskEnum.State.running:
                    self.done.emit((task_name, self.VIEW, (result, image_dialog)))
                elif result['state'] in TaskEnum.State.finished:
                    self.finished_task(task_name, self.VIEW, False, image_dialog)

        self.wallhaven_api.submit(self.wallhaven_api.get_tags_task(image_id, tags_callback))

    def task_update_key(self, task_name: str, key_word: str):
        """
        更新收藏夹内的关键词
        任务流程:
            1.搜索第一页数据,检查是否需要更新
            2.搜索全部数据,筛选出没在image_info文件中的图像id,提交下载任务
            3.等待下载任务全部完成
        """
        all_image_id = set()  # 搜索到的全部图像ID
        image_info_total = None  # 本地数据中已经有的图像ID
        update_image_id: List = None  # 需要更新的图像
        update_total = None  # 总计需要更新的数量
        isUpdate = None  # 是否需要更新
        isFail = False  # 是否失败
        count = 0
        last_page = None
        total = None
        date = None

        def search_callback(result: dict):
            """搜索回调函数"""
            nonlocal last_page, total, date, image_info_total, isUpdate, isFail
            if self.isRunning:
                if result['state'] == TaskEnum.State.success:
                    # 检查是否需要更新
                    last_page = result['data'].iloc[0]['总页数']
                    total = result['data'].iloc[0]['总数']  # 图片总数量
                    date = result['data'].iloc[0]['日期']
                    with self.wallhaven_api.data_manager.KEY_WORD_LOCK:
                        key_info = self.wallhaven_api.data_manager.KEY_WORD.loc[
                            self.wallhaven_api.data_manager.KEY_WORD['关键词'] == key_word
                            ].copy(deep=True)
                    with self.wallhaven_api.data_manager.IMAGE_INFO_LOCK:
                        # 筛选数据(case是否区分大小写,na空值是否匹配,regex禁用正则表达式)
                        image_info_total = self.wallhaven_api.data_manager.IMAGE_INFO.loc[
                            self.wallhaven_api.data_manager.IMAGE_INFO['关键词'].str.contains(
                                key_word, case=True, na=False, regex=False)].copy(deep=True)  # 图像信息中记录了多少条数据
                    # 筛选数据是否有''值
                    image_info_total = image_info_total.loc[~image_info_total.eq('').any(axis=1), 'id']
                    if (total - image_info_total.shape[0] > 3 or
                            (key_info['总数'] != total).any() or
                            (date > key_info['最新日期']).any()):
                        isUpdate = True
                        image_info_total = set(image_info_total)
                        # 需要更新,获取全部页面数据
                        for page in range(1, last_page + 1):
                            self.wallhaven_api.submit(
                                self.wallhaven_api.get_search_task(key_word, page, data_filter))
                    else:
                        isUpdate = False
                        self.done.emit((task_name, self.UPDATEKEY, (task_name, total, total)))  # 更新进度
                        self.done.emit((task_name, self.UPDATEKEY, (last_page, total, date, [])))  # 添加下载
                elif result['state'] in TaskEnum.State.finished:
                    isFail = True

        def data_filter(result: dict):
            nonlocal count, last_page, \
                all_image_id, image_info_total, \
                update_image_id, update_total, \
                isUpdate, isFail
            if self.isRunning:
                if result['state'] == TaskEnum.State.success:
                    all_image_id.update(result['data']['id'].tolist())
                    count += 1
                    self.done.emit((task_name, self.UPDATEKEY, (task_name, count, last_page)))  # 发送进度
                    if count == last_page:
                        update_image_id = List()
                        update_image_id.extend(list(all_image_id - image_info_total))
                        update_total = len(update_image_id)
                        if update_total != 0:
                            isUpdate = True
                            # 将需要下载的图像ID发送给UI
                            self.done.emit((task_name, self.UPDATEKEY, (last_page, total, date, update_image_id)))
                            self.finished_task(task_name, self.UPDATEKEY, True, 1)
                            self.finished.connect(monitor_download)
                        else:
                            isUpdate = False
                elif result['state'] in TaskEnum.State.finished:
                    isFail = True

        def monitor_download(args):
            nonlocal update_image_id, update_total
            if self.isRunning:
                image_id, _, task_state = args
                if task_state[0]:
                    update_image_id.remove(image_id)
                else:
                    items = self.parent.right_widget.cell_items.get(image_id, None)
                    if items is not None:
                        items['button'].click()
                self.done.emit((task_name, self.UPDATEKEY,
                                (task_name, update_total - len(update_image_id), update_total)))

        if self.isRunning:
            self.start_task(task_name, self.UPDATEKEY)
            # 搜索第一页数据
            self.wallhaven_api.submit(
                self.wallhaven_api.get_search_task(key_word, 1, search_callback))
            while self.isRunning:
                if isFail:
                    self.finished_task(task_name, self.UPDATEKEY, False)
                    break
                if isUpdate is None:
                    time.sleep(1)
                    continue
                else:
                    if isUpdate:
                        if update_image_id is not None and len(update_image_id) == 0:
                            self.finished.disconnect(monitor_download)
                            self.finished_task(task_name, self.UPDATEKEY, True, 2)
                            break
                    else:
                        self.finished_task(task_name, self.UPDATEKEY, True, 2)
                        break
                    time.sleep(1)

    def task_load_ui(self):
        """后台加载UI资源"""

        def callback(result):
            if result and self.isRunning:
                with self.wallhaven_api.data_manager.KEY_WORD_LOCK:
                    data = self.wallhaven_api.data_manager.KEY_WORD.copy(deep=True)
                if not data.empty:
                    for index, row in data.iterrows():
                        self.done.emit(
                            (self.LOADUI, self.LOADUI,
                             (row['关键词'], row['总页数'],
                              row['总数'], row['最新日期'],
                              row['上次更新'])
                             )
                        )
                    self.finished_task(self.LOADUI, self.LOADUI, True)

        if file.check_exist(self.wallhaven_api.key_word_path):
            self.wallhaven_api.data_manager.load_image_and_key(callback)

    def cancel_task(self, task_name: str | list):
        """
        删除任务
        :param task_name: 任务名称
        """
        if task_name in self.task_enum:
            task_name = self.task_dict.pop(task_name, None)
        if task_name:
            self.wallhaven_api.cancel_task(task_name)

    def start_task(self, task_name, task_enum):
        self.start.emit((task_name, task_enum))

    def finished_task(self, task_name, task_enum, state, data=None):
        """任务成功后发射信号"""
        if self.task_dict.get(task_enum, None):
            self.task_dict[task_enum].remove(task_name)
        self.finished.emit((task_name, task_enum, (state, data)))

    def stop(self):
        self.isRunning = False
        self.update_key_executor.shutdown()
        self.wait()

    def run(self):
        self.isRunning = True
        while self.isRunning:
            try:
                task_name, task_enum, task_args = self.task_queue.get(timeout=1)
                if task_enum == self.SEARCH:  # 搜索任务
                    self.task_search(task_name, *task_args)
                elif task_enum == self.THUMB:
                    self.task_thumb(task_name, *task_args)
                elif task_enum == self.DOWNLOAD:
                    self.task_download(task_name, *task_args)
                elif task_enum == self.VIEW:
                    self.task_view(task_name, *task_args)
                elif task_enum == self.LOADUI:
                    self.task_load_ui()
                elif task_enum == self.UPDATEKEY:
                    self.update_key_executor.submit(
                        self.task_update_key,
                        task_name, task_args)
            except Empty:
                pass
