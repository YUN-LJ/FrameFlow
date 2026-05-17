"""图像显示类"""
# 基本库
import gc
import hashlib
import weakref
from io import BytesIO
from typing import Dict, Tuple, Optional
# PySide6库
from PySide6.QtCore import (
    Qt, QRect, QPoint, QEvent, Signal, QObject
)
from PySide6.QtGui import (
    QShortcut, QImage, QPixmap,
    QPainter, QWheelEvent, QMouseEvent,
)
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
# 自定义库
from Fun.BaseTools.Image import ImageLoad


# 风格组件
class ImageManager:
    """全局图像管理器，负责从 BytesIO 加载 QPixmap，自动共享相同内容的图像，管理引用计数和默认图片"""

    _cache: Dict[str, Tuple[QPixmap, int]] = {}  # key=图像内容哈希, value=(QPixmap, refcount)
    _default_pixmap: Optional[QPixmap] = None
    _default_key: str = "__default__"

    @classmethod
    def _get_default_pixmap(cls) -> QPixmap:
        """获取默认空白图片（纯透明，224x224）"""
        if cls._default_pixmap is None:
            default_image = QImage(224, 224, QImage.Format_RGBA8888)
            default_image.fill(Qt.GlobalColor.transparent)
            cls._default_pixmap = QPixmap.fromImage(default_image)
        return cls._default_pixmap

    @classmethod
    def _compute_bytesio_hash(cls, bytesio: BytesIO) -> str:
        """计算 BytesIO 内容的 SHA256 哈希值"""
        pos = bytesio.tell()
        bytesio.seek(0)
        data = bytesio.getvalue()
        hash_value = hashlib.sha256(data).hexdigest()
        bytesio.seek(pos)
        return hash_value

    @classmethod
    def _load_pixmap_from_bytesio(cls, bytesio: BytesIO) -> QPixmap:
        """从 BytesIO 加载 QPixmap"""
        image_load = ImageLoad(bytesio)
        return image_load.get_qpixmap()

    @classmethod
    def acquire_from_bytesio(cls, bytesio: Optional[BytesIO]) -> Tuple[QPixmap, str]:
        """
        从 BytesIO 获取共享的 QPixmap。
        如果 bytesio 为 None 或无效，则返回默认图片和默认键。
        返回: (共享的 QPixmap, 缓存的键)
        """
        if bytesio is None:
            key = cls._default_key
            if key in cls._cache:
                pm, count = cls._cache[key]
                cls._cache[key] = (pm, count + 1)
                return pm, key
            else:
                pm = cls._get_default_pixmap()
                cls._cache[key] = (pm, 1)
                return pm, key

        key = cls._compute_bytesio_hash(bytesio)
        if key in cls._cache:
            pm, count = cls._cache[key]
            cls._cache[key] = (pm, count + 1)
            return pm, key
        else:
            pm = cls._load_pixmap_from_bytesio(bytesio)
            if pm.isNull():
                return cls.acquire_from_bytesio(None)
            cls._cache[key] = (pm, 1)
            return pm, key

    @classmethod
    def release(cls, key: str):
        """释放指定键对应的图像引用计数，若归零则从缓存中删除"""
        if key and key in cls._cache:
            pm, count = cls._cache[key]
            if count <= 1:
                del cls._cache[key]
                # 主动删除pixmap以释放内存
                pm = None
            else:
                cls._cache[key] = (pm, count - 1)

    @classmethod
    def get_image_info(cls, key: str) -> dict:
        """根据键获取图像信息"""
        if key not in cls._cache:
            return {"error": "图像不在缓存中"}
        pm, _ = cls._cache[key]
        if pm.isNull():
            return {"error": "图像为空"}
        image = pm.toImage()
        memory_mb = image.sizeInBytes() / (1024 * 1024)
        return {
            'width': pm.width(),
            'height': pm.height(),
            'memory_mb': memory_mb,
            'has_alpha': pm.hasAlphaChannel()
        }

    @classmethod
    def debug_cache(cls):
        """调试：打印当前缓存内容"""
        for key, (_, cnt) in cls._cache.items():
            print(f"  Key: {key[:16]}... refcount={cnt}")

    @classmethod
    def cleanup_unused(cls):
        """清理未使用的缓存项"""
        keys_to_remove = []
        for key, (pm, count) in cls._cache.items():
            # 尝试检测pixmap是否还有效
            if pm is None or pm.isNull():
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del cls._cache[key]


class FullScreenManager:
    """全屏管理器 - 使用弱引用避免循环"""

    def __init__(self, image_widget: 'ImageWidget'):
        self._image_widget_ref = weakref.ref(image_widget)
        self.fullscreen_window: Optional[QWidget] = None
        self.fullscreen_widget: Optional[QWidget] = None
        self.info_bar: Optional[QWidget] = None
        self.esc_shortcut: Optional[QShortcut] = None

        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)
        self.dragging = False
        self.last_mouse_pos = QPoint()

    @property
    def image_widget(self):
        return self._image_widget_ref()

    def show_full_screen(self, show_info=True):
        widget = self.image_widget
        if widget is None or widget.original_pixmap.isNull():
            return
        if self.fullscreen_window is not None:
            self.exit_full_screen()
            return
        self._create_fullscreen_window()
        self._setup_layout(show_info)
        self._setup_event_handlers()
        if widget:
            widget.isFull = True
            widget.fullScreenSignal.emit(True)

    def exit_full_screen(self):
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

            widget = self.image_widget
            if widget:
                widget.isFull = False
                widget.fullScreenSignal.emit(False)
            gc.collect()

    def _create_fullscreen_window(self):
        self.fullscreen_window = QWidget()
        self.fullscreen_window.setWindowTitle("全屏查看 - 按ESC退出")
        self.fullscreen_window.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.fullscreen_window.showFullScreen()

    def _setup_layout(self, show_info: bool):
        layout = QVBoxLayout(self.fullscreen_window)
        layout.setContentsMargins(0, 0, 0, 0)
        self.fullscreen_widget = QWidget()
        self.fullscreen_widget.setStyleSheet("background-color: black;")
        layout.addWidget(self.fullscreen_widget)
        if show_info:
            self._create_info_bar(layout)

    def _create_info_bar(self, layout: QVBoxLayout):
        self.info_bar = QWidget()
        self.info_bar.setFixedHeight(30)
        self.info_bar.setStyleSheet("background-color: rgba(0,0,0,180); color:white; font-size:12px;")
        info_layout = QHBoxLayout(self.info_bar)
        info_layout.setContentsMargins(10, 0, 10, 0)
        widget = self.image_widget
        if widget:
            info = widget.get_image_info()
            if isinstance(info, dict):
                info_text = f"尺寸: {info.get('width', 0)}×{info.get('height', 0)} | 内存: {info.get('memory_mb', 0):.2f} MB"
            else:
                info_text = str(info)
        else:
            info_text = "无图片"
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color:white;")
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        esc_label = QLabel("按 ESC 退出全屏 | 双击图片恢复原状")
        esc_label.setStyleSheet("color:lightgray;")
        info_layout.addWidget(esc_label)
        layout.addWidget(self.info_bar)

    def _setup_event_handlers(self):
        widget = self.image_widget
        if widget:
            self.fullscreen_window.installEventFilter(widget)
        self.esc_shortcut = QShortcut(Qt.Key.Key_Escape, self.fullscreen_window)
        self.esc_shortcut.activated.connect(self.exit_full_screen)
        self.fullscreen_widget.wheelEvent = self._fullscreen_wheel_event
        self.fullscreen_widget.mousePressEvent = self._fullscreen_mouse_press_event
        self.fullscreen_widget.mouseMoveEvent = self._fullscreen_mouse_move_event
        self.fullscreen_widget.mouseReleaseEvent = self._fullscreen_mouse_release_event
        self.fullscreen_widget.paintEvent = self._fullscreen_paint_event
        self.fullscreen_widget.mouseDoubleClickEvent = self._fullscreen_reset_view
        self.fullscreen_window.mouseDoubleClickEvent = self._fullscreen_window_double_click
        self.fullscreen_widget.update()

    def _fullscreen_paint_event(self, event):
        widget = self.image_widget
        if widget is None or widget.original_pixmap.isNull():
            return
        painter = QPainter(self.fullscreen_widget)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        rect = self._calculate_fullscreen_scaled_rect().translated(self.offset)
        painter.drawPixmap(rect, widget.original_pixmap)
        painter.end()

    def _calculate_fullscreen_scaled_rect(self) -> QRect:
        widget = self.image_widget
        if widget is None:
            return QRect(0, 0, 0, 0)
        wr = self.fullscreen_widget.rect()
        ps = widget.original_pixmap.size()
        ratio = ps.width() / ps.height()
        w_ratio = wr.width() / wr.height()
        if ratio > w_ratio:
            fw = wr.width()
            fh = fw / ratio
        else:
            fh = wr.height()
            fw = fh * ratio
        sw = fw * self.scale_factor
        sh = fh * self.scale_factor
        x = (wr.width() - sw) / 2
        y = (wr.height() - sh) / 2
        return QRect(x, y, sw, sh)

    def _fullscreen_wheel_event(self, event):
        widget = self.image_widget
        if widget is None or widget.original_pixmap.isNull():
            return
        old_scale = self.scale_factor
        old_rect = self._calculate_fullscreen_scaled_rect()
        old_rect_with_offset = old_rect.translated(self.offset)
        mouse_pos = event.position().toPoint()
        delta = event.angleDelta().y()
        self.scale_factor = min(max(self.scale_factor * (1.1 if delta > 0 else 0.909), 0.01), 50.0)
        if abs(self.scale_factor - old_scale) < 0.001:
            return
        if old_rect_with_offset.width() > 0:
            rel_x = (mouse_pos.x() - old_rect_with_offset.x()) / old_rect_with_offset.width()
            rel_y = (mouse_pos.y() - old_rect_with_offset.y()) / old_rect_with_offset.height()
            rel_x = max(0.0, min(1.0, rel_x))
            rel_y = max(0.0, min(1.0, rel_y))
            new_rect = self._calculate_fullscreen_scaled_rect()
            target_x = mouse_pos.x() - rel_x * new_rect.width()
            target_y = mouse_pos.y() - rel_y * new_rect.height()
            self.offset = QPoint(int(target_x - new_rect.x()), int(target_y - new_rect.y()))
        self.fullscreen_widget.update()

    def _fullscreen_mouse_press_event(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.last_mouse_pos = event.position().toPoint()
            self.fullscreen_widget.setCursor(Qt.ClosedHandCursor)
            event.accept()

    def _fullscreen_mouse_move_event(self, event):
        if self.dragging:
            delta = event.position().toPoint() - self.last_mouse_pos
            self.offset += delta
            self.last_mouse_pos = event.position().toPoint()
            self.fullscreen_widget.update()
            event.accept()
        else:
            self.fullscreen_widget.setCursor(Qt.OpenHandCursor if self.scale_factor > 1.0 else Qt.ArrowCursor)

    def _fullscreen_mouse_release_event(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            self.fullscreen_widget.setCursor(Qt.ArrowCursor)
            event.accept()

    def _fullscreen_reset_view(self, event):
        if event.button() == Qt.LeftButton:
            self.scale_factor = 1.0
            self.offset = QPoint(0, 0)
            self.fullscreen_widget.update()
            event.accept()

    def _fullscreen_window_double_click(self, event):
        if event.button() == Qt.LeftButton:
            self._fullscreen_reset_view(event)

    def update_fullscreen(self):
        if self.fullscreen_widget:
            self.fullscreen_widget.update()


class ImageWidget(QWidget):
    """
    enable_zoom_and_drag启用缩放和拖拽
    disable_zoom_and_drag关闭缩放和拖拽
    showFullScreen全屏显示
    防止内存溢出需要主动调用deleteLater方法来清理资源
    """
    mouseEnterSignal = Signal()
    mouseLeaveSignal = Signal()
    mousePressSignal = Signal()
    mouseReleaseSignal = Signal()
    mouseDoubleSignal = Signal()
    mouseWheelSignal = Signal()
    fullScreenSignal = Signal(bool)

    def __init__(self, bytesio: Optional[BytesIO] = None, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)  # 关闭时自动删除C++对象

        self.original_pixmap: QPixmap = ImageManager._get_default_pixmap()
        self._cache_key: Optional[str] = None
        self.display_text: Optional[str] = None
        self.enable_zoom_drag = False
        self.isFull = False
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)
        self.dragging = False
        self.last_mouse_pos = QPoint()

        self.fullscreen_manager = FullScreenManager(self)
        self.setMinimumSize(50, 50)

        if bytesio is not None:
            self.set_image(bytesio)

    def set_image(self, bytesio: Optional[BytesIO]) -> bool:
        if self.display_text is not None:
            self.display_text = None

        new_pm, new_key = ImageManager.acquire_from_bytesio(bytesio)

        # 检查是否是相同的图像，如果是则不需要更新
        if new_key == self._cache_key:
            return False

        # 释放旧图像的引用
        if self._cache_key is not None:
            ImageManager.release(self._cache_key)

        # 设置新图像
        self.original_pixmap = new_pm
        self._cache_key = new_key
        self.reset_view()

        if self.isFull:
            self.fullscreen_manager.update_fullscreen()
        self.update()
        return True

    def set_text(self, text: str):
        self.display_text = text
        # 当设置文本时，释放当前图像的引用
        if self._cache_key is not None:
            ImageManager.release(self._cache_key)
            self._cache_key = None
        self.original_pixmap = QPixmap()
        self.reset_view()
        self.update()

    def reset_view(self):
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)
        self.update()

    def paintEvent(self, event):
        if self.display_text:
            painter = QPainter(self)
            painter.drawText(self.rect(), Qt.AlignCenter, self.display_text)
            return
        if self.original_pixmap.isNull():
            painter = QPainter(self)
            painter.drawText(self.rect(), Qt.AlignCenter, "无图片")
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        rect = self.calculateScaledRect()
        if self.enable_zoom_drag:
            rect.translate(self.offset)
        painter.drawPixmap(rect, self.original_pixmap)

    def calculateScaledRect(self):
        if self.original_pixmap.isNull():
            return QRect(0, 0, 0, 0)
        wr = self.rect()
        ps = self.original_pixmap.size()
        ratio = ps.width() / ps.height()
        w_ratio = wr.width() / wr.height()
        if ratio > w_ratio:
            fw = wr.width()
            fh = fw / ratio
        else:
            fh = wr.height()
            fw = fh * ratio
        sw = fw * self.scale_factor
        sh = fh * self.scale_factor
        x = (wr.width() - sw) / 2
        y = (wr.height() - sh) / 2
        return QRect(x, y, sw, sh)

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

    def wheelEvent(self, event: QWheelEvent):
        if not self.enable_zoom_drag or self.original_pixmap.isNull():
            event.ignore()
            return
        old_scale = self.scale_factor
        old_rect = self.calculateScaledRect().translated(self.offset)
        mouse_pos = event.position().toPoint()
        delta = event.angleDelta().y()
        self.scale_factor = min(max(self.scale_factor * (1.1 if delta > 0 else 0.909), 0.01), 50.0)
        if abs(self.scale_factor - old_scale) < 0.001:
            event.ignore()
            return
        if old_rect.width() > 0:
            rel_x = (mouse_pos.x() - old_rect.x()) / old_rect.width()
            rel_y = (mouse_pos.y() - old_rect.y()) / old_rect.height()
            rel_x = max(0.0, min(1.0, rel_x))
            rel_y = max(0.0, min(1.0, rel_y))
            new_rect = self.calculateScaledRect()
            target_x = mouse_pos.x() - rel_x * new_rect.width()
            target_y = mouse_pos.y() - rel_y * new_rect.height()
            self.offset = QPoint(int(target_x - new_rect.x()), int(target_y - new_rect.y()))
        self.mouseWheelSignal.emit()
        self.update()
        event.accept()

    def can_drag(self):
        if not self.enable_zoom_drag or self.original_pixmap.isNull():
            return False
        sw = self.original_pixmap.width() * self.scale_factor
        sh = self.original_pixmap.height() * self.scale_factor
        return sw > self.width() or sh > self.height()

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
        if self.dragging and self.can_drag():
            delta = event.position().toPoint() - self.last_mouse_pos
            self.offset += delta
            self.last_mouse_pos = event.position().toPoint()
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

    def enterEvent(self, event):
        self.mouseEnterSignal.emit()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.mouseLeaveSignal.emit()
        super().leaveEvent(event)

    def get_image_info(self) -> dict:
        if self._cache_key is None:
            return {"error": "无图像"}
        return ImageManager.get_image_info(self._cache_key)

    def showFullScreen(self, show_info=True):
        self.fullscreen_manager.show_full_screen(show_info)

    def exitFullScreen(self):
        self.fullscreen_manager.exit_full_screen()

    def eventFilter(self, obj, event):
        if self.fullscreen_manager.fullscreen_window and obj == self.fullscreen_manager.fullscreen_window:
            if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
                self.exitFullScreen()
                return True
        return super().eventFilter(obj, event)

    def _cleanup_resources(self):
        """清理资源，释放图像引用"""
        if self._cache_key is not None:
            ImageManager.release(self._cache_key)
            self._cache_key = None
        # 清空pixmap以释放内存
        self.original_pixmap = QPixmap()
        # 清理全屏管理器
        if self.fullscreen_manager:
            self.fullscreen_manager.exit_full_screen()
            self.fullscreen_manager = None

    def closeEvent(self, event):
        """重写closeEvent确保在关闭时清理资源"""
        self._cleanup_resources()
        super().closeEvent(event)

    def deleteLater(self):
        """确保资源删除干净"""
        for object in self.findChildren(QObject):
            object.deleteLater()
        self._cleanup_resources()
        super().deleteLater()

    def isShowImage(self) -> bool:
        """
        判断当前是否显示了有效图像（排除默认图像）
        :return: True表示显示了有效图像，False表示显示默认图像或文本
        """
        # 如果显示的是文本，则没有显示图像
        if self.display_text is not None:
            return False
        
        # 检查是否有缓存key，没有说明没有加载过图像
        if self._cache_key is None:
            return False
        
        # 检查original_pixmap是否有效且不是空图像
        if self.original_pixmap.isNull():
            return False
        
        # 检查是否是默认图像（通过cache_key判断）
        # 如果是默认图像的key，则返回False
        default_pm = ImageManager._get_default_pixmap()
        if not default_pm.isNull() and self.original_pixmap == default_pm:
            return False
        
        return True
