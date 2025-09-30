"""提供简易的照片处理"""
from PIL import Image, ImageFile

from . import file


class Image_PIL:
    def __init__(self, image_path: str):
        self.__image_path = image_path  # 照片路径
        self.__image = self.open_image(image_path)  # ImageFile.ImageFile对象

    @staticmethod
    def ignore_truncation():
        """忽略文件截断"""
        from PIL import ImageFile
        # 允许加载截断的图片文件
        ImageFile.LOAD_TRUNCATED_IMAGES = True

    def open_image(self, image_path: str) -> ImageFile.ImageFile:
        """
        将图片加载为ImageFile对象

        :param image_path:文件绝对路径
        """
        if not file.check_exist(image_path):
            raise FileNotFoundError(f'{image_path}文件不存在')
        if not file.check_image(image_path):
            raise TypeError(f'{image_path}文件不是照片')
        self.__image = Image.open(image_path)
        self.__image_path = image_path
        return self.__image

    @property
    def get_size(self) -> tuple[int, int]:
        # 获取图片的长宽
        width, height = self.__image.size
        return width, height

    @property
    def check_w_screen(self) -> bool:
        """判断照片是否是横屏"""
        width, height = self.get_size  # 获取长宽信息
        if round(width / height, 2) >= 1.0:
            return True
        else:
            return False

    def resize(self, resolution='1920x1080', stretch=False) -> tuple[int, int]:
        """
        将照片按照指定尺寸输出,但照片是竖屏时输出的分辨率宽度只有对应K数的一半
        1K:1920x1080;2k:3840x2160;自定义分辨率使用1920x1080格式
        图像缩放，通过resize()方法来实现
        可用的插值方法包括：
        Image.Resampling.NEAREST：最近邻插值（速度最快，但质量可能较差）。
        Image.Resampling.BILINEAR：双线性插值（速度较快，质量较好）。
        Image.Resampling.BICUBIC：双三次插值（速度较慢，但质量通常最好）。
        Image.Resampling.LANCZOS：Lanczos 插值（需要 PILLOW 额外支持）。

        :param resolution:分辨率
        :param stretch:拉伸
        :return :width,height 返回实际的宽高
        """
        if stretch:  # 拉伸缩放时直接采用指定的分辨率
            width = int(resolution.split('x')[0])
            height = int(resolution.split('x')[1])
        else:  # 非拉伸缩放时竖屏照片修改width,横屏修改height
            # 获取原图像宽高比
            w, h = self.get_size
            AR = w / h
            if self.check_w_screen:
                width = int(resolution.split('x')[0])
                height = int(width * AR)
            else:
                height = int(resolution.split('x')[1])
                width = int(height / AR)
        self.__image = self.__image.resize((width, height), Image.Resampling.LANCZOS)
        return width, height

    def Zip(self, max_size=15, quality=100) -> ImageFile.ImageFile:
        """
        将照片压缩到小于限制(图像尺寸接近max_size且一定下雨max_size)

        :param max_size:照片的最大尺寸MB
        :param quality:保存质量
        """
        import io
        from threading import Thread
        # 获取长宽信息
        width, height = self.get_size
        # 照片的大小
        image_size = file.get_files_size(self.__image_path, unit='MB')
        # 照片的格式
        image_ext = file.get_file_extension(self.__image_path).upper()
        img_byte_arr = io.BytesIO()  # 开辟内存空间类似于物理磁盘可以保存数据
        # 压缩照片大小
        while image_size > max_size:
            # 减少照片的分辨率已达到压缩的目的
            width, height = round(width * 0.9), round(height * 0.9)
            self.__image = self.__image.resize((width, height), Image.Resampling.LANCZOS)  # 压缩算法

            # 保存至内存中
            self.__image.save(img_byte_arr, image_ext, quality=quality)

            # 重新获取内存中self.__image的大小,将指针移动到末尾并获取位置（即数据大小）
            img_byte_arr.seek(0, io.SEEK_END)
            image_size = img_byte_arr.tell() / 1024 / 1024  # MB度量单位
            # 如果照片大小没有满足要求则清空img_byte_arr中的数据
            if image_size > max_size:
                img_byte_arr.truncate(0)  # 清空数据
                img_byte_arr.seek(0)  # 将指针重置到开头


class IMAGE:

    def Merge(self, 拼接对象='self'):
        # 将两张同高度的照片拼接起来
        # image_target.save(file_path, quality=100)
        # file_path为保存的地址,需要带扩展名,如.png,.jpg,.jpeg;quality是质量,降低改值一样能起到减小照片大小的作用
        image_path = 拼接对象
        if image_path == 'self':
            width, height = self.GetSize()  # 获取长宽信息
            image_target = Image.new('RGB', (width * 2, height))
            image_target.paste(self.__image, box=(0, 0))
            image_target.paste(self.__image, box=(width, 0))
            self.__image = image_target
            return self.__image
        else:
            pass

    def SetWallpaperReg(self, image_path=None):
        """
        用于将照片设置为壁纸

        :param image_path:照片路径,不传入时需要使用save()
        默认为类初始化时候的照片地址
        设置成功返回True
        """
        import win32gui, win32con, win32api
        if image_path is None:
            image_path = self.__image_path
        # 打开指定注册表路径
        reg_key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, win32con.KEY_SET_VALUE)
        # 最后的参数:2拉伸,0居中,6适应,10填充,0平铺
        win32api.RegSetValueEx(reg_key, "WallpaperStyle", 0, win32con.REG_SZ, "10")
        # 最后的参数:1表示平铺,拉伸居中等都是0
        win32api.RegSetValueEx(reg_key, "TileWallpaper", 0, win32con.REG_SZ, "0")
        # 刷新桌面与设置壁纸
        win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, image_path, win32con.SPIF_SENDWININICHANGE)
        return True

    def SetWallpaperAPI(self, image_data=None):
        """
        从内存中的图像数据设置Windows壁纸

        :param image_data:内存中的图像数据，可以是PIL Image对象或字节流
        """
        import ctypes, os, tempfile, io
        if image_data is None:
            image_data = self.__image
        # 如果是PIL Image对象，转换为字节流
        if isinstance(image_data, Image.Image):
            img_byte_arr = io.BytesIO()
            # 保存为BMP格式，Windows壁纸最好使用BMP格式
            image_data.save(img_byte_arr, format='BMP')  # 保存为二进制数据流如同保存在物理磁盘上一样
            img_byte_arr = img_byte_arr.getvalue()  # 获取二进制数据,用于网络传输、内存操作
        else:
            img_byte_arr = image_data

        # 创建一个临时文件，关闭后自动删除
        with tempfile.NamedTemporaryFile(suffix='.bmp', delete=False) as temp_file:
            temp_file.write(img_byte_arr)
            temp_path = temp_file.name

        try:
            # 设置壁纸
            SPI_SETDESKWALLPAPER = 20  # 系统操作符
            # 调用Windows API设置壁纸
            ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER,  # 操作标识符,20表示的操作为更改壁纸
                0,  # 动态参数,更改壁纸不需要用到此参数
                temp_path,  # 壁纸路径
                3  # SPIF_UPDATEINIFILE | SPIF_SENDCHANGE 更新方式
                # 如果只使用SPIF_UPDATEINIFILE(值为1)壁纸设置会保存但可能不会立即刷新;
                # 如果只使用 SPIF_SENDCHANGE(值为2)壁纸会立即刷新但可能不会保存到系统配置中。
            )
        finally:
            # 无论是否成功，都删除临时文件
            try:
                os.remove(temp_path)
            except:
                pass

    def Save(self, 保存目录='', 指定格式=None):
        # 将照片保存为指定格式,可以用于照片转换格式
        if 保存目录 == '':
            image_dir = os.path.dirname(self.__image_path)
        else:
            image_dir = 保存目录
        image_name = os.path.basename(self.__image_path)
        if 指定格式 == None:
            指定格式 = os.path.splitext(image_name)[1]
        image_name = os.path.splitext(image_name)[0] + 指定格式
        image_path = os.path.join(image_dir, image_name)
        if os.path.exists(image_path):
            image_path = os.path.join(image_dir, Get.NowTime() + image_name)
        File(image_dir).EnsureExist()
        self.__image.save(image_path, quality=100)
        print(f'IMAGE:图片保存成功{image_path}')
        return image_path
