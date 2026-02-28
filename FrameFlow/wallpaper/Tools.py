"""壁纸播放工具类"""
from wallpaper.Config import *


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


class ImageQt:
    """用于使用Qt作为桌面窗口进行壁纸播放"""

    def __init__(self):
        self.isRunning = False
        self.all_widget = {}
        self.timer = QTimer()  # 定时器,用于实时检测新增显示器
        self.timer.timeout.connect(self.create)

    def create(self):
        """创建桌面背景"""
        for screen in QApplication.screens():
            if screen.name() not in self.all_widget:
                widget = WindowDesktop(screen)
                image_widegt = ImageWidget()  # 用于显示图像的类
                widget.addWidget(image_widegt)
                self.all_widget[widget.name] = (widget, image_widegt)

    def start(self):
        if not self.isRunning:
            self.isRunning = True
            self.timer.start(1000)

    def stop(self):
        """删除桌面背景,并停止"""
        if self.isRunning:
            for widget, image_widegt in self.all_widget.values():
                image_widegt.deleteLater()
                widget.deleteLater()
            self.all_widget = {}
            self.timer.stop()
            self.isRunning = False

    def set_wallpaper(self, image: np.ndarray):
        """
        设置壁纸
        :param image:图像
        """
        if self.isRunning:
            try:
                image_w, image_h = image.shape[:2]
                image_scale = image_w / image_h
                for widget, image_widget in self.all_widget.values():
                    # 计算屏幕比例与图像比例是否接近,接近则采用拉伸,否则采用填充
                    screen_size = (int(widget.width() * widget.dpi), int(widget.height() * widget.dpi))
                    screen_scale = screen_size[0] / screen_size[1]
                    mode = Image_Enum.resize_stretch if abs(
                        screen_scale - image_scale) < 0.2 else Image_Enum.resize_fill
                    # 重新缩放图像
                    image_progress = Image_PIL()
                    image_progress.open_image(image)
                    image_progress.resize(screen_size, stretch=mode)
                    image_widget.set_image(image_progress.get_array)
            except Exception as e:
                print(f'\n{PACK_NAME}.{self.__class__.__name__}.set_wallpaper {e}')
        else:
            print(f'\n{PACK_NAME}.{self.__class__.__name__}.set_wallpaper 请调用start方法后再使用')


class ImageProcess:
    """图像处理类,采用子进程处理图像,将其结果返回到队列中"""

    def __init__(self, image_temp_num: int, scaling_factor=1.0):
        """
        :param image_temp_num:图片缓冲数量
        """
        self.isRunning = False  # 是否正在运行
        self.image_list = None  # 待处理列表
        self.image_temp_num = image_temp_num
        self.scaling_factor = scaling_factor  # 缩放因子,图像的最终尺寸以屏幕尺寸乘以缩放因子
        self.screen_size = self.get_screen_size()  # 获取屏幕尺寸
        self.result_queue = Queue(self.image_temp_num)  # 缓冲队列,默认三张
        self.process = Process(target=self.execute, name='ImageProcess')

    def set_temp_num(self, image_temp_num: int):
        """设置图像缓冲数量,如果正在运行中则会关闭处理进程"""
        if self.isRunning:
            self.stop()
        self.image_temp_num = image_temp_num

    def set_image_list(self, image_list):
        """设置待处理列表,如果正在运行中则会关闭处理进程"""
        if self.isRunning:
            self.stop()
        self.image_list = image_list

    def get_screen_size(self):
        """获取屏幕尺寸,返回最大屏幕尺寸"""
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
        return (int(max_width * self.scaling_factor),
                int(max_height * self.scaling_factor))

    def get_image(self, timeout=3) -> tuple[str, np.ndarray, np.ndarray] | None:
        """获取图片"""
        try:
            result = self.result_queue.get(timeout=timeout)
            return result
        except Empty:
            return None

    def execute(self):
        """执行器,执行单张图像的处理"""
        scale = self.screen_size[0] / self.screen_size[1]
        image = Image_PIL(load_trunc_images=True)
        for image_path in self.image_list:
            try:
                image.open_image(image_path)
                image_org = image.get_array
                if not image.check_w_screen:
                    # 竖屏照片计算拼接两份最符合目标分辨率还是三份最符合
                    w, h = image.get_size
                    num_2 = abs((w * 2 / h) - scale)
                    num_3 = abs((w * 3 / h) - scale)
                    num = 1 if num_2 > num_3 else 2
                    image.merge(other_half='self', num=num)  # 如果是竖屏照片则横向复制一份
                image.resize(size=self.screen_size)
                image.zip(max_size=15)  # 限制图像最大尺寸不超过15MB
                self.result_queue.put((image_path, image.get_array, image_org))
            except Exception as e:
                print(f'\n{PACK_NAME}.{self.__class__.__name__}.execute: {e} :'
                      f'错误文件名称:{image_path}')
        self.result_queue.put((None, None, None))

    def start(self):
        """开始图像处理"""
        if self.image_list != []:
            self.isRunning = True
            self.process.start()

    def stop(self):
        """停止图像处理"""
        if self.isRunning:
            try:
                self.process.kill()
            except Exception as e:
                print(f'\n{PACK_NAME}.{self.__class__.__name__}.stop: 错误{e}')
            finally:
                self.process = Process(target=self.execute, name='ImageProcess')
                self.result_queue = Queue(self.image_temp_num)  # 清空队列
                self.isRunning = False


class DataManager:
    """播放历史数据管理,调用auto_save_timer属性的start方法可以开启自动保存"""
    # 类属性
    isSave = False  # 是否正在保存
    isAutoSave = False  # 自动保存是否正在执行
    auto_save_time = 60  # 自动保存间隔
    IMAGE_HISTORY = pd.DataFrame(columns=IMAGE_HISTORY_COLUMNS).astype(IMAGE_HISTORY_DTYPE)
    IMAGE_HISTORY_LOCK = Lock()

    def __init__(self):
        self.isRunning = True  # 是否运行
        self.auto_save_timer = Timer(self.auto_save_time, self.auto_save)  # 自动保存定时器
        self.auto_save_timer.daemon = True  # 设置为守护线程,确保主线程退出时,改子线程立即退出

    @general.timer_decorator
    def load_history(self, callback=None):
        """
        加载历史数据,返回一个bool值给回调函数
        :param callback:回调函数
        """
        state = False
        if file.check_exist(IMAGE_HISTORY_PATH):
            extension = file.get_file_extension(IMAGE_HISTORY_PATH)
            # 读取文件
            if extension == '.csv':
                load_pd = pd.read_csv(IMAGE_HISTORY_PATH).astype(IMAGE_HISTORY_DTYPE)
            elif extension == '.xlsx':
                load_pd = pd.read_excel(IMAGE_HISTORY_PATH).astype(IMAGE_HISTORY_DTYPE)
            elif extension == '.feather':
                load_pd = pd.read_feather(IMAGE_HISTORY_PATH).astype(IMAGE_HISTORY_DTYPE)
            # 添加数据
            if not load_pd.empty:
                self.add_history(load_pd)
                state = True
        if callback is not None:
            Signal(callback).emit(state)
        else:
            return state

    def add_history(self, image_id: str | pd.DataFrame):
        """新增已播放数据"""
        if isinstance(image_id, str):
            image_id = pd.DataFrame([image_id], columns=IMAGE_HISTORY_COLUMNS).astype(IMAGE_HISTORY_DTYPE)
        with self.IMAGE_HISTORY_LOCK:
            # 表合并+数据去重(链式操作pandas内部有优化且避免线程安全问题)
            self.IMAGE_HISTORY = pd.concat([self.IMAGE_HISTORY, image_id]).drop_duplicates(
                subset=['id'], keep='last', ignore_index=True)

    def clear_history(self):
        """清空播放历史"""
        with self.IMAGE_HISTORY_LOCK:
            self.IMAGE_HISTORY = pd.DataFrame(columns=IMAGE_HISTORY_COLUMNS).astype(IMAGE_HISTORY_DTYPE)

    def get_history(self):
        """获取播放历史"""
        with self.IMAGE_HISTORY_LOCK:
            return self.IMAGE_HISTORY['id'].tolist()

    def auto_save(self):
        """自动保存"""
        if self.isRunning:
            print(f'\n{PACK_NAME}.{self.__class__.__name__}.auto_save :'
                  f'正在保存,当前时间:{get.now_time('%Y-%m-%d %H:%M:%S')}')
            self.isAutoSave = True
            with self.IMAGE_HISTORY_LOCK:
                self.save(IMAGE_HISTORY_PATH, self.IMAGE_HISTORY)
            self.isAutoSave = False
            # 重新设置定时器
            if self.isRunning:
                self.auto_save_timer = Timer(self.auto_save_time, self.auto_save)
                self.auto_save_timer.daemon = True
                self.auto_save_timer.start()

    def save(self, file_path: str, df: pd.DataFrame):
        try:
            self.isSave = True
            extension = os.path.splitext(file_path)[1]
            file.ensure_exist(os.path.dirname(file_path))
            if extension == '.xlsx':
                df.to_excel(file_path, index=False)
            elif extension == '.csv':
                df.to_csv(file_path, index=False, encoding='utf-8')
            elif extension == '.feather':
                df.to_feather(file_path)
            self.isSave = False
            return True
        except Exception as e:
            print(f'{PACK_NAME}.{self.__class__.__name__}.save error:\n\t{e}')
            return False

    def stop(self):
        self.isRunning = False
        if self.auto_save_timer.is_alive():
            self.auto_save_timer.cancel()
        while self.isSave or self.isAutoSave:
            time.sleep(1)
