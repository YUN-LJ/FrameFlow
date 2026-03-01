"""右侧布局"""
from pyside6_GUI.sub_ui.wallpaper.widgetUI.Config import *


class RightWidget(Ui_rightwidget, QWidget):

    def __init__(self, wallpaper: WallPaperPlay, parent=None):
        super().__init__()
        self.__parent = parent
        self.wallpaper = wallpaper
        self.image_name = None  # 当前图像的名称
        self.image = None  # 当前图像数据
        self.isPause = False  # 是否暂停
        self.colmun = 1  # 网格布局列数
        self.setupUi(self)
        self.uiInit()
        self.bind()

    def uiInit(self):
        """界面初始化"""
        self.pushButton_open.setIcon(FIF.FOLDER)
        self.pushButton_full.setIcon(FIF.FIT_PAGE)
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

        def pause_play(value):
            self.isPause = value
            self.pause_play_timer.start(300)

        self.pushButton_open.clicked.connect(pushButton_open)
        self.pushButton_full.clicked.connect(self.image_widget.showFullScreen)
        # 防抖定时器
        self.pause_play_timer = QTimer()
        self.pause_play_timer.setSingleShot(True)  # 单次触发
        self.pause_play_timer.timeout.connect(lambda: self.wallpaper.pause(self.isPause))
        # 触发暂停信号
        self.image_widget.mousePressSignal.connect(lambda: pause_play(True))  # 鼠标按下时触发暂停
        self.image_widget.mouseWheelSignal.connect(lambda: pause_play(True))  # 鼠标滚轮触发暂停
        self.image_widget.mouseLeaveSignal.connect(lambda: pause_play(False))  # 鼠标离开时结束暂停
        self.image_widget.fullScreenSignal.connect(pause_play)  # 进入全屏时触发暂停,退出全屏时结束暂停

    def setImage(self, image_name, image,
                 ):
        """
        设置图片
        :param image_name: 图像路径
        :param image: 图像数据
        """
        self.image_name = image_name
        self.image = image
        # 设置文本
        self.lineEdit_name.setText(image_name)
        # 设置图片
        self.image_widget.set_image(image)

    def setInfo(self, image_purity: str, image_categories: str,
                image_time: str, image_tags: list):
        """
        设置图像信息

        :param image_purity: 图像级别
        :param image_categories: 图像分类
        :param image_time: 图像日期
        :param image_tags: 图像标签
        """

        # 清空布局
        self.clear_layout(self.gridLayout)
        row = -1
        for index, tag in enumerate(image_tags):
            col = index % self.colmun
            if col == 0:
                row += 1
            button = TransparentPushButton(tag)
            # button.clicked.connect(lambda _, value=tag: self.tag_clicked.emit(value))
            self.gridLayout.addWidget(
                button, row, col, 1, 1
            )

    def clear_layout(self, layout):
        """清空布局中的所有控件"""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)  # 取出并移除第一个项目
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()  # 删除控件
                else:
                    # 如果是子布局，递归删除
                    clear_layout(item.layout())
