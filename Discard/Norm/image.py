from PIL import Image, ImageFile
from Fun.BaseTools import Get


class Image_PIL:
    """图像处理类,基于PIL库封装"""
    # 是否允许加载截断的图片文件,默认为不允许
    LOAD_TRUNCATED_IMAGES = False

    def __init__(self, image_path: str | BytesIO | np.ndarray = None, load_trunc_images: bool = False):
        self.__image_path = image_path  # 照片路径
        if load_trunc_images:
            self.LOAD_TRUNCATED_IMAGES = True
        if image_path is not None:
            self.__image = self.open_image(image_path)  # ImageFileBase.ImageFile对象

    def open_image(self, image_input: str | BytesIO | np.ndarray) -> ImageFile.ImageFile | bool:
        """
        将图片加载为ImageFile对象

        :param image_input:输入的图像
        :ruturn :图像不完整时会返回Flase,如果开启允许加载截断则会忽略图像完整性检查
        """
        # 允许加载截断图像
        ImageFile.LOAD_TRUNCATED_IMAGES = self.LOAD_TRUNCATED_IMAGES
        if isinstance(image_input, str):
            if not FileBase(image_input).exists:
                raise FileNotFoundError(f'{image_input}文件不存在')
            if not FileBase(image_input).is_image:
                raise TypeError(f'{image_input}文件不是照片')
            self.__image = Image.open(image_input)
            self.__image_path = image_input
        elif isinstance(image_input, np.ndarray):
            self.__image = Image.fromarray(image_input)
        elif isinstance(image_input, BytesIO):
            self.__image = Image.open(image_input)
        return self.__image

    @property
    def check_w_screen(self) -> bool:
        """判断照片是否是横屏,横屏返回True,竖屏返回False"""
        width, height = self.get_size  # 获取长宽信息
        if round(width / height, 2) >= 1.0:
            return True
        else:
            return False

    @property
    def check_image(self) -> bool:
        """检查图像是否完整"""
        try:
            self.__image.load()
            return True
        except IOError:
            return False

    @property
    def get_size(self) -> tuple[int, int]:
        # 获取图片的长宽
        width, height = self.__image.size
        return width, height

    @property
    def get_array(self) -> np.ndarray:
        """转为数组类型,RGB颜色通道"""
        return np.array(self.__image)

    @property
    def get_cv2(self) -> np.ndarray:
        """转为cv2形式的图像"""
        return cv2.cvtColor(self.get_array, cv2.COLOR_RGB2BGR)

    @property
    def get_BytesIO(self) -> BytesIO:
        """转为BytesIO类型的图像"""
        image = BytesIO()
        self.__image.save(image, format='PNG')
        return image

    @property
    def get_PIL(self) -> ImageFile.ImageFile:
        return self.__image

    def copy(self) -> ImageFile.ImageFile:
        return self.__image.copy()

    def resize(self, size: tuple[int, int], stretch: str = ImageEnum.resize_auto,
               resample=Image.Resampling.LANCZOS) -> tuple[int, int]:
        """
        将照片按照指定尺寸输出
        图像缩放，通过resize()方法来实现
        可用的插值方法包括：
        Image.Resampling.NEAREST：最近邻插值（速度最快，低精度场景（无抗锯齿））。
        Image.Resampling.BILINEAR：双线性插值（速度较快，边缘略模糊）。
        Image.Resampling.BICUBIC：双三次插值（速度较慢，常规高质量缩放（比 BILINEAR 清晰））。
        Image.Resampling.LANCZOS：Lanczos 插值（纹理清晰、抗锯齿优秀）。
        Image.Resampling.BOX：平均池化缩放（适合缩小图像）

        :param size:缩放到的目标尺寸(w,h)
        :param stretch:缩放方式,默认按照最接近目标分辨率的尺寸进行缩放,即宽更接近则按照宽为目标分辨率,高保存比例
                       其余可选值:
                       拉伸:强制分辨率与目标值一致
                       填充:默认值上对不足目标分辨率的一边进行平均色填充
                       剪裁:进行中心裁剪确保尺寸与目标分别率一致

        :param resample:缩放插值方法
        :return :w,h 返回实际的宽高
        """

        def auto_size():
            """自动计算宽高缩放,保持比例"""
            diff_width = abs(size[0] - original_width)
            diff_height = abs(size[1] - original_height)
            if diff_width > diff_height:  # 按高度缩放
                height = size[1]
                width = int(scale * height)
            else:  # 按宽度缩放
                width = size[0]
                height = int(width / scale)
            return width, height

        # 计算原图宽高比
        original_width, original_height = self.get_size
        scale = original_width / original_height
        if stretch == ImageEnum.resize_auto:  # 自动计算图像宽高最接近目标分辨率的一条
            width, height = auto_size()
            self.__image = self.__image.resize((width, height), resample)
        elif stretch == ImageEnum.resize_fill:  # 填充
            width, height = auto_size()
            # 创建一个目标尺寸画布
            value = self.get_array.mean(axis=(0, 1)).astype(int)  # 计算图像的每个通道的平均值
            canvas = Image.new('RGB', size, tuple(value))
            canvas.paste(self.__image.resize((width, height), resample),
                         ((size[0] - width) // 2, (size[1] - height) // 2))
            self.__image = canvas
        elif stretch == ImageEnum.resize_stretch:  # 拉伸
            width, height = size
            self.__image = self.__image.resize((width, height), resample)
        elif stretch == ImageEnum.resize_cut:  # 中心裁剪
            target_width, target_height = size
            img_width, img_height = self.get_size
            # 计算缩放比例
            width_ratio = target_width / img_width
            height_ratio = target_height / img_height
            # 使用较大的比例，确保裁剪后能覆盖目标区域
            scale = max(width_ratio, height_ratio)
            # 计算缩放后的尺寸
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            # 缩放图像
            img_resized = self.__image.resize((new_width, new_height), resample)
            # 计算裁剪区域（中心裁剪）
            left = (new_width - target_width) // 2
            top = (new_height - target_height) // 2
            right = left + target_width
            bottom = top + target_height
            # 执行裁剪
            self.__image = img_resized.crop((left, top, right, bottom))
            width, height = self.get_size
        return width, height

    def zip(self, max_size=15, quality=100) -> ImageFile.ImageFile:
        """
        将照片压缩到小于限制(图像尺寸接近max_size且一定小于max_size)

        :param max_size:照片的最大尺寸MB
        :param quality:保存质量
        """
        import io
        # 获取长宽信息
        width, height = self.get_size
        # 照片的格式
        img_byte_arr = io.BytesIO()  # 开辟内存空间类似于物理磁盘可以保存数据
        # 保存至内存中
        self.__image.save(img_byte_arr, 'PNG', quality=quality)
        # 照片的大小
        img_byte_arr.seek(0, io.SEEK_END)
        image_size = img_byte_arr.tell() / 1024 / 1024  # MB度量单位
        if image_size <= max_size:
            return self.__image
        # 使用数学公式直接计算需要缩放的比例
        target_pixels = (width * height) * (max_size / image_size)
        # 计算新的尺寸（保持宽高比）
        scale_factor = math.sqrt(target_pixels / (width * height))
        new_width = max(int(width * scale_factor * 0.95), 1)  # 稍微保守一点
        new_height = max(int(height * scale_factor * 0.95), 1)
        # 调整到目标尺寸
        self.__image = self.__image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS)
        # 验证并微调（最多2次迭代）
        for _ in range(2):
            img_byte_arr.truncate(0)  # 清空数据
            img_byte_arr.seek(0)  # 将指针重置到开头
            self.__image.save(img_byte_arr, 'JPEG', quality=quality)
            image_size = img_byte_arr.tell() / (1024 * 1024)
            if image_size <= max_size:
                break
            # 需要进一步缩小
            scale_factor = math.sqrt(max_size / image_size)
            new_width = max(int(new_width * scale_factor * 0.95), 1)
            new_height = max(int(new_height * scale_factor * 0.95), 1)
            self.__image = self.__image.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )
        return self.__image

    def merge(self, other_half: str = 'self', num: int = 1, w=True):
        """
        将两张照片拼接起来

        :param other_half:另一张照片的路径,如果是self则是自我拼接
        :param num:拼接几份
        :param w: 沿w方向拼接
        """
        # 将两张同高度的照片拼接起来
        image_path = other_half
        if image_path == 'self':
            width, height = self.get_size  # 获取长宽信息
            if w:
                image_target = Image.new('RGB', (width * (num + 1), height))
                for i in range(num + 1):
                    image_target.paste(self.__image, box=(i * width, 0))
                self.__image = image_target
                return self.__image
            else:
                image_target = Image.new('RGB', (width, height * (num + 1)))
                for i in range(num + 1):
                    image_target.paste(self.__image, box=(0, i * height))
                self.__image = image_target
                return self.__image
        else:
            pass

    def close_image(self):
        """关闭图像"""
        self.__image.close()

    def show_image(self, time_out=0):
        """显示图像,指定显示时间,默认为无限等待,单位为ms"""
        cv2.imshow(os.path.basename(self.__image_path), self.get_cv2)
        cv2.waitKey(time_out)

    def save(self, target_path='', ext='', quality=100) -> bool:
        """
        将照片保存为指定格式,可以用于照片转换格式

        :param target_path:保存路径,不指定时默认保存为原照片所在文件夹
        :param ext:扩展名,如.png,不指定时默认为原扩展名
        :param quality:保存质量
        """
        if target_path == '':
            target_path = FileBase(self.__image_path).dir_name
        image_name = FileBase(self.__image_path).name_base
        if ext == '':
            ext = FileBase(self.__image_path).extension
        FileBase(target_path).ensure_exists()
        now_time = Get.now_time()
        image_name += f'_{now_time}{ext}'
        target_path += f'\\{image_name}'
        if FileBase(target_path).is_image:
            self.__image.save(target_path, quality=quality)
            return True
        else:
            raise TypeError(f'目标路径不是图像格式{target_path}')