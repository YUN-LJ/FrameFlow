"""
有关PySide6类的高级封装操作
"""
import os, numpy as np, cv2
from io import BytesIO
from Fun.Norm import get
import win32gui, win32con
from screeninfo import get_monitors

from PySide6.QtCore import Qt, QRect, QPoint, QEvent
from PySide6.QtGui import (QWindow, QAction, QIcon, QShortcut, QScreen,
                           QPixmap, QPainter, QPaintEvent,
                           QImage, QWheelEvent, QMouseEvent)
from PySide6.QtWidgets import (
    QFileDialog, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QSystemTrayIcon, QMenu, QApplication
)


def get_exist_dir(caption: str = '选择文件夹', dir_path: str = get.run_dir()) -> str:
    """
    用于选择单个目录,外部调用时需要用lambda :方法

    :param caption:窗口标题
    :param dir_path:初始目录,默认为文件启动路径
    :return dir:str
    """
    dir = QFileDialog.getExistingDirectory(parent=None,  # 父对象
                                           caption=caption,  # 对话框标题提示词
                                           dir=dir_path,  # 默认显示目录
                                           options=QFileDialog.ShowDirsOnly  # 只显示文件夹
                                           )
    return dir


def get_exist_files(caption: str = '', dir_path: str = get.run_dir(), ext=None) -> list[str]:
    """
    用于选择单个文件,外部调用时需要用lambda :方法
    :param caption:窗口标题
    :param dir_path:初始目录,默认为文件启动路径
    :param ext:设置文件的扩展名
    :return file:list[str]
    """
    # ext="视频(*.mp4;*.wmv;*.flv;*.avi);;文本(*.txt);;All file(*)"
    file, _ = QFileDialog.getOpenFileNames(None,  # 父对象
                                           caption,  # 窗口标题
                                           dir_path,  # 默认启动路径
                                           ext  # 选择格式
                                           )
    return file


def embed_qt(target_inf: str | int, widget: QWidget, class_name: list[str] = None, accurate: bool = True) -> int:
    """
    将窗口嵌入到Pyside6窗口中
    需要外部窗口随着pyside6一同关闭需要重写closeEvent
    def closeEvent(self, event):
        # 发送关闭消息给外部窗口（Windows API）
        if self.hwnd:
            import win32gui,win32con
            # WM_CLOSE 消息：通知窗口关闭
            win32gui.SendMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)
        super().closeEvent(event)  # 继续执行 Qt 窗口的关闭逻辑

    :param target_inf:查找的窗口标题str或进程pid
    :param widget:需要嵌入的窗口对象QWidget
    :param class_name:窗口所属的类,[cmd:'ConsoleWindowClass',终端:'CASCADIA_HOSTING_WINDOW_CLASS']
    :param accurate:是否开启精确查找bool
    :return :窗口句柄hwnd
    """
    from PySide6.QtGui import QWindow
    import win32gui, win32process, os

    # 主线程PID
    pid_main = os.getpid()

    # 历遍全部窗口,callback是回调函数(即每次查找一个窗口句柄时执行的操作)
    hwnd_list = []  # 找到的窗口句柄,按理来说只有一个,如果有多个则取最后一个

    def callback(hwnd, extra):
        # extra是EnumWindows的第二个参数
        pid = win32process.GetWindowThreadProcessId(hwnd)  # 当前窗口pid
        if pid == pid_main:
            return False
        # 如果输入的target_inf是pid
        elif pid == extra:
            hwnd_list.append(hwnd)
            return True
        # 如果输入的target_inf是窗口标题
        elif isinstance(extra, str):
            window_title = win32gui.GetWindowText(hwnd)  # 当前窗口标题
            if accurate == True and window_title == extra:  # 精确查找
                window_class_name = win32gui.GetClassName(hwnd)  # 当前窗口类别
                if class_name is None:
                    hwnd_list.append((hwnd, window_title, window_class_name, pid))
                else:
                    if window_class_name in class_name:
                        hwnd_list.append((hwnd, window_title, window_class_name, pid))
            elif accurate == False and window_title.find(extra) != -1:  # 模糊查询
                window_class_name = win32gui.GetClassName(hwnd)  # 当前窗口类别
                if class_name is None:
                    hwnd_list.append((hwnd, window_title, window_class_name, pid))
                else:
                    if window_class_name in class_name:
                        hwnd_list.append((hwnd, window_title, window_class_name, pid))

    win32gui.EnumWindows(callback, target_inf)

    if hwnd_list == []:  # 没有匹配到窗口
        return False
    else:
        hwnd = hwnd_list[-1][0]
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    # 根据窗口句柄嵌入到pyside6界面中
    console_window = QWindow.fromWinId(hwnd)
    # 创建一个Qwiget用于容纳consolewindow
    widget_window = QWidget.createWindowContainer(console_window)
    # 将widget_window添加到布局中
    layout.addWidget(widget_window)
    return hwnd


def embed_qt_by_hwnd(hwnd, widget: QWidget) -> bool:
    """
    将窗口嵌入到Pyside6窗口中
    需要外部窗口随着pyside6一同关闭需要重写closeEvent
    def closeEvent(self, event):
        # 发送关闭消息给外部窗口（Windows API）
        if self.hwnd:
            import win32gui,win32con
            # WM_CLOSE 消息：通知窗口关闭
            win32gui.SendMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)
        super().closeEvent(event)  # 继续执行 Qt 窗口的关闭逻辑
    :param hwnd: 窗口句柄
    :param widget: pyside6容器
    """
    from PySide6.QtGui import QWindow
    try:
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        # 根据窗口句柄嵌入到pyside6界面中
        console_window = QWindow.fromWinId(hwnd)
        # 创建一个Qwiget用于容纳consolewindow
        widget_window = QWidget.createWindowContainer(console_window)
        # 将widget_window添加到布局中
        layout.addWidget(widget_window)
        return True
    except:
        return False


# 窗口无边框移动
class ReMouseWidget(QWidget):
    # 重写了鼠标响应事件
    def __init__(self, ):
        # 继承QWidget父对象
        super(ReMouseWidget, self).__init__()
        # 鼠标相对窗口的位置(x,y)
        self.__startPos = None
        # 鼠标移动的距离(x,y)
        self.__wmGap = None
        # 屏幕边界坐标
        self.screen_x_left = None
        self.screen_x_right = None
        self.screen_y_top = None
        self.screen_y_bottom = None

    def mousePressEvent(self, event):
        # 鼠标按下时，记录鼠标相对窗口的位置
        if event.button() == Qt.LeftButton:
            # event.pos() 鼠标相对窗口的位置
            # event.globalPos() 鼠标在屏幕的绝对位置
            self.__startPos = event.pos()

    def mouseMoveEvent(self, event):
        # 鼠标移动时，移动窗口跟上鼠标；同时限制窗口位置，不能移除主屏幕
        # event.pos()减去最初相对窗口位置，获得移动距离(x,y)
        self.__wmGap = event.pos() - self.__startPos
        # 移动窗口,保持鼠标与窗口的相对位置不变
        final_pos = self.pos() + self.__wmGap
        # 检查是否移除了当前主屏幕
        # 左方界限
        if self.frameGeometry().topLeft().x() + self.__wmGap.x() <= 0:
            final_pos.setX(0)
        # 上方界限
        if self.frameGeometry().topLeft().y() + self.__wmGap.y() <= 0:
            final_pos.setY(0)
        # 右方界限
        if self.frameGeometry().bottomRight().x() + self.__wmGap.x() >= 1920 / 1.25:
            final_pos.setX(1920 / 1.25 - self.width())
        # 下方界限
        if self.frameGeometry().bottomRight().y() + self.__wmGap.y() >= 1080 / 1.24:
            final_pos.setY(1080 / 1.24 - self.height())
        # 移动窗口
        self.move(final_pos)

    def mouseReleaseEvent(self, event):
        # 鼠标释放后重置
        if event.button() == Qt.LeftButton:
            self.__startPos = None
            self.__wmGap = None
        if event.button() == Qt.RightButton:
            self.__startPos = None
            self.__wmGap = None

    def screen_lim(self):
        """获取屏幕边界,支持多屏"""
        # 获取显示器数量
        self.desktop = QApplication.screens()
        # 获取各个屏幕的边界坐标
        self.screen_x = []
        self.screen_y = []
        # x [0, 1920, -1920, 0]
        # y [0, 1080, 0, 1200]
        for screen in self.desktop:
            geometry = screen.geometry()
            # device_pixel_ratio = screen.devicePixelRatio()#屏幕缩放比
            self.screen_x.append(geometry.x())
            # self.screen_x.append(geometry.x() + geometry.width() * device_pixel_ratio)
            self.screen_x.append(geometry.x() + geometry.width())
            self.screen_y.append(geometry.y())
            # self.screen_y.append(geometry.y() + geometry.height() * device_pixel_ratio)
            self.screen_y.append(geometry.y() + geometry.height())

    def enterEvent(self, event):
        # 鼠标进入窗口时
        pass

    def leaveEvent(self, event):
        # 鼠标离开窗口
        pass


# 系统托盘
class TrayIcon(QSystemTrayIcon):

    def __init__(self, SetUI, exit_func=None, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.ui = SetUI
        self.exit_func = exit_func
        self.createMenu()

    def createMenu(self):
        self.menu = QMenu()
        self.showAction1 = QAction('显示', self, triggered=self.show_window)
        self.quitAction = QAction('退出', self, triggered=self.quit)

        self.menu.addAction(self.showAction1)
        self.menu.addAction(self.quitAction)
        self.setContextMenu(self.menu)

        # 设置图标
        self.setIcon(QIcon(":/icons/ico_main.png"))
        self.icon = self.MessageIcon.Information

        # 把鼠标点击图标的信号和槽连接
        self.activated.connect(self.onIconClicked)

    def show_window(self):
        # 若是最小化，则先正常显示窗口，再变为活动窗口（暂时显示在最前面）
        # self.ui.showNormal()
        self.ui.show()
        self.ui.activateWindow()

    def quit(self):
        # QtWidgets.qApp.quit()
        self.exit_func()
        os._exit(0)  # 强制退出

    def onIconClicked(self, reason):
        # 鼠标点击icon传递的信号会带有一个整形的值
        # 1是表示单击右键，2是双击左键，3是单击左键，4是用鼠标中键点击
        # 鼠标左键单击或者双击时触发
        if reason == self.ActivationReason.Trigger or \
                reason == self.ActivationReason.DoubleClick:
            if self.ui.isMinimized() or not self.ui.isVisible():
                # 若是最小化，则先正常显示窗口，再变为活动窗口（暂时显示在最前面）
                self.show_window()
                # self.ui.setWindowFlags(QtCore.Qt.Window)
                # self.ui.show()
            else:
                self.ui.close()


class ImageWidget(QWidget):
    """
    用于显示图片
    enable_zoom_and_drag启用缩放和拖拽
    disable_zoom_and_drag关闭缩放和拖拽
    showFullScreen全屏显示
    """

    def __init__(self, image_input=None):
        super().__init__()
        if image_input is None:
            image_input = np.full((224, 224, 3), fill_value=70, dtype=np.uint8)
        self.image_input = image_input
        self.original_pixmap = self._load_image(image_input)
        self.setMinimumSize(50, 50)

        # 缩放和拖动功能的状态
        self.enable_zoom_drag = False

        # 缩放相关参数
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)

        # 拖动相关参数
        self.dragging = False
        self.last_mouse_pos = QPoint()

        # 全屏相关
        self.fullscreen_window = None
        self.fullscreen_widget = None
        self.info_bar = None
        self.esc_shortcut = None

    def _load_image(self, image_input):
        if isinstance(image_input, QPixmap):
            return image_input.copy()
        elif isinstance(image_input, QImage):
            return QPixmap.fromImage(image_input)
        elif isinstance(image_input, np.ndarray):
            return self._load_from_numpy(image_input)
        elif hasattr(image_input, 'mode') and hasattr(image_input, 'size'):
            return self._load_from_pil(image_input)
        elif isinstance(image_input, BytesIO):
            return self._load_from_bytesio(image_input)
        elif isinstance(image_input, bytes):
            return self._load_from_bytes(image_input)
        elif isinstance(image_input, str):
            pixmap = QPixmap(image_input)
            if pixmap.isNull():  # 可能是图像过大采用cv加载
                nparr = np.fromfile(image_input, dtype=np.uint8)  # 读取数据
                image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)  # 解码图像
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # 转化通道
                return self._load_from_numpy(image)
            return pixmap
        else:
            print(f"警告: 不支持的图片类型: {type(image_input)}")
            return QPixmap()

    def _load_from_numpy(self, np_array):
        try:
            h, w, c = np_array.shape
            bytes_per_line = w * c
            qimage = QImage(np_array.data, w, h, bytes_per_line,
                            QImage.Format_RGB888 if c == 3 else QImage.Format_RGBA8888)
            return QPixmap.fromImage(qimage.copy())
        except Exception as e:
            print(f"从numpy加载图片失败: {e}")
            return QPixmap()

    def _load_from_pil(self, pil_image):
        try:
            if pil_image.mode != 'RGB':
                if pil_image.mode == 'RGBA':
                    pil_image = pil_image.convert('RGBA')
                else:
                    pil_image = pil_image.convert('RGB')

            buffer = BytesIO()
            if pil_image.mode == 'RGBA':
                pil_image.save(buffer, format='PNG')
            else:
                pil_image.save(buffer, format='JPEG')

            buffer.seek(0)
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            return pixmap
        except Exception as e:
            print(f"从PIL加载图片失败: {e}")
            return QPixmap()

    def _load_from_bytesio(self, bytesio_obj):
        try:
            bytesio_obj.seek(0)
            pixmap = QPixmap()
            pixmap.loadFromData(bytesio_obj.getvalue())
            if pixmap.isNull():  # 可能是图像过大采用cv加载
                bytesio_obj.seek(0)
                nparr = np.frombuffer(bytesio_obj.read(), np.uint8)  # 读取数据
                image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)  # 解码图像
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # 转化通道
                return self._load_from_numpy(image)
            return pixmap
        except Exception as e:
            print(f"从BytesIO加载图片失败: {e}")
            return QPixmap()

    def _load_from_bytes(self, bytes_data):
        try:
            pixmap = QPixmap()
            pixmap.loadFromData(bytes_data)
            return pixmap
        except Exception as e:
            print(f"从bytes加载图片失败: {e}")
            return QPixmap()

    def is_same_image(self, image_input):
        """
        判断新输入的image_input与当前self.image_input是否相同

        参数:
        image_input: 新的图片输入

        返回:
        bool: True表示相同，False表示不同
        """
        # 1. 类型不同直接返回False
        if type(image_input) != type(self.image_input):
            return False

        # 2. 对于字符串路径
        if isinstance(image_input, str) and isinstance(self.image_input, str):
            return os.path.normpath(image_input) == os.path.normpath(self.image_input)

        # 3. 对于bytes类型
        if isinstance(image_input, bytes) and isinstance(self.image_input, bytes):
            return image_input == self.image_input

        # 4. 对于BytesIO类型
        if isinstance(image_input, BytesIO) and isinstance(self.image_input, BytesIO):
            image_input.seek(0)
            self.image_input.seek(0)
            return image_input.read() == self.image_input.read()

        # 5. 对于numpy数组
        if isinstance(image_input, np.ndarray) and isinstance(self.image_input, np.ndarray):
            if image_input.shape != self.image_input.shape:
                return False
            return np.array_equal(image_input, self.image_input)

        # 6. 对于PIL图像
        if hasattr(image_input, 'mode') and hasattr(self.image_input, 'mode'):
            # 比较模式和尺寸
            if image_input.mode != self.image_input.mode:
                return False
            if image_input.size != self.image_input.size:
                return False

            # 转换为bytes比较
            buffer1 = BytesIO()
            buffer2 = BytesIO()

            image_format = 'PNG' if image_input.mode == 'RGBA' else 'JPEG'
            image_input.save(buffer1, format=image_format)
            self.image_input.save(buffer2, format=image_format)

            return buffer1.getvalue() == buffer2.getvalue()

        # 7. 对于QPixmap
        if isinstance(image_input, QPixmap) and isinstance(self.image_input, QPixmap):
            return image_input.cacheKey() == self.image_input.cacheKey()

        # 8. 对于QImage
        if isinstance(image_input, QImage) and isinstance(self.image_input, QImage):
            return image_input.cacheKey() == self.image_input.cacheKey()

        # 9. 其他情况尝试比较数据
        try:
            # 尝试将新输入转换为QPixmap进行比较
            new_pixmap = self._load_image(image_input)
            if new_pixmap.isNull() or self.original_pixmap.isNull():
                return False

            # 比较尺寸
            if new_pixmap.size() != self.original_pixmap.size():
                return False

            # 比较hash值
            import hashlib
            # 将QPixmap转换为QByteArray然后计算hash
            buffer = QByteArray()
            buffer_stream = QBuffer(buffer)
            buffer_stream.open(QIODevice.WriteOnly)
            new_pixmap.save(buffer_stream, "PNG")

            buffer2 = QByteArray()
            buffer_stream2 = QBuffer(buffer2)
            buffer_stream2.open(QIODevice.WriteOnly)
            self.original_pixmap.save(buffer_stream2, "PNG")

            hash1 = hashlib.md5(buffer.data()).hexdigest()
            hash2 = hashlib.md5(buffer2.data()).hexdigest()

            return hash1 == hash2

        except Exception as e:
            print(f"比较图片时出错: {e}")
            # 如果无法比较，默认返回False（需要更新）
            return False

    def set_image(self, image_input) -> bool:
        """设置新图片，如果是相同的图片则跳过更新"""
        # 检查是否相同
        if self.is_same_image(image_input):
            return False  # 返回False表示没有更新

        self.image_input = image_input
        self.original_pixmap = self._load_image(image_input)
        self.reset_view()
        return True  # 返回True表示已更新

    def paintEvent(self, event: QPaintEvent):
        if self.original_pixmap.isNull():
            painter = QPainter(self)
            painter.drawText(self.rect(), Qt.AlignCenter, "图片加载失败")
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # 计算缩放后的矩形
        scaled_rect = self.calculateScaledRect()

        # 应用偏移量（如果启用了缩放拖动功能）
        if self.enable_zoom_drag:
            scaled_rect.translate(self.offset)

        painter.drawPixmap(scaled_rect, self.original_pixmap)

    def calculateScaledRect(self):
        if self.original_pixmap.isNull():
            return QRect(0, 0, 0, 0)

        widget_rect = self.rect()
        pixmap_size = self.original_pixmap.size()

        # 始终计算自适应窗口的尺寸
        pixmap_ratio = pixmap_size.width() / pixmap_size.height()
        widget_ratio = widget_rect.width() / widget_rect.height()

        if pixmap_ratio > widget_ratio:
            # 图片更宽，按宽度缩放
            fitted_width = widget_rect.width()
            fitted_height = fitted_width / pixmap_ratio
        else:
            # 图片更高，按高度缩放
            fitted_height = widget_rect.height()
            fitted_width = fitted_height * pixmap_ratio

        # 应用当前缩放因子
        scaled_width = fitted_width * self.scale_factor
        scaled_height = fitted_height * self.scale_factor

        # 计算居中位置
        x = (widget_rect.width() - scaled_width) / 2
        y = (widget_rect.height() - scaled_height) / 2

        return QRect(x, y, scaled_width, scaled_height)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update()

    def enable_zoom_and_drag(self):
        if not self.enable_zoom_drag:
            self.enable_zoom_drag = True
            self.setMouseTracking(True)
            self.reset_view()

    def disable_zoom_and_drag(self):
        if self.enable_zoom_drag:
            self.enable_zoom_drag = False
            self.setMouseTracking(False)
            self.reset_view()
            self.setCursor(Qt.ArrowCursor)

    def reset_view(self):
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)
        self.update()

    def wheelEvent(self, event: QWheelEvent):
        if not self.enable_zoom_drag or self.original_pixmap.isNull():
            event.ignore()
            return

        # 保存缩放前的状态
        old_scale = self.scale_factor

        # 计算缩放前的矩形（考虑当前偏移）
        old_rect = self.calculateScaledRect()
        old_rect_with_offset = old_rect.translated(self.offset)

        # 获取鼠标位置
        mouse_pos = event.position().toPoint()

        # 判断缩放方向
        if event.angleDelta().y() > 0:
            # 向上滚，放大 - 这里限制最大缩放为50.0（5000%）
            self.scale_factor = min(self.scale_factor * 1.1, 50.0)
        else:
            # 向下滚，缩小 - 这里限制最小缩放为0.01（1%）
            self.scale_factor = max(self.scale_factor / 1.1, 0.01)

        if abs(self.scale_factor - old_scale) < 0.001:
            event.ignore()
            return

        # 智能缩放：以鼠标位置为中心
        if old_rect_with_offset.width() > 0 and old_rect_with_offset.height() > 0:
            # 计算鼠标在图片中的相对位置（考虑当前偏移）
            rel_x = (mouse_pos.x() - old_rect_with_offset.x()) / old_rect_with_offset.width()
            rel_y = (mouse_pos.y() - old_rect_with_offset.y()) / old_rect_with_offset.height()

            # 确保比例在0-1范围内
            rel_x = max(0.0, min(1.0, rel_x))
            rel_y = max(0.0, min(1.0, rel_y))

            # 计算缩放后的矩形（不考虑偏移）
            new_rect = self.calculateScaledRect()

            # 计算鼠标在新图片中的目标位置
            target_x = mouse_pos.x() - rel_x * new_rect.width()
            target_y = mouse_pos.y() - rel_y * new_rect.height()

            # 更新偏移量：使鼠标位置对应的图片内容保持不变
            self.offset = QPoint(
                int(target_x - new_rect.x()),
                int(target_y - new_rect.y())
            )

        self.update()
        event.accept()

    def can_drag(self):
        """判断当前是否可以拖动图片"""
        if not self.enable_zoom_drag or self.original_pixmap.isNull():
            return False

        # 计算缩放后的图片尺寸
        scaled_width = self.original_pixmap.width() * self.scale_factor
        scaled_height = self.original_pixmap.height() * self.scale_factor

        # 只有当缩放后的图片尺寸大于窗口尺寸时，才允许拖动
        widget_rect = self.rect()
        return scaled_width > widget_rect.width() or scaled_height > widget_rect.height()

    def mousePressEvent(self, event: QMouseEvent):
        if not self.can_drag():
            super().mousePressEvent(event)
            return

        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.last_mouse_pos = event.position().toPoint()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.enable_zoom_drag:
            super().mouseMoveEvent(event)
            return

        current_pos = event.position().toPoint()

        if self.dragging and self.can_drag():
            delta = current_pos - self.last_mouse_pos
            self.offset += delta
            self.last_mouse_pos = current_pos
            self.update()
            event.accept()
        elif not self.dragging and self.can_drag():
            self.setCursor(Qt.OpenHandCursor)
            event.accept()
        else:
            self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.dragging and event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """鼠标双击事件：复原图像"""
        if event.button() == Qt.LeftButton:
            self.reset_view()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def get_image_info(self):
        if self.original_pixmap.isNull():
            return "无图片"

        return {
            'width': self.original_pixmap.width(),
            'height': self.original_pixmap.height(),
            'input_type': type(self.image_input).__name__,
            'has_alpha': self.original_pixmap.hasAlphaChannel()
        }

    # ==================== 全屏功能 ====================
    def showFullScreen(self, show_info=True):
        """显示全屏图片，支持ESC退出,show_info是否显示提示信息"""
        if self.original_pixmap.isNull():
            return

        # 如果已经在全屏，先退出
        if self.fullscreen_window is not None:
            self.exitFullScreen()
            return

        # 创建全屏窗口
        self.fullscreen_window = QWidget()
        self.fullscreen_window.setWindowTitle("全屏查看 - 按ESC退出")
        self.fullscreen_window.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        # 设置全屏
        self.fullscreen_window.showFullScreen()

        # 创建全屏布局
        layout = QVBoxLayout(self.fullscreen_window)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建全屏图片显示部件
        self.fullscreen_widget = QWidget()
        self.fullscreen_widget.setStyleSheet("background-color: black;")
        layout.addWidget(self.fullscreen_widget)

        # 创建信息栏
        self.info_bar = QWidget()
        self.info_bar.setFixedHeight(30)
        self.info_bar.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                font-size: 12px;
            }
        """)

        info_layout = QHBoxLayout(self.info_bar)
        info_layout.setContentsMargins(10, 0, 10, 0)

        # 显示图片信息
        if show_info:
            info = self.get_image_info()
            if isinstance(info, dict):
                info_text = f"尺寸: {info.get('width', 0)}×{info.get('height', 0)}"
            else:
                info_text = str(info)

            self.info_label = QLabel(info_text)
            self.info_label.setStyleSheet("color: white;")
            info_layout.addWidget(self.info_label)

            info_layout.addStretch()

            # 添加退出提示
            self.esc_label = QLabel("按 ESC 退出全屏 | 双击图片或窗口任意位置退出")
            self.esc_label.setStyleSheet("color: lightgray;")
            info_layout.addWidget(self.esc_label)

            layout.addWidget(self.info_bar)

        # 初始化全屏状态
        self.fullscreen_scale_factor = 1.0
        self.fullscreen_offset = QPoint(0, 0)
        self.fullscreen_dragging = False
        self.fullscreen_last_mouse_pos = QPoint()

        # 设置事件过滤器
        self.fullscreen_window.installEventFilter(self)

        # 添加ESC快捷键
        self.esc_shortcut = QShortcut(Qt.Key.Key_Escape, self.fullscreen_window)
        self.esc_shortcut.activated.connect(self.exitFullScreen)

        # 重写全屏窗口的事件处理
        self.fullscreen_widget.wheelEvent = self.fullscreenWheelEvent
        self.fullscreen_widget.mousePressEvent = self.fullscreenMousePressEvent
        self.fullscreen_widget.mouseMoveEvent = self.fullscreenMouseMoveEvent
        self.fullscreen_widget.mouseReleaseEvent = self.fullscreenMouseReleaseEvent
        self.fullscreen_widget.paintEvent = self.fullscreenPaintEvent

        # 允许窗口双击退出
        self.fullscreen_window.mouseDoubleClickEvent = self.fullscreenWindowDoubleClick

        # 强制更新显示
        self.fullscreen_widget.update()

    def exitFullScreen(self):
        """退出全屏"""
        if self.fullscreen_window:
            try:
                if self.esc_shortcut:
                    self.esc_shortcut.setEnabled(False)
                self.fullscreen_window.close()
                self.fullscreen_window.deleteLater()
            except:
                pass

            # 清理引用
            self.fullscreen_window = None
            self.fullscreen_widget = None
            self.info_bar = None
            self.esc_shortcut = None

    def fullscreenPaintEvent(self, event):
        """全屏窗口的绘制事件"""
        if self.original_pixmap.isNull():
            return

        painter = QPainter(self.fullscreen_widget)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # 获取全屏窗口尺寸
        widget_rect = self.fullscreen_widget.rect()
        pixmap_size = self.original_pixmap.size()

        # 计算自适应尺寸
        pixmap_ratio = pixmap_size.width() / pixmap_size.height()
        widget_ratio = widget_rect.width() / widget_rect.height()

        if pixmap_ratio > widget_ratio:
            fitted_width = widget_rect.width()
            fitted_height = fitted_width / pixmap_ratio
        else:
            fitted_height = widget_rect.height()
            fitted_width = fitted_height * pixmap_ratio

        # 应用缩放因子
        scaled_width = fitted_width * self.fullscreen_scale_factor
        scaled_height = fitted_height * self.fullscreen_scale_factor

        # 计算居中位置
        x = (widget_rect.width() - scaled_width) / 2
        y = (widget_rect.height() - scaled_height) / 2

        # 应用偏移量
        scaled_rect = QRect(x, y, scaled_width, scaled_height)
        scaled_rect.translate(self.fullscreen_offset)

        painter.drawPixmap(scaled_rect, self.original_pixmap)

    def fullscreenWheelEvent(self, event):
        """全屏窗口的滚轮事件（缩放）"""
        if self.original_pixmap.isNull():
            return

        # 保存缩放前的状态
        old_scale = self.fullscreen_scale_factor
        widget_rect = self.fullscreen_widget.rect()
        pixmap_size = self.original_pixmap.size()

        # 计算当前显示矩形
        pixmap_ratio = pixmap_size.width() / pixmap_size.height()
        widget_ratio = widget_rect.width() / widget_rect.height()

        if pixmap_ratio > widget_ratio:
            fitted_width = widget_rect.width()
            fitted_height = fitted_width / pixmap_ratio
        else:
            fitted_height = widget_rect.height()
            fitted_width = fitted_height * pixmap_ratio

        old_width = fitted_width * old_scale
        old_height = fitted_height * old_scale
        old_x = (widget_rect.width() - old_width) / 2 + self.fullscreen_offset.x()
        old_y = (widget_rect.height() - old_height) / 2 + self.fullscreen_offset.y()

        # 获取鼠标位置
        mouse_pos = event.position().toPoint()

        # 判断缩放方向
        if event.angleDelta().y() > 0:
            # 放大
            self.fullscreen_scale_factor = min(self.fullscreen_scale_factor * 1.1, 50.0)
        else:
            # 缩小
            self.fullscreen_scale_factor = max(self.fullscreen_scale_factor / 1.1, 0.01)

        # 计算缩放后尺寸
        new_width = fitted_width * self.fullscreen_scale_factor
        new_height = fitted_height * self.fullscreen_scale_factor

        # 计算鼠标在图片中的相对位置
        if old_width > 0 and old_height > 0:
            rel_x = (mouse_pos.x() - old_x) / old_width
            rel_y = (mouse_pos.y() - old_y) / old_height

            rel_x = max(0.0, min(1.0, rel_x))
            rel_y = max(0.0, min(1.0, rel_y))

            # 计算新位置
            new_x = mouse_pos.x() - rel_x * new_width
            new_y = mouse_pos.y() - rel_y * new_height

            # 计算偏移量
            center_x = (widget_rect.width() - new_width) / 2
            center_y = (widget_rect.height() - new_height) / 2

            self.fullscreen_offset = QPoint(
                int(new_x - center_x),
                int(new_y - center_y)
            )

        self.fullscreen_widget.update()

    def fullscreenMousePressEvent(self, event):
        """全屏窗口的鼠标按下事件（拖动）"""
        if event.button() == Qt.LeftButton:
            self.fullscreen_dragging = True
            self.fullscreen_last_mouse_pos = event.position().toPoint()
            self.fullscreen_widget.setCursor(Qt.ClosedHandCursor)
            event.accept()

    def fullscreenMouseMoveEvent(self, event):
        """全屏窗口的鼠标移动事件"""
        current_pos = event.position().toPoint()

        if self.fullscreen_dragging:
            delta = current_pos - self.fullscreen_last_mouse_pos
            self.fullscreen_offset += delta
            self.fullscreen_last_mouse_pos = current_pos
            self.fullscreen_widget.update()
            event.accept()
        else:
            self.fullscreen_widget.setCursor(Qt.OpenHandCursor)

    def fullscreenMouseReleaseEvent(self, event):
        """全屏窗口的鼠标释放事件"""
        if event.button() == Qt.LeftButton and self.fullscreen_dragging:
            self.fullscreen_dragging = False
            self.fullscreen_widget.setCursor(Qt.ArrowCursor)
            event.accept()

    def fullscreenWindowDoubleClick(self, event):
        """全屏窗口的双击事件"""
        if event.button() == Qt.LeftButton:
            self.exitFullScreen()
            event.accept()

    def eventFilter(self, obj, event):
        """事件过滤器，用于捕获键盘事件"""
        if self.fullscreen_window and obj == self.fullscreen_window:
            if event.type() == QEvent.Type.KeyPress:
                if event.key() == Qt.Key.Key_Escape:
                    self.exitFullScreen()
                    return True
        return super().eventFilter(obj, event)


class WindowDesktop(QWidget):
    """
    用于创建Window系统下的桌面层级窗口
    addWidget方法可以添加自定义的QWidget子类
    """
    main_dpi = None  # 主屏幕的DPI

    def __init__(self, screen: QScreen):
        super().__init__()
        # 实例属性
        self.name = screen.name()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # 移除所有边距（上、右、下、左）
        # 获取屏幕分辨率,初始化完成后会变成以屏幕左上角为准的x,y 宽高以主屏幕缩放为准
        # 排除任务栏时用 availableGeometry,不排除时用geometry
        self.rect = screen.availableGeometry()
        self.dpi: float = None  # 所在屏幕的DPI
        # 计算DPI
        for monitor in get_monitors():
            # 计算所在屏幕的DPI
            if monitor.name == self.name or (monitor.x == self.rect.x() and monitor.y == self.rect.y()):
                self.dpi = round(monitor.width / screen.geometry().width(), 2)
            # 计算主屏幕DPI
            if self.main_dpi is None and monitor.x == 0 and monitor.y == 0:
                for i in QApplication.screens():
                    rect = i.geometry()
                    if rect.x() == 0 and rect.y() == 0:  # 主屏幕
                        self.main_dpi = round(monitor.width / rect.width(), 2)
        # 初始化widget
        self.uiIinit()  # 窗口初始化
        self.embedWidget()  # 嵌入WorkerW
        self.show()  # 显示窗口
        # 调试信息
        # self.addWidget(QLabel(
        #     text=f'设备名称:{self.name}\n'
        #          f'窗口坐标:(x:{self.rect.x()} y:{self.rect.y()} w:{self.rect.width()} h:{self.rect.height()})\n'
        #          f'DPI:{self.dpi} 主屏幕DPI:{self.main_dpi}')
        # )

    def uiIinit(self):
        """窗口初始化"""
        # 将相对主屏幕坐标换算为相对左上角坐标
        offset, normalized_rects = self.get_normalized_screen_geometries()
        self.rect.setRect(normalized_rects[self.name].x(),
                          normalized_rects[self.name].y(),
                          int(self.rect.width() * self.dpi / self.main_dpi),
                          int(self.rect.height() * self.dpi / self.main_dpi))
        # 窗口属性:极简配置,强制显示在背景
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Tool |  # 工具窗口，不占任务栏
            Qt.WindowStaysOnBottomHint)  # 强制最底层
        # 设置窗口尺寸需要以主屏幕DPI来计算
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setFixedSize(self.rect.width(), self.rect.height())

    def embedWidget(self) -> tuple[str, QWidget]:
        """嵌入窗口"""
        # 获取桌面 WorkerW 窗口（替代 Progman，避免层级遮挡）
        # WorkerW 是 Windows 真正的桌面背景窗口，比 Progman 更稳定
        self.progman_hwnd = win32gui.FindWindow("Progman", None)
        win32gui.SendMessageTimeout(self.progman_hwnd, 0x052C, 0, 0, win32con.SMTO_NORMAL, 1000)
        self.workerw_hwnd = None

        # 枚举所有 WorkerW 窗口，找到带 SHELLDLL_DefView 子窗口的父窗口（背景窗口）
        def enum_windows(hwnd, param):
            if win32gui.IsWindowVisible(hwnd) and win32gui.FindWindowEx(hwnd, None, "SHELLDLL_DefView", None):
                self.workerw_hwnd = win32gui.FindWindowEx(None, hwnd, "WorkerW", None)
            return True

        win32gui.EnumWindows(enum_windows, None)
        # 绑定到 WorkerW（真正的背景窗口，无遮挡）
        if self.workerw_hwnd:
            win32gui.SetParent(int(self.winId()), self.workerw_hwnd)
            # 配置窗口属性:窗口显示在最底层(图标在上方)
            win32gui.SetWindowPos(
                int(self.winId()),  # 窗口句柄
                win32con.HWND_BOTTOM,  # 将窗口置于 Z 序的底部
                self.rect.x(), self.rect.y(), 0, 0,  # 窗口坐标(x,y,w,h),坐标左上角屏幕为原点
                # win32con.SWP_NOMOVE |  # 忽略x, y坐标
                win32con.SWP_NOSIZE |  # 忽略w,h坐标
                win32con.SWP_SHOWWINDOW |  # 显示窗口
                win32con.SWP_NOACTIVATE  # 不将窗口激活（不使其获得焦点）
            )
        else:
            raise ValueError(f'{__name__}.{self.__class__.__name__}.embedWidget 未找到WorkerW')

    @staticmethod
    def get_normalized_screen_geometries() -> tuple[QPoint, dict[str:QRect]]:
        """
        获取归一化的屏幕几何信息,原点在所有屏幕的最左上角

        Returns:
            Tuple[QPoint, List[QRect]]:
                - 第一个元素是全局偏移量（最左上角的点）
                - 第二个元素是调整后的屏幕矩形列表
        """
        screens = QApplication.screens()

        if not screens:
            return QPoint(0, 0), []

        # 计算最小x和最小y
        min_x = 0
        min_y = 0

        for screen in screens:
            rect = screen.geometry()
            min_x = min(min_x, rect.x())
            min_y = min(min_y, rect.y())

        # 创建偏移量
        offset = QPoint(min_x, min_y)

        # 转换每个屏幕的坐标
        normalized_rects = {}
        for screen in screens:
            original_rect = screen.geometry()
            adjusted_top_left = original_rect.topLeft() - offset
            normalized_rects.update({screen.name(): QRect(adjusted_top_left, original_rect.size())})

        return offset, normalized_rects

    def getWidgetCount(self) -> int:
        """获取布局内控件数量"""
        return self.layout.count()

    def addWidget(self, widget: QWidget):
        self.layout.addWidget(widget)
        for index in range(self.layout.count()):
            self.layout.setStretch(index, index)


if __name__ == '__main__':
    app = QApplication([])
    # 测试使用文件路径
    window = ImageWidget(
        r"E:\code\Python\simple\AutoWallpaper\wallpaper\pyside6_GUI\sub_ui\wallhaven\config\正常级\人物\8g5d5o.jpg")
    window.resize(800, 600)
    window.enable_zoom_and_drag()  # 启用缩放和拖动功能
    window.show()
    app.exec()
