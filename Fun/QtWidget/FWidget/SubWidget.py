"""子窗口部件"""
import time
import re
# 基本库
import win32gui, win32con
import numpy as np, sys, subprocess
from screeninfo import get_monitors
from typing import TYPE_CHECKING, Optional
# 自定义库
from Fun.BaseTools import CreateTerminal, Get

if TYPE_CHECKING:
    from Fun.BaseTools.Image import ImageLoad
# PySide6库
from PySide6.QtCore import Qt, QRect, QPoint, QEvent, Signal, QThread, QTimer
from PySide6.QtGui import (QWindow, QIcon, QShortcut, QScreen, QFont, QColor,
                           QPixmap, QPainter, QTextCursor,
                           QWheelEvent, QMouseEvent)
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QSystemTrayIcon, QApplication, QSplitter, QTextEdit
)
# 风格组件
from qfluentwidgets import Action, FluentIcon as FIF, Theme, setTheme
from qfluentwidgets.components.widgets import SystemTrayMenu, TextEdit, LineEdit


class AnsiTextEdit(TextEdit):
    """
    支持ANSI转义序列的文本编辑器
    自动解析ANSI颜色码并渲染为富文本
    """
    # ANSI颜色映射表
    ANSI_COLORS = {
        '30': '#000000',  # Black
        '31': '#FF0000',  # Red
        '32': '#00FF00',  # Green
        '33': '#FFFF00',  # Yellow
        '34': '#0000FF',  # Blue
        '35': '#FF00FF',  # Magenta
        '36': '#00FFFF',  # Cyan
        '37': '#FFFFFF',  # White
        '90': '#808080',  # Bright Black
        '91': '#FF5555',  # Bright Red
        '92': '#55FF55',  # Bright Green
        '93': '#FFFF55',  # Bright Yellow
        '94': '#5555FF',  # Bright Blue
        '95': '#FF55FF',  # Bright Magenta
        '96': '#55FFFF',  # Bright Cyan
        '97': '#FFFFFF',  # Bright White
    }
    ANSI_BG_COLORS = {
        '40': '#000000',  # Black
        '41': '#FF0000',  # Red
        '42': '#00FF00',  # Green
        '43': '#FFFF00',  # Yellow
        '44': '#0000FF',  # Blue
        '45': '#FF00FF',  # Magenta
        '46': '#00FFFF',  # Cyan
        '47': '#FFFFFF',  # White
        '100': '#808080',  # Bright Black
        '101': '#FF5555',  # Bright Red
        '102': '#55FF55',  # Bright Green
        '103': '#FFFF55',  # Bright Yellow
        '104': '#5555FF',  # Bright Blue
        '105': '#FF55FF',  # Bright Magenta
        '106': '#55FFFF',  # Bright Cyan
        '107': '#FFFFFF',  # Bright White
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        # 设置等宽字体以更好地显示终端输出
        self.font_size = 10
        font = QFont("Consolas", self.font_size)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        # 当前样式状态
        self.current_color = None
        self.current_bg_color = None
        self.current_bold = False
        self.current_italic = False
        self.current_underline = False
        # ANSI解析正则表达式
        self.ansi_pattern = re.compile(r'\x1b\[([0-9;]*)m')

    def set_font_size(self, size: int):
        """
        设置字体大小
        
        :param size: 字体大小(磅值)
        """
        if size <= 0:
            return

        self.font_size = size
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)

    def get_font_size(self) -> int:
        """
        获取当前字体大小
        
        :return: 字体大小(磅值)
        """
        return self.font_size

    def increase_font_size(self, step=1):
        """
        增大字体
        
        :param step: 增大的步长
        """
        new_size = self.font_size + step
        self.set_font_size(new_size)

    def decrease_font_size(self, step=1):
        """
        减小字体
        
        :param step: 减小的步长
        """
        new_size = self.font_size - step
        if new_size > 0:
            self.set_font_size(new_size)

    def append_ansi_text(self, text: str):
        """
        追加包含ANSI转义序列的文本
        :param text: 包含ANSI码的原始文本
        """
        if not text:
            return
        cursor = self.textCursor()
        # 按 \r\n 分割文本(保留空字符串以检测连续的\r)
        segments = text.split('\r\n')
        for seg_idx, segment in enumerate(segments):
            if seg_idx > 0:
                # \r\n 表示换行,插入新块
                cursor.insertBlock()
            if not segment:
                continue
            # 在segment内部,按 \r 分割处理覆盖逻辑
            parts = segment.split('\r')
            for part_idx, part in enumerate(parts):
                if part_idx > 0:
                    # \r 表示回到行首并覆盖
                    # 移动到当前行开头
                    cursor.movePosition(QTextCursor.StartOfLine)
                    # 选中到行尾
                    cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                    # 删除旧内容
                    cursor.removeSelectedText()
                if not part:
                    continue
                # 解析ANSI码并插入文本
                ansi_parts = self.ansi_pattern.split(part)
                i = 0
                while i < len(ansi_parts):
                    if i % 2 == 0:
                        # 普通文本部分
                        if ansi_parts[i]:
                            self._insert_formatted_text(cursor, ansi_parts[i])
                    else:
                        # ANSI控制序列部分
                        if ansi_parts[i]:
                            self._parse_ansi_codes(ansi_parts[i])
                    i += 1
        self.setTextCursor(cursor)
        self._scroll_to_bottom()

    def _insert_formatted_text(self, cursor: QTextCursor, text: str):
        """插入格式化文本"""
        # 将换行符转换为块分隔
        lines = text.split('\n')
        for idx, line in enumerate(lines):
            if idx > 0:
                cursor.insertBlock()

            if line:
                # 应用当前样式
                format = cursor.charFormat()

                if self.current_color:
                    format.setForeground(QColor(self.current_color))
                else:
                    format.setForeground(QColor('#AAAAAA'))  # 默认前景色

                if self.current_bg_color:
                    format.setBackground(QColor(self.current_bg_color))

                font = QFont(format.font())
                font.setBold(self.current_bold)
                font.setItalic(self.current_italic)
                font.setUnderline(self.current_underline)
                format.setFont(font)

                cursor.setCharFormat(format)
                cursor.insertText(line)

    def _parse_ansi_codes(self, codes_str: str):
        """解析ANSI控制码"""
        if not codes_str:
            return

        codes = codes_str.split(';')

        for code in codes:
            code = code.strip()
            if not code:
                continue

            # 重置所有属性
            if code == '0':
                self.current_color = None
                self.current_bg_color = None
                self.current_bold = False
                self.current_italic = False
                self.current_underline = False

            # 前景色
            elif code in self.ANSI_COLORS:
                self.current_color = self.ANSI_COLORS[code]

            # 背景色
            elif code in self.ANSI_BG_COLORS:
                self.current_bg_color = self.ANSI_BG_COLORS[code]

            # 粗体
            elif code == '1':
                self.current_bold = True

            # 斜体
            elif code == '3':
                self.current_italic = True

            # 下划线
            elif code == '4':
                self.current_underline = True

            # 默认前景色
            elif code == '39':
                self.current_color = None

            # 默认背景色
            elif code == '49':
                self.current_bg_color = None

    def _scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_ansi(self):
        """清空文本并重置样式"""
        self.clear()
        self.current_color = None
        self.current_bg_color = None
        self.current_bold = False
        self.current_italic = False
        self.current_underline = False


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


class LeftandRightSplitter(QSplitter):
    """左右滑动容器"""

    def __init__(self, layout: QHBoxLayout, *args, **kwargs):
        super().__init__(Qt.Horizontal, *args, **kwargs)
        # 设置初始比例,数字代表宽度像素
        self.setSizes([500, 500])
        # 实时更新
        # self.setOpaqueResize(False)
        layout.addWidget(self)


class EmbeddedWindows(QWidget):
    """将窗口嵌入到PySide6窗口中"""

    def __init__(self, hwnd: int, parent=None):
        """
        :param hwnd:窗口句柄
        """
        super().__init__(parent)
        self.hwnd = hwnd

    def embedWindows(self) -> bool:
        """将窗口嵌入到Pyside6窗口中"""
        if self.hwnd:
            self.layout = QVBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            # 根据窗口句柄嵌入到pyside6界面中
            self.window = QWindow.fromWinId(self.hwnd)
            # 创建一个QWidget用于容纳terminal_window
            self.terminal_widget = QWidget.createWindowContainer(self.window)
            # 将widget_window添加到布局中
            self.layout.addWidget(self.terminal_widget)
            return True
        return False


class EmbeddedPythonTerminal(QWidget):
    """嵌入python启动器终端"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hwnd = None  # 已嵌入的启动器窗口句柄
        self.terminal_window = None  # 已嵌入的窗口

    def embedTerminal(self):
        """将窗口嵌入到Pyside6窗口中"""
        if self.terminal_window is None:
            self.layout = QHBoxLayout(self)
            hwnd = Get.python_cmd_hwnd()
            terminal_window = EmbeddedWindows(hwnd)
            if terminal_window.embedWindows():
                self.hwnd = hwnd
                self.terminal_window = terminal_window
                self.layout.addWidget(terminal_window)

    def show(self):
        super().show()
        self.embedTerminal()

    def closeEvent(self, event):
        super().closeEvent(event)  # 继续执行 Qt 窗口的关闭逻辑
        # 发送关闭消息给外部窗口（Windows API）
        if self.hwnd:
            # WM_CLOSE 消息：通知窗口关闭
            win32gui.SendMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)


class TerminalWidget(QWidget):
    """
    终端显示组件（基于 ConPTY + ansi2html）
    提供 UI 界面展示和交互，通过 HTML 渲染 ANSI 转义序列
    """
    loadFinished = Signal()  # 加载完成

    class TerminalOutputReader(QThread):
        """后台线程读取终端进程输出"""
        output_ready = Signal(str)

        def __init__(self, terminal_process: CreateTerminal, parent=None):
            super().__init__(parent)
            self.terminal_process = terminal_process
            self.running = True

        def run(self):
            """在线程中持续读取输出"""
            while self.running and self.terminal_process.is_running:
                output = self.terminal_process.get_output(False)
                if output:
                    self.output_ready.emit(output)
                self.msleep(5)

        def stop(self):
            """停止读取"""
            self.running = False
            self.wait(3000)

    def __init__(self, auto_start=True, parent=None, terminal_type="cmd", python_path=None):
        """
        初始化终端

        :param parent: 父窗口
        :param terminal_type: 终端类型，"python" 或 "cmd",默认为cmd类型
        :param python_path: Python 解释器路径（仅在 terminal_type="python" 时有效）
        """
        super().__init__(parent)
        self.parent = parent
        self.terminal = CreateTerminal(terminal_type, python_path)
        self.reader_thread: TerminalWidget.TerminalOutputReader = None
        self.__uiInit()
        if auto_start:
            self.startTerminal()

    def __uiInit(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.output_edit = AnsiTextEdit(self.parent)
        layout.addWidget(self.output_edit)

        self.input_line = LineEdit()

        if self.terminal.type == CreateTerminal.TERMINAL_TYPE_PYTHON:
            self.input_line.setPlaceholderText("输入 Python 命令...")
        else:
            self.input_line.setPlaceholderText("输入 CMD 命令...")

        self.input_line.returnPressed.connect(self.sendCommand)
        layout.addWidget(self.input_line)

    def startTerminal(self):
        """启动终端"""
        success, message = self.terminal.start()
        if success:
            # CMD和Python都使用char模式以获得实时输出
            self.reader_thread = self.TerminalOutputReader(self.terminal, self.parent)
            self.reader_thread.output_ready.connect(self.__appendOutput)
            self.reader_thread.start()

    def sendCommand(self, text=None):
        """发送命令到终端"""
        if self.terminal.is_running:
            command = self.input_line.text() if text is None else text
            if command:
                success = self.terminal.send_command(command)
                if success:
                    self.input_line.clear()
                else:
                    self.__appendOutput("发送命令失败\n")

    def __appendOutput(self, text):
        """添加输出文本-增量更新"""
        if not text:
            return
        self.output_edit.append_ansi_text(text)

    def closeEvent(self, event):
        """关闭时清理进程"""
        if self.reader_thread:
            self.reader_thread.stop()
        self.terminal.stop()
        super().closeEvent(event)


class AcondaWidget(TerminalWidget):
    """aconda终端显示"""

    def __init__(self, conda_path, activate_name=None, parent=None):
        """
        :param conda_path:activate路径
        :param activate_name:需要激活的环境
        """
        self.conda_path = conda_path
        self.activate_name = activate_name  # 当前激活的环境,为None时处于继承状态
        super().__init__(False, parent, "cmd")
        self.startTerminal()
        if self.activate_name is not None:
            self.__init_timer = QTimer()
            self.__init_timer.timeout.connect(self.__init_activate)
            self.__init_timer.start(5)

    def __init_activate(self):
        if self.terminal.wait_command:
            self.activateName(self.activate_name)
            self.__init_timer.stop()

    def activateName(self, name):
        self.sendCommand(f'{self.conda_path} {name}')
        self.activate_name = name


if __name__ == '__main__':
    app = QApplication([])
    setTheme(Theme.DARK)
    conda_path = r'E:\code\miniconda3\Scripts\activate.bat'
    window = AcondaWidget(conda_path, 'AutoWallpaper')
    window.output_edit.set_font_size(14)
    # window = TerminalWidget(terminal_type='python')
    window.show()
    app.exec()
