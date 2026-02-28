"""壁纸播放主文件"""
from wallpaper.Tools import *


class WallPaperPlay:
    """
    壁纸播放类
    该类只能在主线程中创建
    """
    Object = []  # 存储了全部的实例化对象,多模块需要共享时使用
    image_play_signal = Signal()  # 壁纸播放时发送当前播放的图像名称和图像数据
    image_info_signal = Signal()  # 关键词模式下发送当前图像的信息pd.DataFrame
    image_erro_stop_signal = Signal()  # 壁纸播放因错误发生导致停止时发送True

    def __init__(self):
        # 类属性
        self.isRunning = False  # 是否正在运行
        self.isPause = False  # 是否暂停
        self.image_mode = IMAGE_CUSTOM_MODE  # 默认为自定义模式,不同的播放模式将影响播放列表
        self.image_api = IMAGE_WINDOWS_QT  # 默认为使用QT作为底层窗口
        self.image_time = IMAGE_TIME  # 播放时间间隔
        self.image_dir = IMAGE_DIR  # 用户壁纸文件夹路径
        self.image_key = []  # wallhaven模块中的收藏夹数据
        self.image_choice_key = IMAGE_CHOICE_KEY  # 选择的关键词
        self.image_temp_num = IMAGE_TEMP_NUM  # 壁纸缓存数量
        self.image_pause_time = time.time()  # 上次暂停的时间,时间戳
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
        self.Object.append(self)

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

    def add_dir(self, image_dir: str):
        """添加用户自定义文件夹"""
        if image_dir not in self.image_dir:
            self.image_dir.append(image_dir)
            self.restart()

    def del_dir(self, image_dir: str):
        """删除用户自定义文件夹"""
        if image_dir in self.image_dir:
            self.image_dir.remove(image_dir)
            self.restart()

    def add_key(self, image_key: str):
        """添加关键词"""
        if image_key not in self.image_choice_key:
            self.image_choice_key.append(image_key)
            self.restart()

    def del_key(self, image_key: str):
        """删除关键词"""
        if image_key in self.image_choice_key:
            self.image_choice_key.remove(image_key)
            self.restart()

    def get_keys(self) -> list[str]:
        """获取全部关键词"""
        if not self.image_key:
            if WallHavenAPI.Object:
                for wallhaven_api in WallHavenAPI.Object:
                    if wallhaven_api.data_manager.isLoad:
                        self.image_key = wallhaven_api.data_manager.KEY_WORD['关键词'].tolist()
            else:
                wallhaven_api = WallHavenAPI()
                if not wallhaven_api.data_manager.isLoad:
                    wallhaven_api.data_manager.load_image_and_key()
                self.image_key = wallhaven_api.data_manager.KEY_WORD['关键词'].tolist()
        return self.image_key

    def get_key_image_list(self, key_word: str) -> pd.DataFrame:
        """获取某个关键词的全部图像数据"""
        if WallHavenAPI.Object:
            for wallhaven_api in WallHavenAPI.Object:
                if wallhaven_api.data_manager.isLoad:
                    with wallhaven_api.data_manager.IMAGE_INFO_LOCK:
                        image_info = wallhaven_api.data_manager.IMAGE_INFO.loc[
                            wallhaven_api.data_manager.IMAGE_INFO['关键词'].str.contains(
                                key_word, case=True, na=False, regex=False)
                        ].copy(deep=True).reset_index()
        else:
            wallhaven_api = WallHavenAPI()
            if not wallhaven_api.data_manager.isLoad:
                wallhaven_api.data_manager.load_image_and_key()
            with wallhaven_api.data_manager.IMAGE_INFO_LOCK:
                image_info = wallhaven_api.data_manager.IMAGE_INFO.loc[
                    wallhaven_api.data_manager.IMAGE_INFO['关键词'].str.contains(
                        key_word, case=True, na=False, regex=False)
                ].copy(deep=True).reset_index()
        return image_info

    def get_image_info(self, image_path: str) -> pd.DataFrame:
        if WallHavenAPI.Object:
            for wallhaven_api in WallHavenAPI.Object:
                if wallhaven_api.data_manager.isLoad:
                    with wallhaven_api.data_manager.IMAGE_INFO_LOCK:
                        image_info = wallhaven_api.data_manager.IMAGE_INFO.loc[
                            wallhaven_api.data_manager.IMAGE_INFO['本地路径'] == image_path
                            ].copy(deep=True).reset_index()
        else:
            wallhaven_api = WallHavenAPI()
            if not wallhaven_api.data_manager.isLoad:
                wallhaven_api.data_manager.load_image_and_key()
            with wallhaven_api.data_manager.IMAGE_INFO_LOCK:
                image_info = wallhaven_api.data_manager.IMAGE_INFO.loc[
                    wallhaven_api.data_manager.IMAGE_INFO['本地路径'] == image_path
                    ].copy(deep=True).reset_index()
        return image_info

    def get_image_list(self) -> list:
        """根据配置生成播放列表"""
        image_list = set()
        history = set(self.data_manager.get_history())
        if self.image_mode == IMAGE_CUSTOM_MODE:
            if self.image_dir:
                for image_dir in self.image_dir:
                    image_list.update(
                        file.get_files_path(
                            image_dir, only_file=True, ext=file.IMAGE_EXTENSION))
        elif self.image_mode == IMAGE_KEY_MODE:
            if self.image_choice_key:
                for image_key in self.image_choice_key:
                    image_list.update(self.get_key_image_list(image_key)['本地路径'].tolist())
        self.image_list = list(image_list - history)
        return self.image_list

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
                image_path, image_progress, image_org = result
                if image_path is None and image_progress is None and image_org is None:
                    print(f'{PACK_NAME}.{self.__class__.__name__} 播放队列播放完成,准备重启')
                    self.data_manager.clear_history()
                    self.restart()
                    return
            # image.show_image(3000)  # 显示图像
            print(f'壁纸播放:{PACK_NAME}.{self.__class__.__name__}.execute'
                  f'\n路径:{image_path} 时间{get.now_time()}')
            # 发送信号
            self.image_play_signal.emit((image_path, image_org))  # 发送图像路径和图像数据
            if self.image_mode == IMAGE_KEY_MODE:
                self.image_info_signal.emit(self.get_image_info(image_path))
            # 设置为壁纸
            if self.image_api == IMAGE_WINDOWS_QT:
                QTimer.singleShot(0, self.image_qt.create)  # 创建桌面窗口
                self.image_qt.set_wallpaper(image_progress)
            elif self.image_api == IMAGE_WINDOWS_API:
                set_wallpaper_API(Image_PIL().open_image(image_progress))
            # 添加到历史数据中
            self.data_manager.add_history(image_path)
            # 重置定时器
            self.image_play = Timer(self.image_time, self.execute)  # 壁纸播放定时器
            self.image_play.daemon = True
            if not self.isPause:
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
            try:
                self.image_play.start()
            except RuntimeError:
                # 重置定时器
                self.image_play = Timer(0, self.execute)  # 壁纸播放定时器
                self.image_play.daemon = True

    def pause(self, pause: bool = True):
        """暂停"""
        if self.isRunning:
            if pause and not self.isPause:
                self.isPause = True
                if self.image_play.is_alive():
                    self.image_play.cancel()
                self.image_pause_time = time.time()
            elif not pause and self.isPause:
                self.isPause = False
                diff_time = time.time() - self.image_pause_time  # 暂停了多久
                interval = min(abs(self.image_time - diff_time), self.image_time)
                self.image_play = Timer(interval, self.execute)  # 壁纸播放定时器
                self.image_play.daemon = True
                self.image_play.start()

    def stop(self):
        """停止播放"""
        if self.isRunning:
            print(f'{PACK_NAME}.{self.__class__.__name__} 正在停止...')
            self.isRunning = False
            self.image_list = []  # 重置播放列表
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
            self.image_dir, self.image_choice_key, self.image_time,
            self.image_temp_num, self.image_mode)


if __name__ == '__main__':
    app = QApplication([])
    wallpaper_play = WallPaperPlay()
    wallpaper_play.start()
    app.exec()
