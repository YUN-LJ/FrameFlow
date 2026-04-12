"""
壁纸播放API
面向对象编程方式
"""
from SubAPI.WallPaper.ImportPack import *
from SubAPI.WallPaper import Config
from SubAPI.WallPaper.Tools import *


def load_config():
    # 加载配置文件
    while not ConfigData.is_loaded(): time.sleep(0.1)
    with ConfigData.lock:
        value = ConfigData.data().get_values(section_name=Config.PACK_NAME)
        if value:
            Config.IMAGE_DIR = value.get('image_dir', Config.IMAGE_DIR)
            Config.IMAGE_CHOICE_KEY = value.get('image_choice_key', Config.IMAGE_CHOICE_KEY)
            Config.IMAGE_CHOICE_TAG = value.get('image_choice_tag', Config.IMAGE_CHOICE_TAG)
            Config.IMAGE_PLAY_MODE = value.get('image_play_mode', Config.IMAGE_PLAY_MODE)
            Config.IMAGE_TIME = value.get('image_time', Config.IMAGE_TIME)
            Config.IMAGE_TEMP_NUM = value.get('image_temp_num', Config.IMAGE_TEMP_NUM)
            Config.IMAGE_PLAY_SORT = value.get('image_play_sort', Config.IMAGE_PLAY_SORT)


def save_config():
    data = {}
    data.update({'image_dir': Config.IMAGE_DIR,
                 'image_choice_key': Config.IMAGE_CHOICE_KEY,
                 'image_choice_tag': Config.IMAGE_CHOICE_TAG,
                 'image_play_mode': Config.IMAGE_PLAY_MODE,
                 'image_time': Config.IMAGE_TIME,
                 'image_temp_num': Config.IMAGE_TEMP_NUM,
                 'image_play_sort': Config.IMAGE_PLAY_SORT
                 })
    ConfigData.data().add_values(data, Config.PACK_NAME)


class WallPaperAPI:
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
        self.image_key_mode = ImageKeyMode()  # 关键词模式
        self.image_play = ImagePlay(self.image_key_mode)  # 图像播放类
        self.start_signal = self.image_play.start_signal
        self.pause_signal = self.image_play.pause_signal
        self.play_image_signal = self.image_play.play_image_signal

    def select_key(self, key: str, image_info: pd.DataFrame = None) -> bool:
        """选择关键词"""
        with self._lock:
            if key not in Config.IMAGE_CHOICE_KEY:
                Config.IMAGE_CHOICE_KEY.append(key)
            image_info = get_image_info_by_key(key) if image_info is None else image_info
            self.image_key_mode.add_play_data(image_info)
            return True

    def deselect_key(self, key: str) -> bool:
        """取消选择关键词"""
        with self._lock:
            if key in Config.IMAGE_CHOICE_KEY:
                Config.IMAGE_CHOICE_KEY.remove(key)
            self.image_key_mode.del_play_data(key)
            return True

    def set_sample(self, value: bool):
        self.image_play.set_sample(value)

    def set_image_play_time(self, value):
        self.image_play.play_timer.set_interval(value)
        if value != Config.IMAGE_TIME:
            Config.IMAGE_TIME = value

    @staticmethod
    def set_image_play_mode(value):
        if value != Config.IMAGE_PLAY_MODE:
            Config.IMAGE_PLAY_MODE = value

    @property
    def isPause(self) -> bool:
        return self.image_play.play_timer.isPause

    def start(self):
        self.image_play.start()

    def pause(self):
        self.image_play.pause()

    def stop(self):
        self.image_play.stop()


load_config()
