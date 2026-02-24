"""右侧布局"""
from pyside6_GUI.sub_ui.wallpaper.widgetUI.Config import *


class RightWidget(Ui_rightwidget, QWidget):

    def __init__(self, parent=None):
        super().__init__()
        self.__parent = parent
        self.image_name = None  # 当前图像的名称
        self.image = None  # 当前图像数据
        self.setupUi(self)
        self.uiInit()
        self.bind()

    def uiInit(self):
        """界面初始化"""
        self.pushButton_open.setIcon(FIF.FOLDER)
        self.image_widget = ImageWidget()
        self.image_widget.enable_zoom_and_drag()
        self.horizontalLayout_2.addWidget(self.image_widget)

    def bind(self):
        def pushButton_open():
            if self.image_name is not None:
                if file.check_exist(self.image_name):
                    file.open_file_use_explorer(self.image_name)
                else:
                    pass

        self.pushButton_open.clicked.connect(pushButton_open)
        self.pushButton_full.clicked.connect(self.image_widget.showFullScreen)

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
        self.image_name = image_name
        self.image = image
        # 设置文本
        self.lineEdit_name.setText(image_name)
        # 设置图片
        self.image_widget.set_image(image)
