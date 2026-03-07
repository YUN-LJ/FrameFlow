"""对话框文件"""
from pyside6_GUI.sub_ui.home.ImportPack import *


class ImageDialog(Ui_Image, MessageBoxBase):
    tagClicked = Signal(str)  # 标签被点击时会发送当前被点击的标签值
    tagsUpdateSignal = Signal(Task)  # 标签更新信号

    def __init__(self, wallhaven_api: WallHavenAPI, cell: GroupBoxCell, all_cell: list, parent=None):
        """
        :param wallhaven_api: WallHavenAPI
        :param cell: GroupBoxCell 当前单元格
        :param all_cell: list 全部单元格
        """
        self.__parent = parent
        super().__init__(self.__parent)
        self.wallhaven_api = wallhaven_api
        self.cell = cell  # 当前显示的单元格
        self.all_cell = all_cell  # 全部单元格
        self.tags_task: Task = None  # 当前标签任务
        self.download_task: Task = None  # 当前图像加载任务
        self.progress_timer = QTimer()  # 用于显示图像加载进度
        self.progress_timer.timeout.connect(self.displayImage)
        self.colmun = 4
        self.uiInit()
        self.bind()
        self.hideCancelButton()
        self.load_image_tags(self.cell)

    def uiInit(self):
        widget = QWidget(self)
        self.setupUi(widget)
        self.image_widget = ImageWidget()
        self.image_widget.setMinimumHeight(0)
        self.horizontalLayout.addWidget(self.image_widget)
        self.viewLayout.addWidget(widget)
        self.pushButton_full.setIcon(FIF.FIT_PAGE)

    def bind(self):
        """绑定事件"""

        def switch_images(index):
            if 0 <= index < len(self.all_cell):
                self.load_image_tags(self.all_cell[index])

        self.resize_timer = QTimer()
        self.resize_timer.timeout.connect(self.resizeSize)
        self.resize_timer.start(300)
        self.tagsUpdateSignal.connect(self.displayTags)
        self.pushButton_full.clicked.connect(lambda _: self.image_widget.showFullScreen())
        self.pushButton_back.clicked.connect(lambda _: switch_images(self.all_cell.index(self.cell) - 1))
        self.pushButton_next.clicked.connect(lambda _: switch_images(self.all_cell.index(self.cell) + 1))
        shortcut_back = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        shortcut_back.activated.connect(self.pushButton_back.click)
        shortcut_next = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        shortcut_next.activated.connect(self.pushButton_next.click)

    def load_image_tags(self, cell: GroupBoxCell):
        self.cell = cell
        self.image_widget.set_image(self.image_widget.defaultImage)
        image_id = cell.getText()
        image_path = cell.image_path['image']
        if self.tags_task is not None:
            self.tags_task.cancel()
        if self.download_task is not None:
            self.download_task.cancel()
        # UI清理
        self.clear_layout(self.gridLayout_tags)
        for lable in self.scrollAreaWidgetContents.findChildren(QLabel):
            if '_value' in lable.objectName():
                lable.setText('')
        self.image_widget.setMinimumHeight(0)
        # 创建新的任务
        self.tags_task = self.wallhaven_api.get_tags_task(image_id)
        self.download_task = self.wallhaven_api.get_download_task(image_path)
        self.wallhaven_api.add_task(self.tags_task)
        self.wallhaven_api.add_task(self.download_task)
        self.tags_task.add_done_callback(self.tagsUpdateSignal.emit)

        self.progress_timer.start(200)

    def displayTags(self, task: Task):
        """显示标签"""
        result = task.result()
        tags = result.iloc[0]['标签']
        row = -1
        self.clear_layout(self.gridLayout_tags)
        for index, tag in enumerate(tags.split(';')):
            col = index % self.colmun
            if col == 0:
                row += 1
            button = TransparentPushButton(tag)
            button.clicked.connect(lambda _, value=tag: self.tagClicked.emit(value))
            self.gridLayout_tags.addWidget(
                button, row, col, 1, 1
            )
        self.label_id_value.setText(result.iloc[0]['id'])
        self.label_category_value.setText(result.iloc[0]['类别'])
        self.label_purity_value.setText(result.iloc[0]['分级'])
        self.label_data_value.setText(str(result.iloc[0]['日期']))
        self.label_file_size_value.setText(f"{round(result.iloc[0]['文件大小'] / 1024 / 1024, 2)}MB")
        self.label_local_path_value.setText(result.iloc[0]['本地路径'])
        self.label_remote_path_value.setText(result.iloc[0]['远程路径'])

    def displayImage(self):
        """显示图片"""
        if self.download_task is not None:
            task = self.download_task
            if not task.done():
                value = int((task.progress.finished / task.progress.total) * 100) if task.progress.total != 0 else 0
                self.progressBar.setValue(value)
            elif not task.cancelled() and task.result():
                self.progress_timer.stop()
                self.progressBar.setValue(100)
                image_data: ImageData = task.result()
                self.image_widget.set_image(image_data.get_image())
                self.image_widget.setMinimumHeight(self.widget.height())

    def resizeSize(self):
        """与主窗口保持缩放"""
        self.widget.setMinimumWidth(self.__parent.width() * 0.8)
        self.widget.setMinimumHeight(self.__parent.height() * 0.8)

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
