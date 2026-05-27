"""弹窗类"""
from SubAPI.WallHaven.ImportPack import *
from SubAPI.WallHaven.api.WorkFlow import DownloadWorkFlow, ImageInfoTask
from SubAPI.WallHaven.Desktop.SearchPage.DesignFile.ImageDialog import Ui_Image


class ImageDialog(Ui_Image, MessageBoxBase):
    startSignal = Signal(DownloadWorkFlow)
    progressSignal = Signal(DownloadWorkFlow)  # 进度条更新信号
    finishedSignal = Signal(object)  # 完成信号
    tagClicked = Signal(str)  # 标签被点击时会发送当前被点击的标签值

    def __init__(self, current_data: pd.Series, search_data: pd.DataFrame):
        """
        :param current_data:当前显示的数据
        :param search_data:搜素到的数据(该关键词数据)
        """
        super().__init__(GlobalValue.TOP_WINDOWS)
        self.current_data = current_data
        self.search_data = search_data
        self.column = 4
        self.startSignal.connect(self.__start)
        self.progressSignal.connect(self.__progress)
        self.finishedSignal.connect(self.__finished)

        # 图像加载定时器,防抖
        self.loadImage_timer = QTimer()
        self.loadImage_timer.setSingleShot(True)
        self.loadImage_timer.timeout.connect(self.loadImage)

        self.uiInit()
        self.bind()
        self.loadImage_timer.start(100)

    def uiInit(self):
        widget = SimpleCardWidget(self)
        self.setupUi(widget)
        self.image_widget = ImageWidget(parent=self)
        self.image_widget.setMinimumHeight(0)
        self.horizontalLayout.addWidget(self.image_widget)
        self.viewLayout.addWidget(widget)
        self.pushButton_full.setIcon(FIF.FIT_PAGE)
        self.pushButton_copy.setIcon(FIF.COPY)
        self.resize_timer = QTimer()
        self.resize_timer.timeout.connect(self.resizeSize)
        self.resize_timer.start(100)

        self.hideCancelButton()
        # 所有子控件继承样式
        widget.setStyleSheet("""ImageDialog, ImageDialog * {background-color: transparent;}""")

    def bind(self):
        """绑定事件"""

        def pushButton_full():
            self.image_widget.showFullScreen()
            shortcut_back = QShortcut(QKeySequence(Qt.Key.Key_Left),
                                      self.image_widget.fullscreen_manager.fullscreen_widget)
            shortcut_back.activated.connect(self.pushButton_back.click)
            shortcut_next = QShortcut(QKeySequence(Qt.Key.Key_Right),
                                      self.image_widget.fullscreen_manager.fullscreen_widget)
            shortcut_next.activated.connect(self.pushButton_next.click)

        @info_bar_decorator
        def switch_images(index):
            try:
                if index < 0:
                    raise IndexError
                self.current_data = self.search_data.iloc[index]
            except IndexError:
                return False, '没有更多图片了', self
            self.loadImage_timer.start(100)
            return True, f'正在加载 {self.current_data['id']}', self

        @info_bar_decorator
        def pushButton_copy():
            if self.work_flow.image_data is not None:
                image_path = self.work_flow.image_data.image_path
                if image_path:
                    FileBase(image_path).copy_to_clipboard()
                    return True, f'已复制到剪切板{self.work_flow.image_data.image_id}', self
            return False, '没有图片数据', self

        self.pushButton_copy.clicked.connect(pushButton_copy)  # 将当前的图像数据复制到剪切板中
        self.pushButton_full.clicked.connect(pushButton_full)
        self.pushButton_back.clicked.connect(lambda _: switch_images(
            self.current_data.name - 1))
        self.pushButton_next.clicked.connect(lambda _: switch_images(
            self.current_data.name + 1))

        shortcut_back = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        shortcut_back.activated.connect(self.pushButton_back.click)
        shortcut_next = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        shortcut_next.activated.connect(self.pushButton_next.click)

    def loadImage(self):
        """加载图像"""
        # 初始化任务
        if hasattr(self, 'work_flow'):
            self.work_flow.stop()
        params = DownloadWorkFlow.Params(
            self.current_data['id'], key_word=self.current_data['关键词'], url=self.current_data['远程路径'], save=False
        )
        self.work_flow = DownloadWorkFlow(params)
        self.work_flow.setSignal(self.startSignal, self.progressSignal, self.finishedSignal)
        self.work_flow.start(priority=2)

    def __start(self):
        self.progressBar.setValue(0)
        self.progressBar.show()
        self.clear_layout(self.gridLayout_tags)
        for label in self.scrollAreaWidgetContents.findChildren(QLabel):
            if '_value' in label.objectName():
                label.setText('')
        self.image_widget.set_text('加载中...')
        self.image_widget.setMinimumHeight(0)

    def __progress(self, value: DownloadWorkFlow):
        self.progressBar.setValue(value.get_progress())

    def __finished(self, value: ImageInfoTask | DownloadWorkFlow):
        if isinstance(value, ImageInfoTask):
            if value.result() is not None:
                self.displayTags(value.result())
        elif isinstance(value, DownloadWorkFlow):
            if value.result() is not None and value.params.image_id == self.current_data['id']:
                self.progressBar.hide()
                self.image_widget.set_image(value.result().image.get_bytesIO())
                self.image_widget.setMinimumHeight(self.widget.height())
            else:
                self.image_widget.set_text('加载失败')

    def displayTags(self, image_info: pd.DataFrame):
        """显示标签"""
        tags = image_info.iloc[0]['标签']
        row = -1
        self.clear_layout(self.gridLayout_tags)
        for index, tag in enumerate(tags.split(';')):
            col = index % self.column
            if col == 0:
                row += 1
            button = TransparentPushButton(tag)
            button.clicked.connect(lambda _, value=tag: self.tagClicked.emit(value))
            self.gridLayout_tags.addWidget(button, row, col, 1, 1)
        self.label_id_value.setText(image_info.iloc[0]['id'])
        self.label_category_value.setText(image_info.iloc[0]['类别'])
        self.label_purity_value.setText(image_info.iloc[0]['分级'])
        self.label_data_value.setText(str(image_info.iloc[0]['日期']))
        self.label_file_size_value.setText(f"{round(image_info.iloc[0]['文件大小'] / 1024 / 1024, 2)}MB")
        self.label_local_path_value.setText(image_info.iloc[0]['本地路径'])
        self.label_remote_path_value.setText(image_info.iloc[0]['远程路径'])

    def resizeSize(self):
        """与主窗口保持缩放"""
        self.widget.setMinimumWidth(GlobalValue.TOP_WINDOWS.width() * 0.8)
        self.widget.setMinimumHeight(GlobalValue.TOP_WINDOWS.height() * 0.8)
        text = Str.char_auto_line_break(self.label_local_path_value.text().replace('\n', ''),
                                        self.widget.width() * 0.6)
        self.label_local_path_value.setText(text)

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
                    self.clear_layout(item.layout())

    def deleteLater(self):
        """确保资源删除干净"""
        self.work_flow.stop()
        self.resize_timer.stop()
        for object in self.findChildren(QObject):
            object.deleteLater()
        super().deleteLater()
