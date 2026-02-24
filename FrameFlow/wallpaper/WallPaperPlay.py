"""壁纸播放主文件"""
from wallpaper.Tools import *


class WallPaperPlay:
    """
    壁纸播放类
    该类只能在主线程中创建
    """
    image_play_signal = Signal()  # 壁纸播放时发送当前播放的图像名称和图像数据
    image_erro_stop_signal = Signal()  # 壁纸播放因错误发生导致停止时发送True

    def __init__(self):
        # 类属性
        self.isRunning = False  # 是否正在运行
        self.image_mode = IMAGE_CUSTOM_MODE  # 默认为自定义模式,不同的播放模式将影响播放列表
        self.image_api = IMAGE_WINDOWS_QT  # 默认为使用QT作为底层窗口
        self.image_time = IMAGE_TIME  # 播放时间间隔
        self.image_dir = IMAGE_DIR  # 用户壁纸文件夹路径
        self.image_temp_num = IMAGE_TEMP_NUM  # 壁纸缓存数量
        # 图像处理类
        self.image_process = ImageProcess(
            image_temp_num=self.image_temp_num, scaling_factor=1.0
        )
        # 已播放的历史数据管理
        self.data_manager = DataManager()
        Thread(target=self.data_manager.load_history, daemon=True).start()  # 后台加载历史文件
        self.image_list = []  # 播放列表
        # Qt桌面背景设置,必须由主线程创建,否则内部的定时器将会失效
        self.image_qt = ImageQt()
        # 壁纸播放定时器
        self.image_play = Timer(0, self.execute)
        self.image_play.daemon = True

    def set_mode(self, value: int):
        """设置播放模式"""
        if value in [IMAGE_CUSTOM_MODE, IMAGE_VIDEO_MODE, IMAGE_KEY_MODE]:
            # 如果模式不一样则设置模式
            if self.image_mode != value:
                self.image_mode = value
                # 如果正在运行则重启
                self.restart()
        else:
            raise TypeError(f'\n{PACK_NAME}.{self.__class__.__name__}.set_mode 错误:输入的值不输入预设模式 {value}')

    def set_api(self):
        """设置壁纸API"""

    def set_time(self, timeout: float | int):
        """设置播放间隔"""
        if isinstance(timeout, (float, int)):
            if self.image_play.is_alive():
                self.image_play.cancel()
            self.image_time = timeout
            # 如果正在运行则重设置定时器
            if self.isRunning:
                self.image_play = Timer(self.image_time, self.execute)
                self.image_play.daemon = True
                self.image_play.start()
        else:
            raise TypeError(f'{PACK_NAME}.{self.__class__.__name__}.set_time 错误:输入不是浮点类型 {timeout}')

    def set_temp_num(self, temp_num: int):
        """设置壁纸缓存数量"""
        self.image_temp_num = temp_num
        self.image_process.set_temp_num(self.image_temp_num)
        # 如果正在运行则重启
        self.restart()

    def add_dir(self):
        """添加用户自定义文件夹"""

    def del_dir(self):
        """删除用户自定义文件夹"""

    def get_image_list(self) -> list:
        """根据配置生成播放列表"""
        if self.image_mode == IMAGE_CUSTOM_MODE:
            if self.image_dir != []:
                image_list = set()
                for image_dir in self.image_dir:
                    image_list.update(
                        file.get_files_path(image_dir, only_file=True, ext=file.IMAGE_EXTENSION)
                    )
                history = set(self.data_manager.get_history())
                self.image_list = list(image_list - history)
                return self.image_list
        elif self.image_mode == IMAGE_KEY_MODE:
            return []

    def execute(self):
        """执行器,从队列中获取图像数据并设置为壁纸"""
        if self.isRunning:
            result = self.image_process.get_image()
            if result is None:
                print(f'{PACK_NAME}.{self.__class__.__name__} 播放队列为空')
                self.image_erro_stop_signal.emit(True)
                self.stop()
                return
            else:
                name, image_progress, image_org = result
            # image.show_image(3000)  # 显示图像
            print(f'壁纸播放:{PACK_NAME}.{self.__class__.__name__}.execute'
                  f'\n名称:{name} 时间{get.now_time()}')
            self.image_play_signal.emit((name, image_org))  # 发送图像名称和图像数据
            if self.image_api == IMAGE_WINDOWS_QT:
                QTimer.singleShot(0, self.image_qt.create)  # 创建桌面窗口
                self.image_qt.set_wallpaper(image_progress)
            elif self.image_api == IMAGE_WINDOWS_API:
                set_wallpaper_API(Image_PIL().open_image(image_progress))
            # 添加到历史数据中
            self.data_manager.add_history(name)
            # 重置定时器
            self.image_play = Timer(self.image_time, self.execute)  # 壁纸播放定时器
            self.image_play.daemon = True
            self.image_play.start()

    def start(self):
        """开始播放"""
        if not self.isRunning:
            if self.image_list == []:
                self.get_image_list()
            self.isRunning = True
            print(f'\n播放开始:'
                  f'\n\t播放列表总长度:{len(self.image_list)}'
                  f'\n\t播放模式:{self.image_mode}'
                  f'\n\t播放间隔:{self.image_time}'
                  f'\n\t播放API:{self.image_api}')

            # 开启历史数据定时保存
            if self.data_manager.auto_save_timer.is_alive():
                self.data_manager.auto_save_timer.start()

            # 创建桌面窗口,实时检测
            if self.image_api == IMAGE_WINDOWS_QT:
                self.image_qt.start()

            # 开启子进程处理图像数据
            self.image_process.set_image_list(self.image_list)
            self.image_process.start()
            self.image_play.start()

    def stop(self):
        """停止播放"""
        if self.isRunning:
            print(f'{PACK_NAME}.{self.__class__.__name__} 正在停止...')
            self.isRunning = False
            # 定时器只有在start()方法后到等待执行的这段时间is_alive的返回值是True
            if self.image_play.is_alive():
                self.image_play.cancel()
                # 重置定时器
                self.image_play = Timer(0, self.execute)  # 壁纸播放定时器
                self.image_play.daemon = True
            self.image_qt.stop()
            self.image_process.stop()
            # 保存历史数据
            self.data_manager.save(IMAGE_HISTORY_PATH, self.data_manager.IMAGE_HISTORY)
            self.data_manager.stop()
            print(f'{PACK_NAME}.{self.__class__.__name__} 已停止。')

    def restart(self):
        if self.isRunning:
            self.stop()
            self.start()

    def save_config(self):
        """保存当前配置"""
        save_config(
            self.image_dir, self.image_time,
            self.image_temp_num, self.image_mode)


if __name__ == '__main__':
    app = QApplication([])
    wallpaper_play = WallPaperPlay()
    wallpaper_play.start()
    app.exec()
