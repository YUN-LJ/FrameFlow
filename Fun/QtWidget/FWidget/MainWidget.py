"""主窗口部件"""
import darkdetect, sys
# 图形库
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QStackedWidget, QSystemTrayIcon
)
from PySide6.QtCore import QTimer, QSize, QEventLoop, Qt, Signal
from PySide6.QtGui import QIcon
# 美化库
from qframelesswindow.utils import getSystemAccentColor
from qfluentwidgets import (
    FluentIcon as FIF, setTheme, setThemeColor, Theme, SystemTrayMenu,
    Action, NavigationItemPosition, MSFluentWindow, SimpleCardWidget,
    Pivot, SegmentedWidget, SplashScreen
)
from Fun.BaseTools import LogClass

logger = LogClass.get_logger(__name__, console_level='WARNING')

CURRENT_THEME = darkdetect.theme()
THEME_AUTO = 'Auto'
THEME_DARK = 'Dark'
THEME_LIGHT = 'Light'


def change_theme(theme=THEME_AUTO, color=None):
    """
    修改主题
    :param theme:默认根据系统主题来设置
    :param color:默认根据系统主题来设置
    """
    global CURRENT_THEME
    if theme == THEME_AUTO:
        # 获取系统主题
        system_theme = darkdetect.theme()  # 返回字符串 'Dark' 或 'Light'
        if system_theme == 'Dark':
            CURRENT_THEME = 'Dark'
            setTheme(Theme.DARK)
        else:
            CURRENT_THEME = 'Light'
            setTheme(Theme.LIGHT)
    else:
        setTheme(Theme.DARK if theme == THEME_DARK else Theme.LIGHT)
        CURRENT_THEME = theme
    # 全局主题色
    # 只能获取 Windows 和 macOS 的主题色
    if color is None:
        if sys.platform in ["win32", "darwin"]:
            # save=True时对后续创建的对象也会生效,否则只对当前存在的对象生效
            setThemeColor(getSystemAccentColor(), save=False, lazy=True)
    else:
        setThemeColor(color, save=False, lazy=True)


# ---懒加载窗口---
class LazyLoadMS(MSFluentWindow):
    """懒加载的MS风格主界面"""

    def __init__(self, widget_list: list[tuple] = None, lazy=True, windows_icon: str = None):
        """
        :param widget_list:传入列表参数,每个元素的值为(名称,图标,子窗口类名,是否置于底层)
        :param lazy:是否启用懒加载,默认启用
        :param windows_icon:窗口图标
        """
        self.widget_list = widget_list
        self.lazy = lazy
        self.fast_show = True
        super().__init__()
        windows_icon = ':/qfluentwidgets/images/logo.png' if windows_icon is None else windows_icon
        self.setWindowIcon(QIcon(windows_icon))

        # 设置窗口属性，防止最大化时背景被系统覆盖
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)

        # 加载子窗口
        self.load_sub_widget = LoadSubWidget(self)
        # 添加窗口
        for name, icon, widget, bottom in widget_list:
            self.addWidget((name, icon, widget), bottom)
        # 连接页面切换
        self.stackedWidget.currentChanged.connect(self.pageChange)

        # 应用主题
        change_theme()  # 延迟应用会导致窗口最大化时主题不生效

    def addWidget(self, widget: tuple[str, QIcon, QWidget], bottom=False):
        """
        添加子窗口
        :param widget:待添加的子窗口,名称,图标,窗口类
        :param bottom:是否添加到底部,默认从上到下添加
        """
        self.load_sub_widget.addSubWidget(widget[2])
        position = NavigationItemPosition.BOTTOM if bottom else NavigationItemPosition.SCROLL
        self.addSubInterface(SubWidgetBase(widget[0], self), widget[1], widget[0], position=position)

    def pageChange(self, index: int):
        """切换页面时"""
        self.load_sub_widget.pageChange(index)

    def getWidget(self, index) -> 'SubWidgetBase':
        """获取子窗口,索引值与传入的列表顺序一致"""
        return self.stackedWidget.widget(index)

    def notLazyLoad(self, is_show: bool = True):
        """
        非懒加载,带启动动画的加载
        :param is_show:是否显示
        """
        # 如果不是懒加载,则直接加载所有子窗口
        if not self.lazy and self.fast_show:
            # 创建启动页面
            splashScreen = SplashScreen(self.windowIcon(), self)
            splashScreen.setIconSize(QSize(102, 102))
            loop = QEventLoop(self)
            # 在创建其他子页面前先显示主界面
            if is_show:
                super().show()
            for i in range(len(self.widget_list), -1, -1):
                self.load_sub_widget.pageChange(i)
            QTimer.singleShot(1000, loop.quit)
            loop.exec()
            # 隐藏启动页面
            splashScreen.finish()
            self.fast_show = False

    def show(self):
        """显示窗口"""
        # 如果不是懒加载,则直接加载所有子窗口
        if not self.lazy and self.fast_show:
            self.lazyLoad()
        else:
            super().show()


class SubWidgetBase(SimpleCardWidget):
    """子窗口基类,用于占位未加载的子窗口"""

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        # 必须给子界面设置全局唯一的对象名
        self.setObjectName(text.replace(' ', '-'))


class LoadSubWidget:
    """实际用于控制加载子窗口的类"""

    def __init__(self, parent: LazyLoadMS):
        self.parent = parent
        self.page_dict: dict[int, QWidget] = {}  # 子窗口字典{页面索引,页面实际的子类}
        self.page_object: dict[int, QWidget] = {}  # 子窗口实例字典

    def addSubWidget(self, widget_name: QWidget):
        """添加子窗口"""
        self.page_dict[len(self.page_dict)] = widget_name

    def pageChange(self, index: int) -> bool:
        """页面改变时"""
        widget_name = self.page_dict.get(index, False)
        if widget_name:
            sub_widget_base = self.parent.getWidget(index)
            if not sub_widget_base.hBoxLayout.count():
                widget = widget_name(self.parent)
                sub_widget_base.hBoxLayout.addWidget(widget)
                self.page_object[index] = widget
                logger.info(f'已添加子窗口{widget.__class__.__name__}')
            return True
        else:
            return False

    def page_close(self, index: int = None):
        """关闭子窗口"""
        if index is None:
            for widget in self.page_object.values():
                widget.close()
                # widget.deleteLater()
        else:
            widget = self.page_object.get(index, None)
            if widget:
                widget.close()


# ---标签导航---
class TopWidget(SimpleCardWidget):
    """顶端标签导航"""

    def __init__(self, use_segmented: bool = True, parent=None):
        super().__init__(parent)
        self.__parent = parent
        # 可选Pivot/SegmentedWidget
        self.topWidget = SegmentedWidget(self) if use_segmented else Pivot(self)  # 导航栏
        self.stackedWidget = QStackedWidget(self)  # 实际窗口
        self.vBoxLayout = QVBoxLayout(self)
        # 连接信号
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)

        self.vBoxLayout.setContentsMargins(30, 0, 30, 30)
        self.vBoxLayout.addWidget(self.topWidget, 0, Qt.AlignmentFlag.AlignHCenter)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.resize(400, 400)

    def addSubInterface(self, widget: QWidget, object_name: str, text: str):
        """添加子界面"""
        widget.setObjectName(object_name)
        self.stackedWidget.addWidget(widget)
        # 使用全局唯一的 objectName 作为路由键
        self.topWidget.addItem(
            routeKey=object_name,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def onCurrentIndexChanged(self, index):
        """界面切换时触发"""
        widget = self.stackedWidget.widget(index)
        self.topWidget.setCurrentItem(widget.objectName())

    def switchPage(self, value: int | QWidget):
        """
        切换页面
        :param value:支持输入页面索引,窗口对象
        """
        widget = self.stackedWidget.widget(value) if isinstance(value, int) else value
        self.stackedWidget.setCurrentWidget(widget)
        self.topWidget.setCurrentItem(widget.objectName())


# ---系统托盘---
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
