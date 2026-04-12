"""FTabel的配套组件用于创建单元格类或一行类"""
# PySide6原生组件
from PySide6.QtCore import Signal, Qt, QTimer, QObject, QPoint
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QTableWidgetItem,
                               QGroupBox, QHeaderView, QStackedWidget, QTableWidget,
                               QAbstractItemView, QWidget, QSizePolicy, QApplication)
# 风格化组件
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets.components.widgets import (
    TableWidget, CheckBox, TitleLabel, IndeterminateProgressRing,
    ProgressRing, PrimaryToolButton
)
from Fun.QtWidget import ImageWidget
from Fun.BaseTools import ImageLoad


class ImageCellBase:
    """
    单元格基类,在调用createWidget方法前修改对应属性的类即可完成替换
    需要同时继承QWidget类或其子类
    """

    def __init__(self):
        self.layout = QVBoxLayout  # 主容器布局
        self.layout_title = QHBoxLayout  # 顶部标头布局
        self.check_box = CheckBox  # 标题按钮
        self.image_widget = ImageWidget  # 图片显示容器

    def uiInit(self, widget, layout, layout_title, check_box):
        """UI初始化"""
        if layout is not None:
            self.layout = layout
        if layout_title is not None:
            self.layout_title = layout_title
        if check_box is not None:
            self.check_box = check_box
        widget.resize(300, 300)
        self.createWidget(widget)

    def createWidget(self, widget):
        """创建子控件实例"""
        # 实例创建
        self.layout = self.layout(widget)
        self.layout_title = self.layout_title(widget)
        self.check_box = self.check_box(widget)
        self.image_widget = self.image_widget(parent=widget)
        # 布局设置
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout_title.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout_title.setSpacing(0)
        # 添加控件
        self.layout.addLayout(self.layout_title)
        self.layout_title.addWidget(self.check_box)
        self.layout.addWidget(self.image_widget)

    def setImage(self, image: ImageLoad | str):
        if not isinstance(image, ImageLoad):
            image = ImageLoad(image)
        self.image_widget.set_image(image)

    def setImageText(self, text: str):
        self.image_widget.set_text(text)

    def setText(self, text: str):
        self.check_box.setText(text)


class ImageCell(QGroupBox, ImageCellBase):
    """基础单元格继承使用示例"""
    checkedChanged = Signal(bool)  # 内部选择按钮状态改变时

    def __init__(self, parent=None, layout=None, layout_title=None, check_box=None):
        QGroupBox.__init__(self, parent)
        ImageCellBase.__init__(self)
        self.uiInit(self, layout, layout_title, check_box)

    def setColor(self, color: str):
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


if __name__ == '__main__':
    app = QApplication([])
    cell = ImageCell()
    cell.setImage(r"E:\user_file\Pictures\壁纸\wallhaven\限制级\人物\1k5o19.jpg")
    cell.show()
    app.exec()
