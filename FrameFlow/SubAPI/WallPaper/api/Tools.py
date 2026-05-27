"""壁纸播放工具类"""
from SubAPI.WallPaper.ImportPack import *

logger = LogClass.get_logger(__name__, console_level='WARNING')


def load_config():
    # 加载配置文件
    if not CONFIG_DATA.is_loaded(5):
        logger.warning(f'{Config.PACK_NAME} 本地配置加载失败')
        return
    with CONFIG_DATA as data:
        value = data.get_values(section_name=Config.PACK_NAME)
        if value:
            Config.IMAGE_DIR = value.get('image_dir', Config.IMAGE_DIR)
            Config.IMAGE_CHOICE_KEY = value.get('image_choice_key', Config.IMAGE_CHOICE_KEY)
            Config.IMAGE_CHOICE_TAG = value.get('image_choice_tag', Config.IMAGE_CHOICE_TAG)
            Config.IMAGE_CHOICE_CATEGORIES = value.get('image_choice_categories', Config.IMAGE_CHOICE_CATEGORIES)
            Config.IMAGE_CHOICE_PURITY = value.get('image_choice_purity', Config.IMAGE_CHOICE_PURITY)
            Config.IMAGE_PLAY_MODE = value.get('image_play_mode', Config.IMAGE_PLAY_MODE)
            Config.IMAGE_TIME = value.get('image_time', Config.IMAGE_TIME)
            Config.IMAGE_TEMP_NUM = value.get('image_temp_num', Config.IMAGE_TEMP_NUM)
            Config.IMAGE_PLAY_SORT = value.get('image_play_sort', Config.IMAGE_PLAY_SORT)


def save_config():
    data = {}
    data.update({'image_dir': Config.IMAGE_DIR,
                 'image_choice_key': Config.IMAGE_CHOICE_KEY,
                 'image_choice_tag': Config.IMAGE_CHOICE_TAG,
                 'image_choice_categories': Config.IMAGE_CHOICE_CATEGORIES,
                 'image_choice_purity': Config.IMAGE_CHOICE_PURITY,
                 'image_play_mode': Config.IMAGE_PLAY_MODE,
                 'image_time': Config.IMAGE_TIME,
                 'image_temp_num': Config.IMAGE_TEMP_NUM,
                 'image_play_sort': Config.IMAGE_PLAY_SORT
                 })
    CONFIG_DATA.data.add_values(data, Config.PACK_NAME)


def get_screen_size(scaling_factor=1.0):
    """
    获取屏幕尺寸,返回最大屏幕尺寸
    :param scaling_factor:缩放因子,图像的最终尺寸以屏幕尺寸乘以缩放因子
    """
    # 获取所有屏幕信息
    monitors = get_monitors()
    max_width = 0  # 最大宽度
    max_height = 0  # 最大高度
    max_diagonal = 0  # 最大对角线尺寸
    for monitor in monitors:
        cur_width = monitor.width
        cur_height = monitor.height
        cur_diagonal = cur_width ** 2 + cur_height ** 2
        if cur_diagonal > max_diagonal:
            max_width = cur_width
            max_height = cur_height
            max_diagonal = cur_diagonal
    return (int(max_width * scaling_factor),
            int(max_height * scaling_factor))


def get_tags_class() -> list:
    """获取当前全部标签类别"""
    IMAGE_INFO.is_loaded(1)
    # explode将子项展开为每一行
    with IMAGE_INFO as df:
        tags = df[IMAGE_INFO.columns.tags].str.split(';').explode().str.strip().unique()
    return tags.tolist()


def get_keys_class(from_info=False) -> list:
    """
    获取全部关键词
    :param from_info:从图像数据中去重筛选,默认从KeyWord中获取数据
    """
    keys = []
    if from_info:
        if IMAGE_INFO.is_loaded(5):
            # explode将子项展开为每一行
            with IMAGE_INFO as df:
                data = df[IMAGE_INFO.columns.key_word].str.split(';').explode().str.strip().unique()
            if not data.empty:
                keys = data.tolist()
    else:
        if KEY_WORD.is_loaded(5):
            with KEY_WORD as df:
                data = df[KEY_WORD.columns.key_word]
            if not data.empty:
                keys = data.tolist()
    return keys


def get_image_info_by_tags(tag: str, wait=False) -> pd.DataFrame:
    """通过标签获取图像信息"""
    if wait:
        IMAGE_INFO.is_loaded(0)
    with IMAGE_INFO as df:
        if df is not None:
            mask_key = df['标签'].str.contains(tag, case=False, na=False, regex=False)
            result = df[mask_key].copy(deep=True).reset_index(drop=True)
        else:
            result = pd.DataFrame()
    return result


def get_image_info_by_key(key: str | list, wait=False) -> pd.DataFrame:
    """
    通过关键词获取图像信息
    :param key: 关键词（str）或关键词列表（list[str]）
    :param wait: 是否等待数据加载完成
    :return: 匹配的图像信息 DataFrame
    """
    if wait:
        IMAGE_INFO.is_loaded(0)

    # 统一转换为列表处理
    if isinstance(key, str):
        key = [key]
    if not key:
        return pd.DataFrame()
    with IMAGE_INFO as df:
        if df is None or df.empty:
            return pd.DataFrame()
        # 构建匹配掩码：只要包含任意一个关键词即匹配
        mask = pd.Series(False, index=df.index)
        for k in key:
            mask |= df['关键词'].str.contains(k, case=True, na=False, regex=False)
        result = df[mask].copy(deep=True).reset_index(drop=True)
    return result


def image_process_mul(image_path, screen_size) -> tuple[BytesIO, BytesIO] | None:
    """
    处理单张图像
    :param image_path:图像路径
    :param screen_size:屏幕尺寸
    :return 原图,处理后的图像
    """
    try:
        scale = screen_size[0] / screen_size[1]
        image = ImageLoad(image_path)  # 加载待处理图像
        image_format = FileBase(image_path).extension  # 图像扩展名
        image_original = image.get_bytesIO(image_format)  # 获取原图
        if image.is_vertical:
            # 竖屏照片计算拼接两份最符合目标分辨率还是三份最符合
            num_2 = abs((image.width * 2 / image.height) - scale)
            num_3 = abs((image.width * 3 / image.height) - scale)
            num = 1 if num_2 > num_3 else 2
            ImageProcess(image).merge('self', num)
        ImageProcess(image).resize(screen_size).zip(15)  # 限制图像最大尺寸不超过15MB
        image_process = image.get_bytesIO(image_format)
        return image_original, image_process
    except Exception as e:
        print(f'{Config.PACK_NAME}.image_process_mul: {e} :错误文件名称:{image_path}')


def set_sample(sample: bool):
    """是否启用随机"""
    if sample != Config.IMAGE_PLAY_SORT:
        Config.IMAGE_PLAY_SORT = sample


def set_play_mode(mode: int):
    """设置播放模式"""
    if mode not in [Config.IMAGE_CUSTOM_MODE, Config.IMAGE_KEY_MODE, Config.IMAGE_VIDEO_MODE]:
        raise ValueError(f'播放模式不在枚举值内{mode}')
    if mode != Config.IMAGE_PLAY_MODE:
        Config.IMAGE_PLAY_MODE = mode


def select_categories(categories: list | str):
    """
    选择类别筛选(使用中文名称)
    :param categories: 类别列表或单个类别，可选值: '常规', '动漫', '人物'
    """
    if isinstance(categories, str):
        categories = [categories]
    valid_categories = ['常规', '动漫', '人物']
    for cat in categories:
        if cat in valid_categories and cat not in Config.IMAGE_CHOICE_CATEGORIES:
            Config.IMAGE_CHOICE_CATEGORIES.append(cat)


def deselect_categories(categories: list | str):
    """
    取消选择类别筛选
    :param categories: 类别列表或单个类别
    """
    if isinstance(categories, str):
        categories = [categories]
    for cat in categories:
        if cat in Config.IMAGE_CHOICE_CATEGORIES:
            Config.IMAGE_CHOICE_CATEGORIES.remove(cat)


def select_purity(purity: list | str):
    """选择播放级别"""
    if isinstance(purity, str):
        purity = [purity]
    valid_purity = ['正常级', '粗略级', '限制级']
    for pur in purity:
        if pur in valid_purity and pur not in Config.IMAGE_CHOICE_PURITY:
            Config.IMAGE_CHOICE_PURITY.append(pur)


def deselect_purity(purity: list | str):
    """取消选择播放级别"""
    if isinstance(purity, str):
        purity = [purity]
    valid_purity = ['正常级', '粗略级', '限制级']
    for pur in purity:
        if pur in valid_purity and pur in Config.IMAGE_CHOICE_PURITY:
            Config.IMAGE_CHOICE_PURITY.remove(pur)


class ImageQt:
    """用于使用Qt作为桌面窗口进行壁纸播放"""

    def __init__(self):
        self.isRunning = False
        self.image = None  # 当前播放的照片
        self.interval = 60000  # 定时器重置桌面间隔
        self.lock = RLock()  # 用于防止背景在创建或重置时与播放照片冲突
        self.all_widget: dict[str, tuple[WindowDesktop, ImageWidget]] = {}

    def clear_all_widgets(self):
        with self.lock:
            for widget, image_widget in self.all_widget.values():
                image_widget.deleteLater()
                widget.deleteLater()
            self.all_widget = {}

    def createBackground(self):
        """创建桌面背景"""
        if self.isRunning:
            self.clear_all_widgets()
            for screen in QApplication.screens():
                with self.lock:
                    if screen.name() not in self.all_widget:
                        widget = WindowDesktop(screen)
                        image_widget = ImageWidget(self.image)  # 用于显示图像的类
                        widget.addWidget(image_widget)
                        self.all_widget[widget.name] = (widget, image_widget)
            QTimer.singleShot(self.interval, self.createBackground)

    def start(self):
        if QApplication.instance() is None:
            raise RuntimeError('请先创建QApplication实例')
        if not self.isRunning:
            self.isRunning = True
            QTimer.singleShot(0, self.createBackground)

    def stop(self):
        """删除桌面背景,并停止"""
        if self.isRunning:
            self.isRunning = False
            self.clear_all_widgets()

    def set_wallpaper(self, image: np.ndarray | BytesIO):
        """
        设置壁纸
        :param image:图像
        """
        if self.isRunning:
            try:
                with self.lock:
                    image = ImageLoad(image)
                    self.image = image.get_bytesIO()
                    image_w, image_h = image.shape[:2]
                    image_scale = image_w / image_h
                    for widget, image_widget in self.all_widget.values():
                        # 计算屏幕比例与图像比例是否接近,接近则采用拉伸,否则采用填充
                        screen_size = (int(widget.width() * widget.dpi), int(widget.height() * widget.dpi))
                        screen_scale = screen_size[0] / screen_size[1]
                        mode = ImageEnum.resize_stretch if abs(
                            screen_scale - image_scale) < 0.2 else ImageEnum.resize_fill
                        # 重新缩放图像
                        ImageProcess(image).resize(screen_size, mode)
                        image_widget.set_image(image.get_bytesIO())
            except Exception as e:
                print(f'\n{Config.PACK_NAME}.{self.__class__.__name__}.set_wallpaper {e}')
        else:
            print(f'\n{Config.PACK_NAME}.{self.__class__.__name__}.set_wallpaper 请调用start方法后再使用')


class ImageProcessTask:
    """处理单张图片的缩放操作"""

    def __init__(self, image_path: str):
        self.image_id = os.path.basename(image_path).split('.')[0]
        self.image_path = image_path
        self.image_info: Optional[pd.Series] = None  # 图像信息
        self.image_process: Optional[BytesIO] = None  # 处理后的图片
        self.image_original: Optional[BytesIO] = None  # 原图
        self.screen_size = get_screen_size()

    def start(self, parent_task: Task = None) -> bool:
        task = Task(image_process_mul, GlobalValue.GLOBAL_Task_PROCESS_MANAGE,
                    args=(self.image_path, self.screen_size))
        result = task.start(0, parent_task=parent_task)
        if result is not None:
            self.image_original, self.image_process = result
            return True
        return False


class ImageProcessManage:
    """图像处理管理类"""

    def __init__(self, image_temp_num: int = Config.IMAGE_TEMP_NUM):
        """
        :param image_temp_num:图片缓冲数量
        """
        self.isRunning = False  # 是否正在运行
        self.image_temp_num = image_temp_num
        self.process = Task(self._execute, GlobalValue.GLOBAL_TASK_MANAGE, name='ImageProcess')
        self.task_queue = QueueThread(1)  # 任务队列,队列中存放图像路径
        self.result_queue = QueueThread(self.image_temp_num - 1)  # 缓冲队列,队列中存放ImageProcessTask类型

    def submit_image_path(self, image_paths: list | str, timeout=None):
        """
        提交待处理图像路径
        :param image_paths:图片路径列表,当任务满时会阻塞
        :param timeout:超时时间
        """
        if isinstance(image_paths, str):
            image_paths = [image_paths]
        for image_path in image_paths:
            try:
                self.task_queue.put(image_path, timeout=timeout)
            except Full:
                logger.info(f'图像处理队列已满,请稍后再试')
        if not self.isRunning:
            self.start()

    def get_result(self, timeout: int = None) -> ImageProcessTask | None:
        """
        获取结果
        :param timeout:等待超时,None为无限等待,超时返回None
        """
        while self.isRunning:
            try:
                return self.result_queue.get(timeout=timeout)
            except Empty:
                return None

    def _execute(self):
        """子进程执行器"""
        while self.isRunning:
            try:
                image_path = self.task_queue.get(timeout=1)
                if FileBase(image_path).exists:
                    task = ImageProcessTask(image_path)
                    result = task.start(self.process)
                    if result:
                        while self.isRunning:
                            try:
                                self.result_queue.put(task, timeout=1)
                                break
                            except Full:
                                pass
            except Empty:
                pass

    def start(self):
        """开始图像处理"""
        if not self.isRunning:
            self.isRunning = True
            self.process.start(priority=1)

    def stop(self):
        """停止图像处理"""
        if self.isRunning:
            self.isRunning = False
            self.process.stop()


class ImageKeyMode:
    """关键字模式,可支持标签,播放数据的添加不需要指定关键词"""

    def __init__(self):
        # 播放数据
        self.use_tags = False
        self.play_data = pd.DataFrame(columns=DataConfig.image_info_columns).astype(DataConfig.image_info_dtype)
        self.history_data = IMAGE_HISTORY
        self.__lock = RLock()

    def enable_tags_mode(self, value=True):
        """启用/关闭标签模式"""
        self.use_tags = value

    def get_filter_data(self) -> pd.DataFrame:
        """获取筛选后的总数据,当筛选后为空时返回play_data"""
        mask_categories = pd.Series([True] * len(self.play_data), index=self.play_data.index)
        mask_purity = pd.Series([True] * len(self.play_data), index=self.play_data.index)

        if Config.IMAGE_CHOICE_CATEGORIES:
            mask_categories = self.play_data['类别'].isin(Config.IMAGE_CHOICE_CATEGORIES)

        if Config.IMAGE_CHOICE_PURITY:
            mask_purity = self.play_data['分级'].isin(Config.IMAGE_CHOICE_PURITY)

        total_data = self.play_data[mask_categories & mask_purity]
        if total_data.empty:
            total_data = self.play_data
        return total_data

    def get_play_progress(self) -> tuple:
        """获取播放进度"""
        with self.__lock:
            total_data = self.get_filter_data()
            mask = total_data['本地路径'].isin(self.history_data.data['本地路径'])
            filter_data = total_data[mask]

            return filter_data.shape[0], total_data.shape[0]

    def get_image_play_data(self, n: int = 1, sample: bool = False) -> pd.DataFrame:
        """
        获取图像信息
        :param n:取几张图片,默认1张
        :param sample:启用随机,默认不随机
        """
        with self.__lock:
            if self.play_data.empty:
                return self.play_data
            # 获取筛选后的总数据
            total_data = self.get_filter_data()
            # 去除掉已经播放的
            mask_history = ~total_data['本地路径'].isin(self.history_data.data['本地路径'])
            filter_data = total_data[mask_history]
            # 如果为空则删除播放历史重新循环
            if filter_data.empty:
                self.history_data.clear()
                filter_data = total_data
            data = filter_data.sample(n=n) if sample else filter_data.head(n)
            self.history_data.add_data(data)
            return data

    def get_image_play_info(self, image_path: str) -> pd.Series | None:
        """根据图像路径获取信息,如果在播放列表内会返回数据,否则返回None"""
        image_info = self.play_data[self.play_data['本地路径'] == image_path].copy(deep=True).reset_index(drop=True)
        if not image_info.empty:
            return image_info.iloc[0]

    def _add_play_data(self, data: pd.DataFrame):
        data.sort_values('日期', ascending=False, inplace=True)
        with self.__lock:
            self.play_data = pd.concat([self.play_data, data]).drop_duplicates(
                subset=['本地路径'], keep='last', ignore_index=True)

    def _del_play_data(self, key: str | list | set = None):
        """
        删除播放数据
        :param key:关键词/标签,为None时删除全部播放数据
        """
        with self.__lock:
            if key is not None:
                column = '标签' if self.use_tags else '关键词'
                if isinstance(key, str):
                    key = [key]
                # 构建匹配掩码：只要包含任意一个关键词即匹配
                mask = pd.Series(False, index=self.play_data.index)
                for k in key:
                    mask |= self.play_data[column].str.contains(k, case=True, na=False, regex=False)
                self.play_data = self.play_data[~mask].reset_index(drop=True)
            else:
                self.play_data = pd.DataFrame(columns=DataConfig.image_info_columns).astype(
                    DataConfig.image_info_dtype)

    def clear_play_data(self):
        """清空播放数据"""
        with self.__lock:
            self.play_data = pd.DataFrame(columns=DataConfig.image_info_columns).astype(
                DataConfig.image_info_dtype)

    def select_key(self, key: str | list, image_info: pd.DataFrame = None) -> bool:
        """选择关键词"""
        with self.__lock:
            if isinstance(key, str):
                key = [key]
            diff_key = set(key) - set(Config.IMAGE_CHOICE_KEY)  # 求差
            if diff_key:  # 记录已选择的关键词
                Config.IMAGE_CHOICE_KEY.extend(diff_key)
            image_info = get_image_info_by_key(key) if image_info is None else image_info
            if not image_info.empty:
                self._add_play_data(image_info)
                text = f'为{key}' if len(key) < 5 else f'长度为{len(key)}'
                logger.info(f'已成功选择关键词 {text}')
                return True
            text = f'为{key}' if len(key) < 5 else f'长度为{len(key)}'
            logger.info(f'选择关键词失败 {text}')
            return False

    def deselect_key(self, key: str | list) -> bool:
        """取消选择关键词"""
        with self.__lock:
            if isinstance(key, str):
                key = [key]
            common_key = set(Config.IMAGE_CHOICE_KEY) & set(key)  # 求交集
            if common_key:  # 记录要取消的关键词
                for k in common_key:
                    Config.IMAGE_CHOICE_KEY.remove(k)
                self._del_play_data(common_key)
            text = f'为{common_key}' if len(common_key) < 5 else f'长度为{len(common_key)}'
            logger.info(f'已成功取消关键词 {text}')
            return True
