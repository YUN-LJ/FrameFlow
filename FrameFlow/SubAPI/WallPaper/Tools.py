"""壁纸播放工具类"""
import numpy as np
import pandas as pd
from SubAPI.WallPaper.ImportPack import *
from SubAPI.WallPaper import Config
from SubAPI.WallHaven.Config import CATEGORY_DICT, PURITY_DICT


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
    ImageInfo.is_loaded(1)
    # explode将子项展开为每一行
    tags = ImageInfo.data()[ImageInfo.columns.tags].str.split(';').explode().str.strip().unique()
    return tags.tolist()


def get_keys_class(from_info=False) -> list:
    """
    获取全部关键词
    :param from_info:从图像数据中去重筛选,默认从KeyWord中获取数据
    """
    if from_info:
        ImageInfo.is_loaded(1)
        # explode将子项展开为每一行
        keys = ImageInfo.data()[ImageInfo.columns.key_word].str.split(';').explode().str.strip().unique()
        return keys.tolist()
    else:
        KeyWord.is_loaded(1)
        keys = KeyWord.data()[KeyWord.columns.key_word].tolist()
        return keys


def get_image_info_by_tags(tag: str) -> pd.DataFrame:
    """通过标签获取图像信息"""
    ImageInfo.is_loaded(1)
    mask_key = ImageInfo.data()['标签'].str.contains(
        tag, case=False, na=False, regex=False)
    result = ImageInfo.data()[mask_key].copy(deep=True).reset_index(drop=True)
    return result


def get_image_info_by_key(key: str) -> pd.DataFrame:
    """通过关键词获取图像信息"""
    ImageInfo.is_loaded(1)
    mask_key = ImageInfo.data()['关键词'].str.contains(
        key, case=True, na=False, regex=False)
    result = ImageInfo.data()[mask_key].copy(deep=True).reset_index(drop=True)
    return result


class ImageQt:
    """用于使用Qt作为桌面窗口进行壁纸播放"""

    def __init__(self):
        self.isRunning = False
        self.image = None  # 当前播放的照片
        self.interval = 60000  # 定时器重置桌面间隔
        self.lock = Lock()  # 用于防止背景在创建或重置时与播放照片冲突
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
        self.image_format = FileBase(image_path).extension
        self.image_info: pd.Series = None  # 图像信息
        self.image_process: BytesIO = None  # 处理后的图片
        self.image_original: BytesIO = None  # 原图
        self.screen_size = get_screen_size()

    def start(self) -> np.ndarray | None:
        try:
            scale = self.screen_size[0] / self.screen_size[1]
            image = ImageLoad(self.image_path)
            self.image_original = image.get_bytesIO(self.image_format)
            if image.is_vertical:
                # 竖屏照片计算拼接两份最符合目标分辨率还是三份最符合
                num_2 = abs((image.width * 2 / image.height) - scale)
                num_3 = abs((image.width * 3 / image.height) - scale)
                num = 1 if num_2 > num_3 else 2
                ImageProcess(image).merge('self', num)
            ImageProcess(image).resize(self.screen_size).zip(15)  # 限制图像最大尺寸不超过15MB
            self.image_process = image.get_bytesIO(self.image_format)
            del image
            gc.collect()
            return self.image_process
        except Exception as e:
            print(f'\n{Config.PACK_NAME}.{self.__class__.__name__}.execute: {e} :'
                  f'错误文件名称:{self.image_path}')


class ImageProcessManage:
    """图像处理管理类"""

    def __init__(self, image_temp_num: int = Config.IMAGE_TEMP_NUM, use_process: bool = False):
        """
        :param image_temp_num:图片缓冲数量
        :param use_process:使用独立进程处理,默认使用线程
        """
        self.isRunning = False  # 是否正在运行
        self.image_temp_num = image_temp_num
        self.use_process = use_process
        if use_process:
            self.process = Process(target=self._execute, name='ImageProcess')
            self.task_queue = QueueMul(1)  # 任务队列,队列中存放图像路径
            self.result_queue = QueueMul(self.image_temp_num - 1)  # 缓冲队列,队列中存放ImageProcessTask类型
        else:
            self.process = Thread(target=self._execute, name='ImageProcess', daemon=True)
            self.task_queue = QueueThread(1)  # 任务队列,队列中存放图像路径
            self.result_queue = QueueThread(self.image_temp_num - 1)  # 缓冲队列,队列中存放ImageProcessTask类型

    def submit_image_path(self, image_paths: list | str):
        """
        提交待处理图像路径
        :param image_paths:图片路径列表,当任务满时会阻塞
        """
        if isinstance(image_paths, str):
            image_paths = [image_paths]
        for image_path in image_paths:
            self.task_queue.put(image_path)
        if not self.isRunning:
            self.start()

    def get_result(self, wait: bool = False) -> ImageProcessTask | None:
        """
        获取结果
        :param wait:是否等待,不等待则有可能返回None
        """
        time_out = 1 if wait else 0
        while self.isRunning:
            try:
                return self.result_queue.get(timeout=time_out)
            except Empty:
                if not wait:
                    return None

    def _execute(self):
        """子进程执行器"""
        while self.isRunning:
            try:
                image_path = self.task_queue.get(timeout=1)
                if FileBase(image_path).exists:
                    task = ImageProcessTask(image_path)
                    result = task.start()
                    if result is not None:
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
            self.process.start()

    def stop(self):
        """停止图像处理"""
        if self.isRunning:
            self.isRunning = False
            try:
                if self.use_process:
                    self.process.kill()  # 退出进程
            except Exception as e:
                print(f'\n{Config.PACK_NAME}.{self.__class__.__name__}.stop: {e}')
            finally:
                if self.use_process:
                    self.process = Process(target=self._execute, name='ImageProcess')
                else:
                    self.process = Thread(target=self._execute, name='ImageProcess', daemon=True)


class ImagePlay:
    """壁纸播放"""

    def __init__(self, image_key_mode: 'ImageKeyMode'):
        self.isRunning = False
        self.sample = bool(Config.IMAGE_PLAY_SORT)
        self.start_signal = TaskSignal()
        self.pause_signal = TaskSignal()
        self.play_image_signal = TaskSignal()  # 当前播放的图片,发送ImageProcessTask类
        self.image_key_mode = image_key_mode  # 关键词模式数据管理类
        self.image_qt = ImageQt()  # 壁纸Qt接口管理类
        self.image_process_manage = ImageProcessManage()  # 图像处理进程管理器
        self.play_timer = ReuseTimer(Config.IMAGE_TIME, self.set_wallpaper)
        self.submit_timer = ReuseTimer(0, self.submit_image_process)

    def set_sample(self, value: bool):
        self.sample = value
        if value != Config.IMAGE_PLAY_SORT:
            Config.IMAGE_PLAY_SORT = int(value)

    def submit_image_process(self):
        """提交图像处理任务"""
        image_data = None
        if Config.IMAGE_PLAY_MODE == Config.IMAGE_KEY_MODE:
            image_data = self.image_key_mode.get_image_play_data(sample=self.sample)
        if image_data is not None and image_data['本地路径'].tolist():
            self.image_process_manage.submit_image_path(image_data['本地路径'].tolist())
        else:
            if not self.play_timer.isPause:
                self.pause()
            time.sleep(1)

    def set_wallpaper(self):
        """获取处理后的图像并设置为壁纸"""

        def key_mode(result: ImageProcessTask) -> bool:
            """关键词模式"""
            # 确保图片在播放列表中
            image_info = self.image_key_mode.get_image_play_info(result.image_path)
            if image_info is not None:
                result.image_info = image_info
                self.play_image_signal.emit(result)
                self.image_qt.set_wallpaper(result.image_process)
                return True
            return False

        while self.isRunning:
            result = self.image_process_manage.get_result(True)
            if result is not None:  # 图像处理数据不为空
                if Config.IMAGE_PLAY_MODE == Config.IMAGE_KEY_MODE:  # 判断模式
                    if key_mode(result):
                        break

    def start(self):
        if not self.isRunning:
            self.isRunning = True
            self.image_qt.start()
            self.submit_timer.start()
            self.play_timer.start()
            self.start_signal.emit(True)

    def pause(self):
        self.play_timer.pause()
        self.submit_timer.pause()
        self.pause_signal.emit(True)

    def stop(self):
        if self.isRunning:
            self.isRunning = False
            self.image_qt.stop()
            self.submit_timer.stop()
            self.play_timer.stop()
            self.image_process_manage.stop()


class ImageKeyMode:
    """关键字模式,可支持标签,播放数据的添加不需要指定关键词"""

    def __init__(self):
        # 播放数据
        self.use_tags = False
        self.play_data = pd.DataFrame(columns=GlobalValue.image_info_columns).astype(GlobalValue.image_info_dtype)
        self.history_data = ImageHistory()
        self.__lock = Lock()

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
            mask = total_data['本地路径'].isin(self.history_data.data()['本地路径'])
            filter_data = total_data[mask]

            return (filter_data.shape[0], total_data.shape[0])

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
            mask_history = ~total_data['本地路径'].isin(self.history_data.data()['本地路径'])
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

    def add_play_data(self, data: pd.DataFrame):
        data.sort_values('日期', ascending=False, inplace=True)
        with self.__lock:
            self.play_data = pd.concat([self.play_data, data]).drop_duplicates(
                subset=['本地路径'], keep='last', ignore_index=True)

    def del_play_data(self, key: str = None):
        """
        删除播放数据
        :param key:关键词/标签
        """
        with self.__lock:
            if key is not None:
                column = '标签' if self.use_tags else '关键词'
                mask_bool = ~self.play_data[column].str.contains(
                    key, case=True, na=False, regex=False)
                self.play_data = self.play_data[mask_bool].reset_index(drop=True)
            else:
                self.play_data = pd.DataFrame(columns=GlobalValue.image_info_columns).astype(
                    GlobalValue.image_info_dtype)

    def clear_play_data(self):
        """清空播放数据"""
        with self.__lock:
            self.play_data = pd.DataFrame(columns=GlobalValue.image_info_columns).astype(
                GlobalValue.image_info_dtype)


if __name__ == '__main__':
    print(get_image_info_by_key('Nian Tuanzitu').shape)
