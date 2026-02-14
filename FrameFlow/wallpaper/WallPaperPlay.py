"""壁纸播放主文件"""
from wallpaper.Tools import *


class WallPaperPlay:
    """壁纸播放类"""

    def __init__(self):
        self.isRunning = False  # 是否正在运行
        self.image_mode = IMAGE_CUSTOM_MODE  # 默认为自定义模式
        self.image_api = IMAGE_WINDOWS_API  # 默认为windows系统API
        self.image_time = IMAGE_TIME  # 播放时间间隔
        self.image_dir = IMAGE_DIR  # 用户壁纸文件夹路径
        self.image_queue = Queue(IMAGE_TEMP_NUM)  # 缓冲队列,默认三张
        self.image_process = ImageProcess(self.image_queue)  # 图像处理类
        self.data_manager = DataManager()  # 已播放的历史数据管理
        self.image_list = None  # 播放列表
        self.image_play = Timer(self.image_time, self.execute)  # 壁纸播放定时器
        self.image_play.daemon = True

    def set_mode(self):
        """设置播放模式"""

    def set_api(self):
        """设置壁纸API"""

    def add_dir(self):
        """添加用户自定义文件夹"""

    def del_dir(self):
        """删除用户自定义文件夹"""

    def get_image_list(self):
        """根据配置生成播放列表"""
        if self.image_mode == IMAGE_CUSTOM_MODE:
            if self.image_dir != []:
                image_list = set()
                for image_dir in self.image_dir:
                    image_list.update(
                        file.get_files_path(image_dir, only_file=True, ext=file.IMAGE_EXTENSION)
                    )
                history = set(self.data_manager.get_history())
                self.image_list = image_list - history
                return self.image_list
        elif self.image_mode == IMAGE_KEY_MODE:
            pass

    def execute(self):
        """执行器,从队列中获取图像数据并设置为壁纸"""
        if self.isRunning:
            try:
                image: BytesIO = self.image_queue.get()
            except Empty:
                print(f'{PACK_NAME}.{self.__class__.__name__} 播放队列为空,已停止播放')
                self.isRunning = False

    def start(self):
        """开始播放"""
        if self.image_list is None:
            return False
        self.isRunning = True
        # 开启子进程处理图像数据
        self.image_process.set_image_list(self.image_list)
        self.image_process.start()
        self.image_play.start()

    def stop(self):
        """停止播放"""
        self.isRunning = False
        # 定时器只有在start()方法后到等待执行的这段时间is_alive的返回值是True
        if self.image_play.is_alive():
            self.image_play.cancel()


if __name__ == '__main__':
    wallpaper_play = WallPaperPlay()
    iamge_list = wallpaper_play.get_image_list()
    print(f'总长度{len(iamge_list)}')
