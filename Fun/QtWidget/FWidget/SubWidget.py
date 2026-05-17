"""子窗口部件"""
# 基本库
import win32con
import win32gui
# PySide6库
from PySide6.QtCore import Qt, QRect, QPoint, QEvent
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QApplication
)
# 风格组件
from qfluentwidgets import CardWidget, ScrollArea
from screeninfo import get_monitors


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
        self.dpi = None  # 所在屏幕的DPI
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
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool |  # 工具窗口，不占任务栏
            Qt.WindowType.WindowStaysOnBottomHint)  # 强制最底层
        # 设置窗口尺寸需要以主屏幕DPI来计算
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setFixedSize(self.rect.width(), self.rect.height())

    def embedWidget(self):
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


class FluentWidgetBase(QWidget):
    """
    创建一个内带滑动容器的全透明窗口
    用于适配Fluent包的主窗口风格
    内部自带布局view_layout,可传递布局
    """

    def __init__(self, parent=None, layout=None):
        super().__init__(parent)
        # 创建滚动区域
        self._content_scroll = ScrollArea(self)
        self._content_scroll.setWidgetResizable(True)
        # 创建主布局
        self._layout = QHBoxLayout()
        super().setLayout(self._layout)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._content_scroll)
        # 创建内容容器
        self._content_widget = CardWidget(self)  # 内部滚动窗口
        self._content_scroll.setWidget(self._content_widget)
        if layout is None:
            self.view_layout = QVBoxLayout(self._content_widget)
            self.view_layout.setContentsMargins(0, 0, 0, 0)
        else:
            self.view_layout = layout
            self.view_layout.setContentsMargins(0, 0, 0, 0)
            self._content_widget.setLayout(self.view_layout)
        # 设置全透明
        self.setStyleSheet(f"{self.__class__.__name__}, {self.__class__.__name__}"
                           " * {background-color: transparent;}")

    def setLayout(self, layout):
        """将布局设置代理给 _content_widget"""
        # 设置到_content_widget
        self._content_widget.setLayout(layout)

    def layout(self):
        """获取 _content_widget 的布局"""
        return self._content_widget.layout()

    def addWidget(self, widget):
        """添加控件到 _content_widget 的布局中"""
        if self._content_widget.layout():
            self._content_widget.layout().addWidget(widget)
        else:
            raise RuntimeError("必须先设置布局才能添加控件")

    def addLayout(self, layout):
        """添加子布局到 _content_widget 的布局中"""
        if self._content_widget.layout():
            self._content_widget.layout().addLayout(layout)
        else:
            raise RuntimeError("必须先设置布局才能添加子布局")

    def setContentsMargins(self, left, top, right, bottom):
        """设置内容边距代理给 _content_widget"""
        self._content_widget.setContentsMargins(left, top, right, bottom)

    def contentsMargins(self):
        """获取内容边距从 _content_widget"""
        return self._content_widget.contentsMargins()

    def setSpacing(self, spacing):
        """设置间距（如果布局支持）"""
        if self._content_widget.layout():
            if hasattr(self._content_widget.layout(), 'setSpacing'):
                self._content_widget.layout().setSpacing(spacing)

    def spacing(self):
        """获取间距（如果布局支持）"""
        if self._content_widget.layout():
            if hasattr(self._content_widget.layout(), 'spacing'):
                return self._content_widget.layout().spacing()
        return 0


class FluentWidgetFromUI(FluentWidgetBase):
    """
    从UI文件创建窗口,只需要同时继承FluentWidgetFromUI,UI_object即可
    容器名为self.content_widget
    """

    def __init__(self, parent=None, layout=None, auto_add=True):
        """
        param auto_add:是否自动添加
        """
        super().__init__(parent=None, layout=None)
        if hasattr(self, 'setupUi'):
            self.content_widget = CardWidget(self)
            self.setupUi(self.content_widget)
            if auto_add:
                self.addWidget(self.content_widget)


class SplitterWidget(QSplitter):
    """滑动容器"""
    default_ratio = (500, 500)

    def __init__(self, default_ratio=None, direction=Qt.Orientation.Horizontal, parent=None):
        """
        :param default_ratio:比例,默认采用默认比例,500:500
        :param direction:方向,默认水平方向
        """
        super().__init__(direction, parent=parent)
        # 设置初始比例,数字代表宽度像素
        ratio = self.default_ratio if default_ratio is None else default_ratio
        self.setSizes(ratio)
        self.setOpaqueResize(True)


class SidebarWidgetCover(CardWidget):
    """侧边栏组件 - 支持附身父控件和展开/收起功能（独立窗口模式）"""

    LEFT = 0
    RIGHT = 1
    TOP = 2
    BOTTOM = 3

    def __init__(self, parent, direction=LEFT, default_size=300):
        super().__init__(parent)

        self.direction = direction
        self.isExpanded = False
        self.default_size = default_size

        # 设置为独立弹出窗口，不占用任务栏
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground, True)
        # self.setAttribute(Qt.WA_StyledBackground, True)
        self.setWindowOpacity(0.8)  # 0.0完全透明，1.0不透明

        # 设置初始尺寸
        if direction in [self.LEFT, self.RIGHT]:
            self.setFixedWidth(default_size)
        else:
            self.setFixedHeight(default_size)

        # 安装父对象事件过滤器
        parent.installEventFilter(self)

    def toggle(self, is_expand: bool = None):
        """切换显示/隐藏"""
        self.hide() if self.isExpanded else self.show()

    def _adjustPosition(self):
        """调整位置和尺寸以适应父对象"""
        parent = self.parent()
        # 获取父窗口的全局坐标
        parent_rect = parent.rect()
        parent_global_pos = parent.mapToGlobal(parent_rect.topLeft())
        if self.direction == self.LEFT:
            x = parent_global_pos.x()
            y = parent_global_pos.y()
            height = parent_rect.height()
            self.setGeometry(x, y, self.width(), height)
        elif self.direction == self.RIGHT:
            x = parent_global_pos.x() + parent_rect.width() - self.width()
            y = parent_global_pos.y()
            height = parent_rect.height()
            self.setGeometry(x, y, self.width(), height)
        elif self.direction == self.TOP:
            x = parent_global_pos.x()
            y = parent_global_pos.y()
            width = parent_rect.width()
            self.setGeometry(x, y, width, self.height())
        else:  # BOTTOM
            x = parent_global_pos.x()
            y = parent_global_pos.y() + parent_rect.height() - self.height()
            width = parent_rect.width()
            self.setGeometry(x, y, width, self.height())

    def eventFilter(self, obj, event):
        """事件过滤器"""
        # 监听父对象的移动和调整大小事件
        if obj == self.parent():
            if event.type() in [QEvent.Type.Move, QEvent.Type.Resize]:
                if self.isExpanded:
                    self._adjustPosition()
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        """显示时调整位置并更新状态"""
        self.isExpanded = True
        self._adjustPosition()
        super().showEvent(event)

    def hideEvent(self, event):
        """隐藏时更新状态"""
        self.isExpanded = False
        super().hideEvent(event)

    def resizeEvent(self, event):
        """调整大小时重新定位"""
        self._adjustPosition()
        super().resizeEvent(event)


class SidebarWidget(CardWidget):
    """侧边栏组件 - 支持展开/收起功能"""

    def __init__(self, parent):
        super().__init__(parent)

    def toggle(self):
        """切换显示/隐藏"""
        self.hide() if self.isVisible() else self.show()

# if __name__ == '__main__':
#     from qfluentwidgets import setTheme, Theme
#     from Fun.BaseTools import ImageLoad
#
#
#     def image_test():
#         widn.show()
#         image_widget.close()
#
#
#     image = ImageLoad(r"E:\user_file\Pictures\壁纸\wallhaven\限制级\人物\1k5ll1.jpg")
#
#     app = QApplication([])
#     setTheme(Theme.DARK)
#     image_widget = ImageWidget(image.get_bytesIO())
#     widn = ImageWidget()
#     image_widget.resize(500, 500)
#     image_widget.show()
#     QTimer.singleShot(5000, image_test)
#     app.exec()


# if __name__ == '__main__':
#     app = QApplication([])
#     setTheme(Theme.DARK)
#     # conda_path = r'E:\code\miniconda3\Scripts\activate.bat'
#     # window = AcondaWidget(conda_path, 'AutoWallpaper')
#     # window.output_edit.set_font_size(14)
#     # window = TerminalWidget(terminal_type='python')
#     window_1 = ImageWidget()
#     window_1.show()
#     window = LoadBarDialog('正在加载...', window_1, )
#     window.exec()
#     app.exec()
