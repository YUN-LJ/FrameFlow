"""图像处理包"""
import cv2, os, math
import numpy as np
from io import BytesIO
from typing import Optional
from Fun.BaseTools import FileBase
from PySide6.QtGui import QPixmap, QImage


class ImageEnum:
    """图像处理类的枚举值"""
    resize_auto = '自动'
    resize_fill = '填充'
    resize_stretch = '拉伸'
    resize_cut = '剪裁'  # 自适应中心裁剪
    # 各种插值方法
    interpolation_auto = '自动'  # 自动选择适合的缩放插值方法
    INTER_NEAREST = cv2.INTER_NEAREST,  # 最近邻插值（最快，质量最差）
    INTER_LINEAR = cv2.INTER_LINEAR,  # 双线性插值（默认，速度快）
    INTER_AREA = cv2.INTER_AREA,  # 像素区域关系（缩小效果最好）
    INTER_CUBIC = cv2.INTER_CUBIC,  # 双三次插值（放大效果好，慢）
    INTER_LANCZOS4 = cv2.INTER_LANCZOS4  # Lanczos插值（质量最好，最慢）


class ImageLoad:
    """
    通过cv2实现的图像加载管理
    image属性为BGR通道值,赋值时必须保证为BGR顺序的数组
    """

    def __init__(self, image: str | BytesIO | np.ndarray):
        """
        :param image:图像数据
        """
        self.image = self.__load_image(image)

    def set_image(self, image: str | BytesIO | np.ndarray):
        """设置图像数据"""
        self.image = self.__load_image(image)

    def __load_image(self, image: str | BytesIO | np.ndarray | bytes) -> np.ndarray:
        """加载图像，支持多种输入格式"""

        # 1. numpy数组
        if isinstance(image, np.ndarray):
            return self._normalize_array(image)

        # 2. 文件路径
        elif isinstance(image, str):
            return self._load_from_path(image)

        # 3. BytesIO
        elif isinstance(image, BytesIO):
            return self._load_from_bytesio(image)

        # 4. bytes
        elif isinstance(image, bytes):
            return self._load_from_bytes(image)

        # 5. PIL Image
        elif 'PIL' in str(type(image)):
            return self._load_from_pil(image)

        else:
            raise TypeError(f"不支持的图像类型: {type(image)}")

    def _normalize_array(self, img: np.ndarray) -> np.ndarray:
        """标准化numpy数组格式，统一转换为OpenCV默认格式（BGR/BGRA）"""
        if len(img.shape) == 2:  # 灰度图
            return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif len(img.shape) == 3:
            channels = img.shape[2]
            if channels == 3:
                # 假设是RGB格式（常见情况），转换为BGR
                # 注意：无法自动判断是RGB还是BGR，默认按RGB处理
                return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            elif channels == 4:
                # 假设是RGBA格式，转换为BGRA
                return cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA)
        return img

    def _load_from_path(self, path: str) -> np.ndarray:
        """从文件路径加载（支持中文路径）"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"图像文件不存在: {path}")
        # 使用 numpy 从文件读取（推荐）
        try:
            with open(path, 'rb') as f:
                file_bytes = np.frombuffer(f.read(), np.uint8)
                img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError(f"无法读取图像文件: {path}")
            return img
        except Exception as e:
            raise ValueError(f"读取图像文件失败: {path}\n错误: {e}")

    def _load_from_bytesio(self, bytesio: BytesIO) -> np.ndarray:
        """从BytesIO加载"""
        bytesio.seek(0)
        file_bytes = np.frombuffer(bytesio.getvalue(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("无法从BytesIO解码图像")
        return img

    def _load_from_bytes(self, data: bytes) -> np.ndarray:
        """从bytes加载"""
        file_bytes = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("无法从bytes解码图像")
        return img

    def _load_from_pil(self, pil_image) -> np.ndarray:
        """从PIL Image加载"""
        # PIL使用RGB，需要转换为BGR
        import numpy as np
        rgb = np.array(pil_image.convert('RGB'))
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    @property
    def shape(self) -> tuple:
        """获取图像尺寸 (height, width, channels)"""
        return self.image.shape

    @property
    def height(self) -> int:
        """图像高度"""
        return self.image.shape[0]

    @property
    def width(self) -> int:
        """图像宽度"""
        return self.image.shape[1]

    @property
    def channels(self) -> int:
        """图像通道数"""
        return self.image.shape[2] if len(self.image.shape) == 3 else 1

    @property
    def size_mb(self) -> float:
        """图像内存占用(MB)"""
        return self.image.nbytes / (1024 * 1024)

    @property
    def dtype(self) -> np.dtype:
        """图像数据类型"""
        return self.image.dtype

    @property
    def is_vertical(self) -> bool:
        """判断照片是否是竖屏"""
        if round(self.height / self.width, 2) >= 1.0:
            return True
        else:
            return False

    def info(self) -> dict:
        """获取图像详细信息"""
        return {
            'shape': self.shape,
            'height': self.height,
            'width': self.width,
            'channels': self.channels,
            'dtype': str(self.dtype),
            'memory_mb': self.size_mb,
            'min_value': float(self.image.min()),
            'max_value': float(self.image.max()),
            'mean_value': float(self.image.mean())
        }

    def show(self, title: str = "Image"):
        """显示图像"""
        from Fun.QtWidget.FWidget import ImageWidget
        image_widget = ImageWidget(self)
        image_widget.setWindowTitle(title)
        image_widget.enable_zoom_and_drag()
        image_widget.show()

    def save(self, path: str, quality: int = 100):
        """保存图像"""
        cv2.imwrite(path, self.image, [cv2.IMWRITE_JPEG_QUALITY, quality])

    def get_bytesIO(self, format: str = '.jpg', quality: int = 100) -> BytesIO:
        """获取BytesIO对象"""
        success, encoded = cv2.imencode(format, self.image, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if not success:
            raise RuntimeError("图像编码失败")
        return BytesIO(encoded.tobytes())

    def get_array(self) -> np.ndarray:
        return cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

    def get_qpixmap(self) -> QPixmap:
        """将图像转为Qt可显示的图像"""
        try:
            # 检查原始图像是否有 Alpha 通道
            if len(self.image.shape) == 3 and self.image.shape[2] == 4:
                # 保持 Alpha 通道，将 BGRA 转换为 RGBA
                rgba_array = cv2.cvtColor(self.image, cv2.COLOR_BGRA2RGBA)
                h, w, c = rgba_array.shape
                bytes_per_line = w * c
                qimage = QImage(rgba_array.data, w, h, bytes_per_line, QImage.Format_RGBA8888)
            else:
                # 普通图片，转换为 RGB
                array = self.get_array()  # BGR -> RGB
                h, w, c = array.shape
                bytes_per_line = w * c
                format_ = QImage.Format_RGB888 if c == 3 else QImage.Format_RGBA8888
                qimage = QImage(array.data, w, h, bytes_per_line, format_)
            return QPixmap.fromImage(qimage)
        except Exception as e:
            print(f"转换为 QPixmap 失败: {e}")
            # 返回一个透明的默认图片
            default_array = np.full((224, 224, 4), fill_value=0, dtype=np.uint8)
            h, w, c = default_array.shape
            bytes_per_line = w * c
            qimage = QImage(default_array.data, w, h, bytes_per_line, QImage.Format_RGBA8888)
            return QPixmap.fromImage(qimage)

    def get_qimage(self) -> QImage:
        """
        将图像转为Qt的QImage对象（不进行QPixmap包装）
        返回的QImage共享内存数据，请确保ImageLoad实例生命周期长于QImage的使用
        """
        try:
            h, w = self.height, self.width
            if self.channels == 4:
                # BGRA -> RGBA
                rgba_array = cv2.cvtColor(self.image, cv2.COLOR_BGRA2RGBA)
                bytes_per_line = w * 4
                return QImage(rgba_array.data, w, h, bytes_per_line, QImage.Format_RGBA8888)
            else:
                # BGR -> RGB
                rgb_array = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                bytes_per_line = w * 3
                return QImage(rgb_array.data, w, h, bytes_per_line, QImage.Format_RGB888)
        except Exception as e:
            print(f"转换为 QImage 失败: {e}")
            # 返回默认透明图像
            default_array = np.full((224, 224, 4), fill_value=0, dtype=np.uint8)
            h, w, c = default_array.shape
            bytes_per_line = w * c
            return QImage(default_array.data, w, h, bytes_per_line, QImage.Format_RGBA8888)

class ImageProcess:
    """图像处理类"""

    def __init__(self, image: ImageLoad):
        self.__image = image

    # ----图像缩放----
    def resize(self, size: tuple[int, int], stretch: str = ImageEnum.resize_auto,
               interpolation=ImageEnum.interpolation_auto,
               bg_color: tuple[int, int, int] = None) -> Optional['ImageProcess']:
        """
        将照片缩放到目标尺寸

        :param size:缩放到的目标尺寸(w,h)
        :param stretch:缩放方式,默认按照最接近目标分辨率的尺寸进行缩放,即宽更接近则按照宽为目标分辨率,高保持比例
                       其余可选值:
                       拉伸:强制分辨率与目标值一致
                       填充:默认值上对不足目标分辨率的一边进行平均色填充
                       剪裁:进行中心裁剪确保尺寸与目标分别率一致
        :param interpolation:插值方法
        :param bg_color:填充模式的背景颜色（BGR格式），默认None则自动计算图片边缘平均色
        :return: 返回自身支持链式调用
        """
        if self.__image.image is None:
            raise ValueError("图像未加载")

        target_w, target_h = size
        h, w = self.__image.image.shape[:2]

        # 处理插值方法
        if interpolation == ImageEnum.interpolation_auto:
            if target_w < w or target_h < h:
                interp = cv2.INTER_AREA  # 缩小
            else:
                interp = cv2.INTER_CUBIC  # 放大
        else:
            interp = interpolation[0] if isinstance(interpolation, tuple) else interpolation

        # 如果没有指定填充色，自动计算
        if bg_color is None and stretch == ImageEnum.resize_fill:
            bg_color = self._calculate_edge_average_color()

        # 处理缩放模式
        try:
            if stretch == ImageEnum.resize_stretch:
                self._resize_stretch(target_w, target_h, interp)
            elif stretch == ImageEnum.resize_fill:
                self._resize_fill(target_w, target_h, interp, bg_color)
            elif stretch == ImageEnum.resize_cut:
                self._resize_cut(target_w, target_h, interp)
            else:  # auto
                self._resize_auto(target_w, target_h, interp)

            return self

        except Exception as e:
            raise RuntimeError(f"图像缩放失败: {e}")

    def _calculate_edge_average_color(self) -> tuple[int, int, int]:
        """
        计算全图像的各通道平均值
        用于填充模式，使过渡更自然
        """
        img = self.__image.image
        # 计算BGR三个通道的平均值
        avg_color = np.mean(img, axis=(0, 1)).astype(np.uint8)
        return (int(avg_color[0]), int(avg_color[1]), int(avg_color[2]))

    def _resize_fill(self, target_w: int, target_h: int, interp: int, bg_color: tuple):
        """填充模式"""
        h, w = self.__image.image.shape[:2]
        ratio = min(target_w / w, target_h / h)
        new_w, new_h = int(w * ratio), int(h * ratio)

        # 缩放
        resized = cv2.resize(self.__image.image, (new_w, new_h), interpolation=interp)

        # 如果未提供填充色，使用边缘平均色
        if bg_color is None:
            bg_color = self._calculate_edge_average_color()

        # 创建背景
        if len(self.__image.image.shape) == 3:
            channels = self.__image.image.shape[2]
            canvas = np.full((target_h, target_w, channels), bg_color, dtype=np.uint8)
        else:
            # 灰度图处理
            bg_gray = bg_color[0] if isinstance(bg_color, tuple) else bg_color
            canvas = np.full((target_h, target_w), bg_gray, dtype=np.uint8)

        # 居中放置
        x_offset = (target_w - new_w) // 2
        y_offset = (target_h - new_h) // 2
        canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized

        self.__image.image = canvas

    def _resize_stretch(self, target_w: int, target_h: int, interp: int):
        """拉伸模式"""
        self.__image.image = cv2.resize(self.__image.image, (target_w, target_h),
                                        interpolation=interp)

    def _resize_cut(self, target_w: int, target_h: int, interp: int):
        """裁剪模式"""
        h, w = self.__image.image.shape[:2]
        ratio = max(target_w / w, target_h / h)
        new_w, new_h = int(w * ratio), int(h * ratio)

        # 缩放
        resized = cv2.resize(self.__image.image, (new_w, new_h), interpolation=interp)

        # 中心裁剪
        x_start = (new_w - target_w) // 2
        y_start = (new_h - target_h) // 2

        # 确保边界有效
        x_start = max(0, min(x_start, new_w - target_w))
        y_start = max(0, min(y_start, new_h - target_h))

        self.__image.image = resized[y_start:y_start + target_h, x_start:x_start + target_w]

    def _resize_auto(self, target_w: int, target_h: int, interp: int):
        """自动模式"""
        h, w = self.__image.image.shape[:2]
        target_ratio = target_w / target_h
        current_ratio = w / h

        if current_ratio > target_ratio:
            # 图像更宽，以高度为基准
            new_h = target_h
            new_w = int(w * (target_h / h))
        else:
            # 图像更高，以宽度为基准
            new_w = target_w
            new_h = int(h * (target_w / w))

        # 缩放
        self.__image.image = cv2.resize(self.__image.image, (new_w, new_h), interpolation=interp)

    # ----图像压缩----
    def zip(self, max_size: float = 15, quality: int = 100, format: str = '.jpg') -> Optional['ImageProcess']:
        """
        将照片压缩到小于限制(图像尺寸接近max_size且一定小于max_size)

        :param max_size:照片的最大尺寸MB
        :param quality:保存质量(1-100)，仅对JPEG格式有效
        :param format:目标格式，支持 '.jpg' 或 '.png'
        :return: 返回自身支持链式调用
        """
        if self.__image.image is None:
            raise ValueError("图像未加载")

        # 获取图像尺寸
        h, w = self.__image.image.shape[:2]

        # 测试当前图像大小
        img_byte_arr = BytesIO()

        # 根据格式选择编码方式
        if format.lower() in ['.jpg', '.jpeg', 'jpg', 'jpeg']:
            success, encoded = cv2.imencode('.jpg', self.__image.image,
                                            [cv2.IMWRITE_JPEG_QUALITY, quality])
            use_jpeg = True
        else:  # PNG格式
            success, encoded = cv2.imencode('.png', self.__image.image,
                                            [cv2.IMWRITE_PNG_COMPRESSION, 9])  # 最高压缩率
            use_jpeg = False

        if not success:
            raise RuntimeError("图像编码失败")

        img_byte_arr.write(encoded.tobytes())
        img_byte_arr.seek(0, 2)  # 移动到末尾
        image_size = img_byte_arr.tell() / (1024 * 1024)  # MB

        # 如果已经满足要求，直接返回
        if image_size <= max_size:
            return self

        # 计算需要的像素数量
        target_pixels = (w * h) * (max_size / image_size)

        # 计算新的尺寸（保持宽高比）
        scale_factor = math.sqrt(target_pixels / (w * h))
        new_width = max(int(w * scale_factor * 0.95), 1)  # 稍微保守一点
        new_height = max(int(h * scale_factor * 0.95), 1)

        # 使用内部resize方法调整到目标尺寸
        self.resize(size=(new_width, new_height), stretch=ImageEnum.resize_stretch)
        # 验证并微调（最多3次迭代）
        max_iterations = 3
        for iteration in range(max_iterations):
            # 测试新的大小
            img_byte_arr = BytesIO()
            if use_jpeg:
                success, encoded = cv2.imencode('.jpg', self.__image.image,
                                                [cv2.IMWRITE_JPEG_QUALITY, quality])
            else:
                # PNG可以调整压缩级别
                compression_level = min(9, 3 + iteration * 2)  # 逐渐增加压缩级别
                success, encoded = cv2.imencode('.png', self.__image.image,
                                                [cv2.IMWRITE_PNG_COMPRESSION, compression_level])

            if not success:
                raise RuntimeError("图像编码失败")
            img_byte_arr.write(encoded.tobytes())
            img_byte_arr.seek(0, 2)
            image_size = img_byte_arr.tell() / (1024 * 1024)
            if image_size <= max_size:
                # 如果是JPEG，需要重新解码以应用压缩效果
                if use_jpeg:
                    img_byte_arr.seek(0)
                    file_bytes = np.frombuffer(img_byte_arr.getvalue(), np.uint8)
                    self.__image.image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                break
            # 需要进一步缩小
            h, w = self.__image.image.shape[:2]
            scale_factor = math.sqrt(max_size / image_size)
            new_width = max(int(w * scale_factor * 0.95), 1)
            new_height = max(int(h * scale_factor * 0.95), 1)
            # 使用内部resize方法
            self.resize(size=(new_width, new_height), stretch=ImageEnum.resize_stretch)
        # 最终确保如果是JPEG目标，图像已经应用了压缩
        if use_jpeg and self.__image.size_mb > max_size:
            # 最后一次强制压缩
            img_byte_arr = BytesIO()
            success, encoded = cv2.imencode('.jpg', self.__image.image,
                                            [cv2.IMWRITE_JPEG_QUALITY, quality])
            if success:
                img_byte_arr.write(encoded.tobytes())
                img_byte_arr.seek(0)
                file_bytes = np.frombuffer(img_byte_arr.getvalue(), np.uint8)
                self.__image.image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        return self

    # ----图像拼接----
    def merge(self, other_half: str = 'self', num: int = 1, w: bool = True) -> Optional['ImageProcess']:
        """
        将两张照片拼接起来

        :param other_half:另一张照片的路径或ImageLoad对象，如果是'self'则是自我拼接
        :param num:拼接几份（当other_half='self'时有效）
        :param w: True表示水平拼接，False表示垂直拼接
        :return: 返回自身支持链式调用
        """
        if self.__image.image is None:
            raise ValueError("图像未加载")

        # 获取当前图像尺寸
        h, w_img = self.__image.image.shape[:2]

        # 自我拼接
        if other_half == 'self':
            if w:
                # 水平拼接
                target = np.zeros((h, w_img * (num + 1), 3), dtype=np.uint8)
                for i in range(num + 1):
                    target[:, i * w_img:(i + 1) * w_img] = self.__image.image
                self.__image.image = target
            else:
                # 垂直拼接
                target = np.zeros((h * (num + 1), w_img, 3), dtype=np.uint8)
                for i in range(num + 1):
                    target[i * h:(i + 1) * h, :] = self.__image.image
                self.__image.image = target

        # 与另一张图片拼接
        else:
            # 加载另一张图片
            if isinstance(other_half, str):
                other_image_load = ImageLoad(other_half)
                other_img = other_image_load.image
            elif isinstance(other_half, ImageLoad):
                other_img = other_half.image
            elif isinstance(other_half, np.ndarray):
                other_img = other_half
            else:
                raise TypeError(f"不支持的other_half类型: {type(other_half)}")

            h_other, w_other = other_img.shape[:2]

            if w:
                # 水平拼接
                if h != h_other:
                    # 高度不同，需要调整
                    target_h = max(h, h_other)
                    # 调整当前图像
                    if h < target_h:
                        self.resize(size=(w_img, target_h), stretch=ImageEnum.resize_fill)
                    # 调整另一张图片
                    if h_other < target_h:
                        other_img_resized = cv2.resize(other_img, (w_other, target_h))
                        # 创建临时ImageProcess处理
                        temp_load = ImageLoad(other_img_resized)
                        temp_process = ImageProcess(temp_load)
                        temp_process.resize(size=(w_other, target_h), stretch=ImageEnum.resize_fill)
                        other_img = temp_load.image

                    h = target_h

                # 拼接
                target = np.hstack((self.__image.image, other_img))
                self.__image.image = target
            else:
                # 垂直拼接
                if w_img != w_other:
                    # 宽度不同，需要调整
                    target_w = max(w_img, w_other)
                    # 调整当前图像
                    if w_img < target_w:
                        self.resize(size=(target_w, h), stretch=ImageEnum.resize_fill)
                    # 调整另一张图片
                    if w_other < target_w:
                        other_img_resized = cv2.resize(other_img, (target_w, h_other))
                        temp_load = ImageLoad(other_img_resized)
                        temp_process = ImageProcess(temp_load)
                        temp_process.resize(size=(target_w, h_other), stretch=ImageEnum.resize_fill)
                        other_img = temp_load.image

                    w_img = target_w

                # 拼接
                target = np.vstack((self.__image.image, other_img))
                self.__image.image = target

        return self


def set_wallpaper_reg(image_path: str) -> bool:
    """
    用于将照片设置为壁纸

    :param image_path:照片路径,不传入时需要使用save()
    设置成功返回True
    """
    if not FileBase(image_path).is_image:
        raise TypeError(f'文件不是图像格式{image_path}')
    import win32gui, win32con, win32api
    # 打开指定注册表路径
    reg_key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, win32con.KEY_SET_VALUE)
    # 最后的参数:2拉伸,0居中,6适应,10填充,0平铺
    win32api.RegSetValueEx(reg_key, "WallpaperStyle", 0, win32con.REG_SZ, "10")
    # 最后的参数:1表示平铺,拉伸居中等都是0
    win32api.RegSetValueEx(reg_key, "TileWallpaper", 0, win32con.REG_SZ, "0")
    # 刷新桌面与设置壁纸
    win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, image_path, win32con.SPIF_SENDWININICHANGE)
    return True


def set_wallpaper_API(image_data) -> bool:
    """
    从内存中的图像数据设置Windows壁纸

    :param image_data:内存中的图像数据，可以是PIL Image对象或字节流
    """
    import ctypes, os, tempfile, io
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
    return True


if __name__ == '__main__':
    image_path = FileBase(r"E:\user_file\Pictures\壁纸\wallhaven\限制级\人物\1k2zmv.png")
    image = ImageLoad(image_path.path)
    print(f"图片大小: {image.size_mb} MB")
    image.show()
