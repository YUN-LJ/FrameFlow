"""对话框文件"""
from pyside6_GUI.sub_ui.home.widgetUI.Config import *


class LoadDialog(MessageBoxBase):
    """加载对话框"""

    def __init__(self, text='', parent=None):
        """
        :param text: 要显示的文本内容
        """
        self.__parent = parent
        self.text = text
        super().__init__(self.__parent)
        self.uiInit()

    def uiInit(self):
        """添加基本控件"""
        # 添加环形进度条
        self.progress = IndeterminateProgressRing()
        self.progress.setFixedSize(50, 50)
        self.progress.setStrokeWidth(4)
        self.viewLayout.addWidget(self.progress)
        # 添加文本
        self.label = TitleLabel(text=self.text)
        self.viewLayout.addWidget(self.label)
        # 隐藏确定和取消按钮
        self.hideYesButton()
        # self.hideCancelButton()
        # 设置最小宽度
        self.widget.setMinimumWidth(300)
        self.widget.setMinimumHeight(200)

    def setText(self, text):
        self.label.setText(text)


class ImageDialog(Ui_Image, MessageBoxBase):
    tag_clicked = Signal(str)  # 标签被点击时会发送当前被点击的标签值

    def __init__(self, parent=None):
        self.__parent = parent
        super().__init__(self.__parent)
        widget = QWidget(self)
        self.setupUi(widget)
        self.image_widget = ImageWidget(DEFAULT_IMAGE)
        self.horizontalLayout.addWidget(self.image_widget)
        self.viewLayout.addWidget(widget)
        self.resize_timer = QTimer()
        self.resize_timer.timeout.connect(self.resizeSize)
        self.resize_timer.start(300)
        self.colmun = 4
        self.bind()
        self.hideCancelButton()

    def bind(self):
        """绑定事件"""
        self.pushButton_full.clicked.connect(lambda _: self.image_widget.showFullScreen())

    def display(self, result):
        if isinstance(result, pd.DataFrame):
            tags = result.iloc[0]['标签']
            row = -1
            for index, tag in enumerate(tags.split(';')):
                col = index % self.colmun
                if col == 0:
                    row += 1
                button = TransparentPushButton(tag)
                button.clicked.connect(lambda _, value=tag: self.tag_clicked.emit(value))
                self.gridLayout.addWidget(
                    button, row, col, 1, 1
                )
        elif isinstance(result, io.BytesIO | str):
            self.image_widget.set_image(result)
        elif isinstance(result, dict):
            value = int(result['progress'] * 100 / result['total']) if result['total'] != 0 else 0
            self.progressBar.setValue(value)

    def finished(self, state):
        if not state and self.isVisible():
            TeachingTip.create(
                target=self.yesButton,
                icon=InfoBarIcon.WARNING,
                title='温馨提示',
                content='加载失败',
                isClosable=True,
                tailPosition=TeachingTipTailPosition.BOTTOM,
                duration=1000,
                parent=self.__parent)
        else:
            self.image_widget.enable_zoom_and_drag()  # 启用拖拽和缩放功能
            self.progressBar.hide()

    def resizeSize(self):
        """与主窗口保持缩放"""
        self.widget.setMinimumWidth(self.__parent.width() * 0.8)
        self.widget.setMinimumHeight(self.__parent.height() * 0.8)


class SetDialog(MessageBoxBase):
    """设置对话框"""

    def __init__(self, wallhaven_api: WallHavenAPI, parent=None):
        """
        :param text: 要显示的文本内容
        """
        self.__parent = parent
        self.wallhaven_api = wallhaven_api
        super().__init__(self.__parent)
        self.uiInit()
        self.bind()

    def uiInit(self):
        """添加基本控件"""
        # 添加路径设置
        layout_dir = QHBoxLayout()
        self.label_dir = TitleLabel(text=self.wallhaven_api.download_dir)
        self.label_dir.setMaximumWidth(self.__parent.width() * 0.8)
        self.pushButton_dir = PrimaryToolButton(FIF.FOLDER_ADD)
        layout_dir.addWidget(self.label_dir)
        layout_dir.addWidget(self.pushButton_dir)
        self.viewLayout.addLayout(layout_dir)
        # 添加线程设置
        layout_num_work = QHBoxLayout()
        self.label_num_work = TitleLabel(text=f'当前线程数量:{self.wallhaven_api.num_work}')
        self.spin_box = SpinBox()
        self.spin_box.setRange(1, 20)
        self.spin_box.setValue(self.wallhaven_api.num_work)
        layout_num_work.addWidget(self.label_num_work)
        layout_num_work.addWidget(self.spin_box)
        self.viewLayout.addLayout(layout_num_work)
        # 添加API设置
        layout_api = QHBoxLayout()
        self.label_api = TitleLabel(text='填写API:')
        self.lineEdit_api = LineEdit()
        self.lineEdit_api.setText(self.wallhaven_api.api_key)
        self.pushButton_api = PrimaryToolButton(FIF.UPDATE)
        layout_api.addWidget(self.label_api)
        layout_api.addWidget(self.lineEdit_api)
        layout_api.addWidget(self.pushButton_api)
        self.viewLayout.addLayout(layout_api)
        # 隐藏取消按钮
        self.hideCancelButton()

    def bind(self):
        """绑定按钮"""

        def pushButton_dir():
            save_dir = get_exist_dir('选择保存路径', self.wallhaven_api.download_dir)
            if save_dir:
                self.wallhaven_api.set_download_dir(save_dir)
                self.label_dir.setText(save_dir)

        def pushButton_api():
            api = self.lineEdit_api.text()
            if self.wallhaven_api.set_api_key(api):
                TeachingTip.create(
                    target=self.pushButton_api,
                    icon=InfoBarIcon.SUCCESS,
                    title='温馨提示',
                    content='修改成功,重启后生效。',
                    isClosable=True,
                    tailPosition=TeachingTipTailPosition.BOTTOM,
                    duration=1000,
                    parent=self.__parent)
            else:
                TeachingTip.create(
                    target=self.pushButton_api,
                    icon=InfoBarIcon.ERROR,
                    title='温馨提示',
                    content='修改失败',
                    isClosable=True,
                    tailPosition=TeachingTipTailPosition.BOTTOM,
                    duration=1000,
                    parent=self.__parent)

        def spin_box_value_changed(num_work):
            self.wallhaven_api.set_num_work(num_work)
            self.label_num_work.setText(f'当前线程数量:{self.wallhaven_api.num_work}')
            TeachingTip.create(
                target=self.spin_box,
                icon=InfoBarIcon.SUCCESS,
                title='温馨提示',
                content=f'修改成功,重启后生效。',
                isClosable=True,
                tailPosition=TeachingTipTailPosition.BOTTOM,
                duration=1000,
                parent=self.__parent)

        self.pushButton_dir.clicked.connect(pushButton_dir)
        self.pushButton_api.clicked.connect(pushButton_api)
        self.spin_box.valueChanged.connect(spin_box_value_changed)
        self.yesButton.clicked.connect(self.accept)
