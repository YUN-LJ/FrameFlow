"""子窗口部件"""
import os, numpy as np
from io import BytesIO
import win32gui, win32con
from screeninfo import get_monitors
from typing import TYPE_CHECKING, Optional

from Fun.BaseTools import Get

if TYPE_CHECKING:
    from Fun.BaseTools.Image import ImageLoad

from PySide6.QtCore import Qt, QRect, QPoint, QEvent, Signal, QTimer
from PySide6.QtGui import (QWindow, QAction, QIcon, QShortcut, QScreen,
                           QPixmap, QPainter, QPaintEvent,
                           QImage, QWheelEvent, QMouseEvent)
from PySide6.QtWidgets import (
    QFileDialog, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QSystemTrayIcon, QMenu, QApplication, QTableWidget, QSplitter
)
# 风格组件
from qfluentwidgets import Action, FluentIcon as FIF
from qfluentwidgets.components.widgets import SystemTrayMenu


class ImageWidget(QWidget):
    """
    用于显示图片
    enable_zoom_and_drag启用缩放和拖拽
    disable_zoom_and_drag关闭缩放和拖拽
    showFullScreen全屏显示
    """
    mouseEnterSignal = Signal()
    mouseLeaveSignal = Signal()
    mousePressSignal = Signal()
    mouseReleaseSignal = Signal()
    mouseDoubleSignal = Signal()
    mouseWheelSignal = Signal()
    fullScreenSignal = Signal(bool)

    default_image_load = None  # 会在类外部设置默认的ImageLoad实例

    def __init__(self, image_load: Optional['ImageLoad'] = None, parent=None):
        super().__init__(parent)
        # 直接接收 ImageLoad 对象
        if image_load is None:
            if self.__class__.default_image_load is None:
                from Fun.BaseTools.Image import ImageLoad
                self.__class__.default_image_load = ImageLoad(np.full((224, 224, 4), fill_value=0, dtype=np.uint8))
            self.image_load = self.__class__.default_image_load
        else:
            self.image_load = image_load

        self.display_text = None
        self.original_pixmap = self._load_pixmap_from_imageload()
        self.setMinimumSize(50, 50)

        # 缩放和拖动功能的状态
        self.enable_zoom_drag = False
        self.isFull = False
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)
        self.dragging = False
        self.last_mouse_pos = QPoint()

        # 全屏相关
        self.fullscreen_window = None
        self.fullscreen_widget = None
        self.info_bar = None
        self.esc_shortcut = None

    def _load_pixmap_from_imageload(self) -> QPixmap:
        """从 ImageLoad 对象加载图片为 QPixmap"""
        if self.display_text:
            return QPixmap()
        return self.image_load.get_qpixmap()

    def set_image(self, image_load: Optional['ImageLoad']) -> bool:
        """设置新图片"""
        self.display_text = None

        # 检查是否是同一个对象
        if self.image_load is image_load:
            return False

        self.image_load = image_load
        self.original_pixmap = self._load_pixmap_from_imageload()
        self.reset_view()

        if self.isFull:
            self.fullscreen_widget.update()

        return True

    def set_text(self, text: str):
        """显示文字"""
        self.display_text = text
        self.original_pixmap = QPixmap()
        self.update()

    def paintEvent(self, event):
        if self.display_text:
            painter = QPainter(self)
            painter.drawText(self.rect(), Qt.AlignCenter, self.display_text)
            return

        if self.original_pixmap.isNull():
            painter = QPainter(self)
            painter.drawText(self.rect(), Qt.AlignCenter, "图片加载失败")
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        scaled_rect = self.calculateScaledRect()

        if self.enable_zoom_drag:
            scaled_rect.translate(self.offset)

        painter.drawPixmap(scaled_rect, self.original_pixmap)

    def calculateScaledRect(self):
        if self.original_pixmap.isNull():
            return QRect(0, 0, 0, 0)

        widget_rect = self.rect()
        pixmap_size = self.original_pixmap.size()

        pixmap_ratio = pixmap_size.width() / pixmap_size.height()
        widget_ratio = widget_rect.width() / widget_rect.height()

        if pixmap_ratio > widget_ratio:
            fitted_width = widget_rect.width()
            fitted_height = fitted_width / pixmap_ratio
        else:
            fitted_height = widget_rect.height()
            fitted_width = fitted_height * pixmap_ratio

        scaled_width = fitted_width * self.scale_factor
        scaled_height = fitted_height * self.scale_factor

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

        old_scale = self.scale_factor
        old_rect = self.calculateScaledRect()
        old_rect_with_offset = old_rect.translated(self.offset)
        mouse_pos = event.position().toPoint()

        if event.angleDelta().y() > 0:
            self.scale_factor = min(self.scale_factor * 1.1, 50.0)
        else:
            self.scale_factor = max(self.scale_factor / 1.1, 0.01)

        if abs(self.scale_factor - old_scale) < 0.001:
            event.ignore()
            return

        if old_rect_with_offset.width() > 0 and old_rect_with_offset.height() > 0:
            rel_x = (mouse_pos.x() - old_rect_with_offset.x()) / old_rect_with_offset.width()
            rel_y = (mouse_pos.y() - old_rect_with_offset.y()) / old_rect_with_offset.height()
            rel_x = max(0.0, min(1.0, rel_x))
            rel_y = max(0.0, min(1.0, rel_y))

            new_rect = self.calculateScaledRect()
            target_x = mouse_pos.x() - rel_x * new_rect.width()
            target_y = mouse_pos.y() - rel_y * new_rect.height()

            self.offset = QPoint(
                int(target_x - new_rect.x()),
                int(target_y - new_rect.y())
            )

        self.mouseWheelSignal.emit()
        self.update()
        event.accept()

    def can_drag(self):
        if not self.enable_zoom_drag or self.original_pixmap.isNull():
            return False

        scaled_width = self.original_pixmap.width() * self.scale_factor
        scaled_height = self.original_pixmap.height() * self.scale_factor
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
            self.mousePressSignal.emit()
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

    def enterEvent(self, event):
        self.mouseEnterSignal.emit()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.mouseLeaveSignal.emit()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.dragging and event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(Qt.ArrowCursor)
            self.mouseReleaseSignal.emit()
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.reset_view()
            self.mouseDoubleSignal.emit()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def get_image_info(self):
        if self.original_pixmap.isNull():
            return "无图片"

        return {
            'width': self.original_pixmap.width(),
            'height': self.original_pixmap.height(),
            'memory_mb': self.image_load.size_mb,
            'shape': self.image_load.shape,
            'channels': self.image_load.channels,
            'has_alpha': self.original_pixmap.hasAlphaChannel()
        }

    # ==================== 全屏功能 ====================
    def showFullScreen(self, show_info=True):
        if self.original_pixmap.isNull():
            return

        if self.fullscreen_window is not None:
            self.exitFullScreen()
            return

        self.fullscreen_window = QWidget()
        self.fullscreen_window.setWindowTitle("全屏查看 - 按ESC退出")
        self.fullscreen_window.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.fullscreen_window.showFullScreen()

        layout = QVBoxLayout(self.fullscreen_window)
        layout.setContentsMargins(0, 0, 0, 0)

        self.fullscreen_widget = QWidget()
        self.fullscreen_widget.setStyleSheet("background-color: black;")
        layout.addWidget(self.fullscreen_widget)

        if show_info:
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

            info = self.get_image_info()
            if isinstance(info, dict):
                info_text = f"尺寸: {info.get('width', 0)}×{info.get('height', 0)} | 内存: {info.get('memory_mb', 0):.2f} MB"
            else:
                info_text = str(info)

            self.info_label = QLabel(info_text)
            self.info_label.setStyleSheet("color: white;")
            info_layout.addWidget(self.info_label)
            info_layout.addStretch()

            self.esc_label = QLabel("按 ESC 退出全屏 | 双击图片恢复原状")
            self.esc_label.setStyleSheet("color: lightgray;")
            info_layout.addWidget(self.esc_label)

            layout.addWidget(self.info_bar)

        self.fullscreen_scale_factor = 1.0
        self.fullscreen_offset = QPoint(0, 0)
        self.fullscreen_dragging = False
        self.fullscreen_last_mouse_pos = QPoint()

        self.fullscreen_window.installEventFilter(self)

        self.esc_shortcut = QShortcut(Qt.Key.Key_Escape, self.fullscreen_window)
        self.esc_shortcut.activated.connect(self.exitFullScreen)

        # 绑定事件处理方法
        self.fullscreen_widget.wheelEvent = self.fullscreenWheelEvent
        self.fullscreen_widget.mousePressEvent = self.fullscreenMousePressEvent
        self.fullscreen_widget.mouseMoveEvent = self.fullscreenMouseMoveEvent
        self.fullscreen_widget.mouseReleaseEvent = self.fullscreenMouseReleaseEvent
        self.fullscreen_widget.paintEvent = self.fullscreenPaintEvent
        self.fullscreen_widget.mouseDoubleClickEvent = self.fullscreenResetView  # 改为重置视图

        # 可选：同时也支持窗口背景双击重置
        self.fullscreen_window.mouseDoubleClickEvent = self.fullscreenWindowDoubleClick

        self.fullscreen_widget.update()
        self.isFull = True
        self.fullScreenSignal.emit(True)

    def exitFullScreen(self):
        if self.fullscreen_window:
            try:
                if self.esc_shortcut:
                    self.esc_shortcut.setEnabled(False)
                self.fullscreen_window.close()
                self.fullscreen_window.deleteLater()
            except:
                pass

            self.fullscreen_window = None
            self.fullscreen_widget = None
            self.info_bar = None
            self.esc_shortcut = None
            self.isFull = False
            self.fullScreenSignal.emit(False)

    def fullscreenPaintEvent(self, event):
        if self.original_pixmap.isNull():
            return

        painter = QPainter(self.fullscreen_widget)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        widget_rect = self.fullscreen_widget.rect()
        pixmap_size = self.original_pixmap.size()

        pixmap_ratio = pixmap_size.width() / pixmap_size.height()
        widget_ratio = widget_rect.width() / widget_rect.height()

        if pixmap_ratio > widget_ratio:
            fitted_width = widget_rect.width()
            fitted_height = fitted_width / pixmap_ratio
        else:
            fitted_height = widget_rect.height()
            fitted_width = fitted_height * pixmap_ratio

        scaled_width = fitted_width * self.fullscreen_scale_factor
        scaled_height = fitted_height * self.fullscreen_scale_factor

        x = (widget_rect.width() - scaled_width) / 2
        y = (widget_rect.height() - scaled_height) / 2

        scaled_rect = QRect(x, y, scaled_width, scaled_height)
        scaled_rect.translate(self.fullscreen_offset)

        painter.drawPixmap(scaled_rect, self.original_pixmap)

    def fullscreenWheelEvent(self, event):
        if self.original_pixmap.isNull():
            return

        old_scale = self.fullscreen_scale_factor
        widget_rect = self.fullscreen_widget.rect()
        pixmap_size = self.original_pixmap.size()

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

        mouse_pos = event.position().toPoint()

        if event.angleDelta().y() > 0:
            self.fullscreen_scale_factor = min(self.fullscreen_scale_factor * 1.1, 50.0)
        else:
            self.fullscreen_scale_factor = max(self.fullscreen_scale_factor / 1.1, 0.01)

        new_width = fitted_width * self.fullscreen_scale_factor
        new_height = fitted_height * self.fullscreen_scale_factor

        if old_width > 0 and old_height > 0:
            rel_x = (mouse_pos.x() - old_x) / old_width
            rel_y = (mouse_pos.y() - old_y) / old_height
            rel_x = max(0.0, min(1.0, rel_x))
            rel_y = max(0.0, min(1.0, rel_y))

            new_x = mouse_pos.x() - rel_x * new_width
            new_y = mouse_pos.y() - rel_y * new_height

            center_x = (widget_rect.width() - new_width) / 2
            center_y = (widget_rect.height() - new_height) / 2

            self.fullscreen_offset = QPoint(
                int(new_x - center_x),
                int(new_y - center_y)
            )

        self.fullscreen_widget.update()

    def fullscreenMousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.fullscreen_dragging = True
            self.fullscreen_last_mouse_pos = event.position().toPoint()
            self.fullscreen_widget.setCursor(Qt.ClosedHandCursor)
            event.accept()

    def fullscreenMouseMoveEvent(self, event):
        current_pos = event.position().toPoint()

        if self.fullscreen_dragging:
            delta = current_pos - self.fullscreen_last_mouse_pos
            self.fullscreen_offset += delta
            self.fullscreen_last_mouse_pos = current_pos
            self.fullscreen_widget.update()
            event.accept()
        else:
            # 只在可以拖拽时显示手型光标
            if self.fullscreen_scale_factor > 1.0:  # 或者检查图片是否超出窗口
                self.fullscreen_widget.setCursor(Qt.OpenHandCursor)
            else:
                self.fullscreen_widget.setCursor(Qt.ArrowCursor)

    def fullscreenMouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.fullscreen_dragging:
            self.fullscreen_dragging = False
            self.fullscreen_widget.setCursor(Qt.ArrowCursor)
            event.accept()

    def fullscreenResetView(self, event):
        """全屏模式下双击重置视图"""
        if event.button() == Qt.LeftButton:
            self.fullscreen_scale_factor = 1.0
            self.fullscreen_offset = QPoint(0, 0)
            self.fullscreen_widget.update()
            event.accept()

    def fullscreenWindowDoubleClick(self, event):
        """全屏窗口背景双击也重置视图"""
        if event.button() == Qt.LeftButton:
            self.fullscreenResetView(event)

    def eventFilter(self, obj, event):
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


class EmbeddedPythonTerminal(QWidget):
    """嵌入python启动器终端"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hwnd = Get.python_cmd_hwnd()

    def embedTerminal(self):
        """将窗口嵌入到Pyside6窗口中"""
        if self.hwnd:
            self.layout = QVBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            # 根据窗口句柄嵌入到pyside6界面中
            self.terminal_window = QWindow.fromWinId(self.hwnd)
            # 创建一个QWidget用于容纳terminal_window
            self.terminal_widget = QWidget.createWindowContainer(self.terminal_window)
            # 将widget_window添加到布局中
            self.layout.addWidget(self.terminal_widget)

    def show(self):
        super().show()
        self.embedTerminal()

    def closeEvent(self, event):
        # 发送关闭消息给外部窗口（Windows API）
        if self.hwnd:
            # WM_CLOSE 消息：通知窗口关闭
            win32gui.SendMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)
        super().closeEvent(event)  # 继续执行 Qt 窗口的关闭逻辑


class TrayIcon(QSystemTrayIcon):
    showClicked = Signal()  # 显示按钮
    quitClicked = Signal()  # 退出按钮

    def __init__(self, parent: QWidget = None):
        self.__parent = parent
        super().__init__(parent)
        self.__uiInit()
        self.createMenu()

    def __uiInit(self):
        windows_ico = self.__parent.windowIcon()
        if not windows_ico:
            windows_ico = QIcon(':/qfluentwidgets/images/logo.png')
        self.setIcon(windows_ico)

    def createMenu(self):
        self.menu = SystemTrayMenu(parent=self.__parent)
        self.menu.addActions([
            Action(FIF.HOME, '显示', triggered=lambda _: self.showClicked.emit()),
            Action(FIF.POWER_BUTTON, '退出', triggered=lambda _: self.quitClicked.emit()),
        ])
        self.setContextMenu(self.menu)
        # 把鼠标点击图标的信号和槽连接
        # self.activated.connect(self.onIconClicked)

    def addAction(self, action: Action):
        """添加新控件"""
        self.menu.addAction(action)

    # def onIconClicked(self, reason):
    # 鼠标点击icon传递的信号会带有一个整形的值
    # 1是表示单击右键，2是双击左键，3是单击左键，4是用鼠标中键点击
