"""壁纸播放工具类"""
import pandas as pd

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


class ImageProcess:
    """图像处理类,采用子进程处理图像,将其结果返回到队列中"""

    def __init__(self, result_queue: Queue):
        """
        :param result_queue:结果队列
        """
        self.isRunning = False  # 是否正在运行
        self.image_list = None  # 待处理列表
        self.result_queue = result_queue

    def set_image_list(self, image_list):
        """设置待处理列表,如果正在运行中则会关闭处理进程"""
        if self.isRunning:
            self.stop()
        self.image_list = image_list

    def execute(self):
        """执行器,执行单张图像的处理"""
        for image_path in self.image_list:
            image = Image_PIL(image_path)

    def start(self):
        """开始图像处理"""

    def stop(self):
        """停止图像处理"""


class DataManager:
    """播放历史数据管理,调用auto_save_timer属性的start方法可以开启自动保存"""
    IMAGE_HISTORY = pd.DataFrame(columns=IMAGE_HISTORY_COLUMNS).astype(IMAGE_HISTORY_DTYPE)
    IMAGE_HISTORY_LOCK = Lock()

    def __init__(self):
        self.isRunning = True  # 是否运行
        self.isSave = False  # 是否正在保存
        self.isAutoSave = False  # 自动保存是否正在执行
        self.auto_save_time = 60  # 自动保存间隔
        self.auto_save_timer = Timer(self.auto_save_time, self.auto_save)  # 自动保存定时器
        self.auto_save_timer.daemon = True  # 设置为守护线程,确保主线程退出时,改子线程立即退出

    @general.timer_decorator
    def load_history(self, callback=None):
        """
        加载历史数据,返回一个bool值给回调函数
        :param callback:回调函数
        """
        state = False
        extension = file.get_file_extension(IMAGE_HISTORY_PATH)
        # 读取文件
        if extension == '.csv':
            load_pd = pd.read_csv(IMAGE_HISTORY_PATH).astype(IMAGE_HISTORY_DTYPE)
        elif extension == '.xlsx':
            load_pd = pd.read_excel(IMAGE_HISTORY_PATH).astype(IMAGE_HISTORY_DTYPE)
        elif extension == '.feather':
            load_pd = pd.read_feather(IMAGE_HISTORY_PATH).astype(IMAGE_HISTORY_DTYPE)
        # 添加数据
        if file.check_exist(IMAGE_INFO_PATH):
            self.add_history(load_pd)
            state = True
        if callback is not None:
            Signal(callback).emit(state)
        else:
            return state

    def add_history(self, image_id: str | pd.DataFrame):
        """新增已播放数据"""
        if isinstance(image_id, str):
            image_id = pd.DataFrame(image_id, columns=IMAGE_HISTORY_COLUMNS).astype(IMAGE_HISTORY_DTYPE)
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
