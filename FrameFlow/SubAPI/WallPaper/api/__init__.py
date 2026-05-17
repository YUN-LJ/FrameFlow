from SubAPI.WallPaper.api.Tools import *


@singleton_decorator
class WallPaperAPI:

    def __init__(self):
        self._lock = Lock()
        self.image_key_mode = ImageKeyMode()  # 关键词模式
        self.image_play = ImagePlay(self.image_key_mode)  # 图像播放类
        self.start_signal = self.image_play.start_signal
        self.pause_signal = self.image_play.pause_signal
        self.play_image_signal = self.image_play.play_image_signal

    def select_key(self, key: str | list, image_info: pd.DataFrame = None) -> bool:
        """选择关键词"""
        with self._lock:
            if isinstance(key, str):
                key = [key]
            diff_key = set(key) - set(Config.IMAGE_CHOICE_KEY)
            if diff_key:  # 记录已选择的关键词
                Config.IMAGE_CHOICE_KEY.extend(diff_key)
            image_info = get_image_info_by_key(key) if image_info is None else image_info
            if not image_info.empty:
                self.image_key_mode.add_play_data(image_info)
                return True
            return False

    def deselect_key(self, key: str | list) -> bool:
        """取消选择关键词"""
        with self._lock:
            if isinstance(key, str):
                key = [key]
            diff_key = set(Config.IMAGE_CHOICE_KEY) - set(key)
            if diff_key:  # 记录已选择的关键词
                for k in diff_key:
                    Config.IMAGE_CHOICE_KEY.remove(k)
            self.image_key_mode.del_play_data(key)
            return True

    def select_categories(self, categories: list | str):
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

    def deselect_categories(self, categories: list | str):
        """
        取消选择类别筛选
        :param categories: 类别列表或单个类别
        """
        if isinstance(categories, str):
            categories = [categories]
        for cat in categories:
            if cat in Config.IMAGE_CHOICE_CATEGORIES:
                Config.IMAGE_CHOICE_CATEGORIES.remove(cat)

    def clear_categories(self):
        """清空类别筛选"""
        Config.IMAGE_CHOICE_CATEGORIES.clear()

    def select_purity(self, purity: list | str):
        """
        选择分级筛选(使用中文名称)
        :param purity: 分级列表或单个分级，可选值: '正常级', '粗略级', '限制级'
        """
        if isinstance(purity, str):
            purity = [purity]
        valid_purity = ['正常级', '粗略级', '限制级']
        for pur in purity:
            if pur in valid_purity and pur not in Config.IMAGE_CHOICE_PURITY:
                Config.IMAGE_CHOICE_PURITY.append(pur)

    def deselect_purity(self, purity: list | str):
        """
        取消选择分级筛选
        :param purity: 分级列表或单个分级
        """
        if isinstance(purity, str):
            purity = [purity]
        for pur in purity:
            if pur in Config.IMAGE_CHOICE_PURITY:
                Config.IMAGE_CHOICE_PURITY.remove(pur)

    def clear_purity(self):
        """清空分级筛选"""
        Config.IMAGE_CHOICE_PURITY.clear()

    def set_sample(self, value: bool):
        self.image_play.set_sample(value)

    def set_image_play_time(self, value):
        self.image_play.play_timer.setInterval(value)
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
        print(f"当前播放模式:{Config.IMAGE_PLAY_MODE}\n"
              f"当前播放时间:{Config.IMAGE_TIME}\n"
              f"当前播放顺序:{Config.IMAGE_PLAY_SORT}\n"
              f"当前播放分级:{Config.IMAGE_CHOICE_PURITY}\n"
              f"当前播放分类:{Config.IMAGE_CHOICE_CATEGORIES}")

    def pause(self):
        self.image_play.pause()

    def stop(self):
        self.image_play.stop()
