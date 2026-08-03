"""FTabel的配套组件用于创建单元格类或一行类"""
from io import BytesIO
# PySide6原生组件
from PySide6.QtCore import Signal, Qt, QTimer, QObject, QPoint
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QTableWidgetItem, QLayout,
    QGroupBox, QHeaderView, QStackedWidget, QTableWidget,
    QAbstractItemView, QWidget, QSizePolicy, QApplication,
    QGraphicsView, QGraphicsScene, QGraphicsProxyWidget,
)
from PySide6.QtGui import QTransform
# 风格化组件
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets.components.widgets import (
    TableWidget, CheckBox, TitleLabel, IndeterminateProgressRing,
    ProgressRing, PrimaryToolButton, CardWidget, TransparentToolButton,
    SimpleCardWidget,
)
from Fun.QtWidget import ImageWidget
from Fun.BaseTools import ImageLoad


class CardWidgetMouseSignal(CardWidget):
    doubleClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        self.doubleClicked.emit()


class SimpleCardWidgetMouseSignal(SimpleCardWidget):
    doubleClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        self.doubleClicked.emit()


class ImageCellBase:
    """单元格基类类似designer生成的文件使用方法"""

    @property
    def layoutTitle(self) -> QHBoxLayout:
        """标题布局"""
        return self._layout_title

    @property
    def layoutInfo(self) -> QHBoxLayout:
        """信息布局"""
        return self._layout_info

    @property
    def checkBox(self) -> CheckBox:
        """复选框按钮"""
        return self._check_box

    @property
    def moreButton(self) -> TransparentToolButton:
        """底部更多信息按钮"""
        return self._button_info

    def addWidgetToTitle(self, widget: QWidget):
        """添加控件到标题"""
        self.layoutTitle.addWidget(widget)

    def addLayoutToTitle(self, layout: QLayout):
        """添加布局到标题"""
        self.layoutTitle.addLayout(layout)

    def addWidgetToInfo(self, widget: QWidget):
        """添加控件到信息"""
        self.layoutInfo.insertWidget(self.layoutInfo.count() - 2, widget)

    def addLayoutToInfo(self, layout: QLayout):
        """添加布局到信息"""
        self.layoutInfo.insertLayout(self.layoutInfo.count() - 2, layout)

    def showTitle(self):
        """显示标题"""
        try:
            self._widget_title.show()
        except RuntimeError:
            pass

    def hideTitle(self):
        """隐藏标题"""
        try:
            self._widget_title.hide()
        except RuntimeError:
            pass

    def showInfo(self):
        """显示信息"""
        try:
            self._widget_info.show()
        except RuntimeError:
            pass

    def hideInfo(self):
        """隐藏信息"""
        try:
            self._widget_info.hide()
        except RuntimeError:
            pass

    def setupUi(self, widget: QWidget):
        """设置UI"""
        # 主容器布局
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 顶部标头布局
        self._widget_title = QWidget(widget)
        self._layout_title = QHBoxLayout(self._widget_title)
        self._layout_title.setSpacing(5)
        self._layout_title.setContentsMargins(5, 5, 5, 5)

        # 底部信息布局
        self._widget_info = QWidget(widget)
        self._layout_info = QHBoxLayout(self._widget_info)
        self._layout_info.setSpacing(5)
        self._layout_info.setContentsMargins(5, 5, 5, 5)

        # 标题选择按钮
        self._check_box = CheckBox(widget)

        # 图片显示容器
        self.image_widget = ImageWidget(parent=widget)

        # 创建底部 更多 按钮
        self._button_info = TransparentToolButton(FIF.MORE)
        self._button_info.setFixedSize(20, 20)

        # 创建 Graphics 视图和场景
        self._graphics_view = QGraphicsView(self)
        self._graphics_view.setFixedSize(40, 40)  # 设置合适大小
        self._graphics_view.setStyleSheet("background: transparent; border: none;")
        self._graphics_view.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        scene = QGraphicsScene(self)
        self._graphics_view.setScene(scene)

        # 将按钮添加到场景并旋转
        proxy = scene.addWidget(self._button_info)
        proxy.setRotation(90)

        # 添加控件
        layout.addWidget(self._widget_title)
        layout.addWidget(self.image_widget)
        layout.addWidget(self._widget_info)
        layout.setStretch(1, 1)
        self._layout_title.addWidget(self._check_box)
        self._layout_info.addStretch()
        self._layout_info.addWidget(self._graphics_view)

    def setImage(self, image: str | BytesIO):
        if isinstance(image, str):
            self.image_widget.set_image(ImageLoad(image).get_bytesIO())
        elif isinstance(image, BytesIO):
            self.image_widget.set_image(image)

    def setImageText(self, text: str):
        self.image_widget.set_text(text)

    def setText(self, text: str):
        self._check_box.setText(text)

    def setState(self, checked: bool):
        self._check_box.setChecked(checked)


class ImageCell(QWidget, ImageCellBase):
    """基础单元格继承使用示例"""
    checkedChanged = Signal(bool)  # 内部选择按钮状态改变时
    moreButtonClicked = Signal()  # 内部更多信息按钮被点击时
    doubleClicked = Signal()  # 主窗口被点击时

    # 主容器枚举值
    GROUPBOX = 'QGroupBox'
    CARDWIDGET = 'CardWidget'
    GROUPBOX_AND_CARDWIDGET = 'QGroupBox_CardWidget'

    def __init__(self, parent=None, main_widget_type: str = 'QGroupBox'):
        """
        :param parent:父对象
        :param main_widget_type:主容器类型,默认使用GROUPBOX
        """
        super().__init__(parent)
        self._mouse_focus_animation = True  # 启用鼠标焦点动画

        # 主布局
        self.view_layout = QVBoxLayout(self)
        self.view_layout.setContentsMargins(10, 10, 10, 10)
        self.view_layout.setSpacing(0)

        # 主容器
        if main_widget_type == self.GROUPBOX:
            self.main_widget = QGroupBox(self)
            self.card_widget = SimpleCardWidgetMouseSignal(self.main_widget)
            self.setupUi(self.card_widget)

            layout = QVBoxLayout(self.main_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            layout.addWidget(self.card_widget)

        elif main_widget_type == self.CARDWIDGET:
            self.main_widget = CardWidgetMouseSignal(self)
            self.setupUi(self.main_widget)

        elif main_widget_type == self.GROUPBOX_AND_CARDWIDGET:
            self.main_widget = QGroupBox(self)
            self.card_widget = CardWidgetMouseSignal(self.main_widget)
            self.setupUi(self.card_widget)

            layout = QVBoxLayout(self.main_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            layout.addWidget(self.card_widget)

        # 连接信号
        self.checkBox.stateChanged.connect(self.checkedChanged.emit)
        self.moreButton.clicked.connect(lambda _: self.moreButtonClicked.emit())
        if isinstance(self.main_widget, CardWidgetMouseSignal):
            self.main_widget.doubleClicked.connect(self.doubleClicked.emit)
        elif hasattr(self, 'card_widget'):
            self.card_widget.doubleClicked.connect(self.doubleClicked.emit)
        self.image_widget.mouseDoubleSignal.connect(self.doubleClicked.emit)

        # 添加主容器
        self.view_layout.addWidget(self.main_widget)

    def setColor(self, color: str):
        if isinstance(self.main_widget, QGroupBox):
            self.setStyleSheet(f"""
                QGroupBox {{
                    border: 1px solid {color};
                    border-radius: 5px;
                    margin-top: 3px;
                    font-size: 12px;
                    }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 8px 0 8px;
                    color: {color};
                    }}
                    """)

    def setTitle(self, text: str):
        if isinstance(self.main_widget, QGroupBox):
            self.main_widget.setTitle(text)

    def enableMouseFocus(self, enable: bool = True):
        """设置鼠标进入时是否高亮"""
        self._mouse_focus_animation = enable

    def enterEvent(self, event):
        if self._mouse_focus_animation:
            try:
                self.view_layout.setContentsMargins(0, 0, 0, 0)
            except RuntimeError:
                pass
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._mouse_focus_animation:
            try:
                self.view_layout.setContentsMargins(10, 10, 10, 10)
            except RuntimeError:
                pass
        super().leaveEvent(event)

    def deleteLater(self):
        """确保资源删除干净"""
        try:
            for object in self.findChildren(QObject):
                object.deleteLater()
        except RuntimeError:
            pass
        super().deleteLater()


if __name__ == '__main__':
    app = QApplication([])
    cell = ImageCell(main_widget_type=ImageCell.GROUPBOX)
    cell.setImage(r"E:\user_file\Pictures\壁纸\wallhaven\限制级\人物\1k5o19.jpg")
    cell.show()
    app.exec()
