"""壁纸播放API"""
from SubAPI.WallPaper.api.Tools import *

logger = LogClass.get_logger(__name__, console_level='WARNING')


class ImagePlay:
    """壁纸播放"""

    def __init__(self):
        self.isRunning = False
        # 信号
        self.start_signal = TaskSignal()  # 播放开始信号,发送True
        self.pause_signal = TaskSignal()  # 播放暂停信号,暂停时发送True,恢复时发送False
        self.play_image_signal = TaskSignal()  # 当前播放的图片,发送ImageProcessTask类
        # 图像处理
        self._image_qt = ImageQt()  # 壁纸Qt接口管理类
        self._image_process_manage = ImageProcessManage()  # 图像处理进程管理器
        self._play_timer = ReuseTimer(Config.IMAGE_TIME, self._set_wallpaper, '设置壁纸')  # 播放定时器
        self._submit_timer = ReuseTimer(0, self._submit_image_process, '任务提交')  # 提交图像处理任务定时器
        # 播放模式
        self._image_key_mode = ImageKeyMode()

    @property
    def image_key_mode(self) -> 'ImageKeyMode':
        """返回收藏夹播放模式"""
        return self._image_key_mode

    def _submit_image_process(self):
        """提交图像处理任务"""
        local_paths = []  # 本地路径
        # 获取数据
        if Config.IMAGE_PLAY_MODE == Config.IMAGE_KEY_MODE:
            image_data = self._image_key_mode.get_image_play_data(sample=Config.IMAGE_PLAY_SORT)
            if not image_data.empty:
                local_paths = image_data['本地路径'].tolist()
        elif Config.IMAGE_PLAY_MODE == Config.IMAGE_CUSTOM_MODE:
            pass
        elif Config.IMAGE_PLAY_MODE == Config.IMAGE_VIDEO_MODE:
            pass
        # 提交处理任务
        if local_paths:
            logger.debug(f'已经获取数据 长度:{len(local_paths)}')
            self._image_process_manage.submit_image_path(local_paths)
        else:
            logger.info('数据为空')
            self.pause()

    def _set_wallpaper(self):
        """获取处理后的图像并设置为壁纸"""

        def key_mode(task: ImageProcessTask) -> bool:
            """关键词模式"""
            # 确保图片在播放列表中
            image_info = self._image_key_mode.get_image_play_info(task.image_path)
            if image_info is not None:
                task.image_info = image_info
                self.play_image_signal.emit(task)
                self._image_qt.set_wallpaper(task.image_process)
                logger.debug(f'图像设置成功 路径:{task.image_path}')
                return True
            logger.debug(f'图像不在播放列表中 路径:{task.image_path}')
            return False

        while self.isRunning:
            result = self._image_process_manage.get_result()
            if result is None:  # 图像处理数据为空
                logger.info('获取图像为空')
                time.sleep(1)
                continue
            if Config.IMAGE_PLAY_MODE == Config.IMAGE_KEY_MODE:  # 判断模式
                if key_mode(result):
                    break

    def set_image_play_time(self, value: float | int):
        """设置播放间隔"""
        if isinstance(value, (float, int)):
            if value != Config.IMAGE_TIME:
                Config.IMAGE_TIME = value
                self._play_timer.setInterval(value)
                logger.info(f'设置播放间隔时间 {value}s')
            else:
                logger.info(f'播放间隔时间未改变 {value}s')
        else:
            logger.warning(f'播放间隔时间参数错误 {value}')

    def start(self):
        if not self.isRunning:
            self.isRunning = True
            self._image_qt.start()
            self._submit_timer.start()
            self._play_timer.start()
            logger.info(f"\n\t当前播放模式:{Config.IMAGE_PLAY_MODE}\n"
                        f"\t当前播放时间:{Config.IMAGE_TIME}\n"
                        f"\t当前播放顺序:{Config.IMAGE_PLAY_SORT}\n"
                        f"\t当前播放分级:{Config.IMAGE_CHOICE_PURITY}\n"
                        f"\t当前播放分类:{Config.IMAGE_CHOICE_CATEGORIES}")
            self.start_signal.emit(True)
        else:
            logger.warning('播放已启动')

    def pause(self):
        if not self.isRunning:
            logger.warning('播放已停止')
            return
        self._play_timer.pause()
        self._submit_timer.pause()
        logger.info('播放已暂停')
        self.pause_signal.emit(True)

    def resume(self):
        if not self.isRunning:
            logger.warning('播放已停止')
            return
        self._play_timer.resume()
        self._submit_timer.resume()
        logger.info('播放已恢复')
        self.pause_signal.emit(False)

    def stop(self):
        if self.isRunning:
            self.isRunning = False
            self._image_qt.stop()
            self._submit_timer.stop()
            self._play_timer.stop()
            self._image_process_manage.stop()
            logger.info('播放已停止')


@singleton_decorator
class WallPaperAPI(ImagePlay):
    """全局唯一播放实例"""

    def __init__(self):
        super().__init__()

    def select_key(self, key: str | list) -> bool:
        """选择关键词"""
        return self.image_key_mode.select_key(key)

    def deselect_key(self, key: str | list) -> bool:
        """取消选择关键词"""
        return self.image_key_mode.deselect_key(key)

    @property
    def isPause(self) -> bool:
        return self._play_timer.isPause or self._submit_timer.isPause


if __name__ == '__main__':
    from Fun.BaseTools import LogManager
    from SubAPI.DataManage import DATA_MANAGE
    from PySide6.QtWidgets import QApplication

    set_play_mode(1)  # 设置播放模式为收藏夹模式
    set_sample(False)
    image_play_test = ImagePlay()
    image_play_test.set_image_play_time(3)
    all_key_class = get_keys_class()
    image_play_test.image_key_mode.select_key(all_key_class[0])

    app = QApplication([])

    image_play_test.start()
    try:
        LogManager().set_console_output(console_level='INFO')
        QTimer.singleShot(5000, lambda: set_sample(True))
        app.exec()
    except Exception:
        pass
    finally:
        image_play_test.stop()
        DATA_MANAGE.stop()
