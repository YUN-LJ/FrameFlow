"""右侧布局"""
from pyside6_GUI.sub_ui.wallpaper.widgetUI.Config import *


class RightWidget(Ui_rightwidget, QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.__parent = parent
        self.setupUi(self)
        self.uiInit()

    def uiInit(self):
        """界面初始化"""
        self.pushButton_open.setIcon(FIF.FOLDER)
        self.image_widget = ImageWidget()
        self.image_widget.enable_zoom_and_drag()
        self.horizontalLayout_2.addWidget(self.image_widget)

    def setImage(self, image_name, image,
                 image_purity=None, image_categories=None,
                 image_time=None, image_tags=None):
        """
        设置图片
        :param image_name: 图像路径/图像ID
        :param image: 图像数据
        :param image_purity: 图像级别
        :param image_categories: 图像分类
        :param image_time: 图像日期
        :param image_tags: 图像标签
        """
        # 设置文本
        self.lineEdit_name.setText(image_name)
        # 设置图片
        self.image_widget.set_image(image)
