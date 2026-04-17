"""主窗口部件"""
# 图形库
from PySide6.QtWidgets import QHBoxLayout, QWidget
from PySide6.QtCore import QTimer, QSize, QEventLoop
from PySide6.QtGui import QIcon
# 美化库
from qfluentwidgets import SplashScreen, NavigationItemPosition, MSFluentWindow, SimpleCardWidget


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

        # 加载子窗口
        self.load_sub_widget = LoadSubWidget(self)
        # 添加窗口
        for name, icon, widget, bottom in widget_list:
            self.addWidget((name, icon, widget), bottom)
        # 连接页面切换
        self.stackedWidget.currentChanged.connect(self.pageChange)

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
                print(f'已添加子窗口{widget.__class__.__name__}')
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
