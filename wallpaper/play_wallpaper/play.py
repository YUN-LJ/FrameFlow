"""壁纸播放模块"""
import pandas as pd
from threading import Thread

from Fun.Norm import image, ini, file
from screeninfo import get_monitors

try:
    from .model import Data
except:
    from model import Data

INI_FILE = f'{Data.TEMP_DIR}/config.ini'


class WallPaper:
    """实现壁纸播放的类"""

    def __init__(self):
        self.__data_state = False  # 数据加载状态
        self.__paly_state = False  # 播放状态,False表示未播放
        self.__screen = str  # 当前屏幕最大尺寸
        self.__row = pd.DataFrame  # 随机获取的一行数据
        self.__image_path = str  # 当前播放的照片路径
        self.__func = None  # 每次切换照片时自动调用
        self.__image = None  # 当前播放的照片的PIL图像对象
        self.__stretch = False  # 处理照片缩放时是否拉伸
        self.__paly_time = 10.0  # 播放间隔时间单位秒
        self.get_max_screen()  # 获取屏幕最大尺寸
        self.__ini = ini.INI(INI_FILE, 'Set')

    def __image_process(self) -> bool:
        """图像处理"""
        try:
            # 获取图像路径
            self.__get_image_path()
            # 打开图像
            self.__image = self.IM.open_image(self.__image_path)
            # 图像拼接
            if not self.IM.check_w_screen:
                self.__image = self.IM.merge()
            # 图像缩放
            self.__image = self.IM.resize(self.screen, stretch=self.__stretch)
            # 图像压缩
            self.__image = self.IM.zip(15)
            return True
        except Exception as e:
            print(f'Wallpaper-image_process错误:\n{e}')
            return False

    def __set_image_wallpaper(self) -> bool:
        """设置壁纸"""
        try:
            image.set_wallpaper_API(self.__image)
            Data.update_state(self.__row)
            Data.save_data()
            return True
        except Exception as e:
            print(f'Wallpaper-set_image_wallpaper错误:\n{e}')
            return False

    def __get_image_path(self):
        """获取图像路径"""
        self.__row = Data.get_random_row()
        self.__image_path = self.__row['所在目录'] + self.__row['子文件路径']
        self.__image_path = self.__image_path.loc[self.__image_path.index[0]]

    def get_max_screen(self) -> str:
        """
        获取最大屏幕分辨率,以宽为准
        返回:1920x1080"""
        # 获取所有屏幕信息
        monitors = get_monitors()
        max_width = 0
        max_height = 0
        for monitor in monitors:
            cur_width = monitor.width
            cur_height = monitor.height
            if cur_width > max_width:
                max_width = cur_width
                max_height = cur_height
        self.screen = f'{max_width}x{max_height}'
        return self.screen

    @property
    def get_dirs_path(self) -> set:
        """获取当前目录"""
        return Data.ALL_DIRS

    @property
    def get_play_time(self) -> float:
        """获取当前播放时间间隔"""
        return self.__paly_time

    def load_data(self):
        """从本地加载数据,如果加载失败则播放,会将播放状态切为False"""
        if file.check_exist(INI_FILE):
            config_values = self.__ini.get_values()
            dir_list = []
            for key, value in config_values.items():
                if key == 'paly_time':
                    self.__paly_time = float(value)
                elif key.isdigit():
                    dir_list.append(value)
            self.add_user_dir(dir_list, False)
        if not Data.load_data():
            print(f'Wallpaper:暂无本地数据!')
            self.__data_state = False
        else:
            self.__data_state = True

    def set_play_time(self, play_time=10.0) -> float:
        """设置播放间隔"""
        self.__paly_time = play_time
        return self.__paly_time

    def set_play_func(self, func):
        """
        设置自动调用函数

        :param func:每播放一张壁纸时自动调用,会传入当然播放的照片路径
        """
        self.__func = func

    def play_wallpaper(self):
        """壁纸播放"""
        import time
        start_time = 0
        while True:
            if self.__paly_state:
                if self.__data_state:  # 如果内存中加载的数据的情况下
                    now = time.time()
                    diff = now - start_time
                    if diff >= self.__paly_time:
                        self.IM = image.Image_PIL()
                        self.IM.LOAD_TRUNCATED_IMAGES = True
                        if self.__image_process():
                            print(f'当前播放:{self.__image_path}\n播放间隔:{diff:.2f}s')
                            self.__set_image_wallpaper()
                            if self.__func is not None:
                                try:
                                    self.__func(self.__image_path)
                                except Exception as e:
                                    print(f'函数{self.__func} 错误:{e}')
                            start_time = now
                        else:
                            start_time = now
                            time.sleep(0.3)
                    else:
                        time.sleep(0.3)
                else:
                    self.update_data()
            else:
                break

    def add_user_dir(self, dir_path: list, update=True) -> bool:
        """添加新的照片路径"""
        if isinstance(dir_path, list):
            for item in dir_path:
                Data.add_image_dir(item)
            if update:
                self.update_data()
            return True
        else:
            raise TypeError(f'"{dir_path}":必须是list类型而不是{type(dir_path)}')

    def del_user_dir(self, dir_path: list, update=True) -> bool:
        Data.del_image_dir(dir_path)
        if update:
            self.update_data()
        return True

    def clear_user_dir(self) -> bool:
        """清空照片路径"""
        Data.clear_image_dir()
        self.__data_state = False

    def update_data(self):
        try:
            Data.get_new_data()
            Data.save_data()
            self.__data_state = True
            return True
        except Exception as e:
            self.__data_state = False
            print(f'Wallpaper-update_data错误:\n{e}')
            return False

    def stop(self):
        """停止播放"""
        self.__paly_state = False

    def run(self, cmd=False):
        """
        执行播放

        :param cmd:cmd模式下运行(主线程会等待全部子线程结束后才会结束)
        """
        self.__paly_state = True
        if cmd:
            Thread(target=self.play_wallpaper).start()
        else:
            Thread(target=self.play_wallpaper, daemon=True).start()

    def save_set(self) -> bool:
        """
        保存当前的配置文件
        """
        try:
            all_dir_path = {'paly_time': self.__paly_time}
            all_dir_path.update({index: item for index, item in enumerate(Data.ALL_DIRS)})
            self.__ini.del_section()
            self.__ini.append_values(all_dir_path)
        except Exception as e:
            print(f'Wallpaper-save_set 错误:\n{e}')


if __name__ == '__main__':
    import time

    start = time.time()
    a = WallPaper()
    # a.add_user_dir(
    #     [r'E:/user_file/Pictures/壁纸/暂时储存/测试'],
    #     update=False)  # 应该有个配置文件保存上次选择的文件夹路径
    a.load_data()  # 加载本地数据
    print(f'加载用时:{time.time() - start}')
    # a.set_play_time(10)  # 设置播放时间
    # a.save_set() # 保存播放间隔时间和选择的文件夹路径
    a.run(True)
    # a.stop()  # 停止播放
