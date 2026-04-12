"""右侧布局"""
from SubWidget.ImportPack import *
from SubWidget.WallPaper.DesignFile.RightWidget import Ui_rightwidget


class RightWidget(Ui_rightwidget, QWidget):
    tagClicked = Signal(str)  # 标签被点击时会发送当前被点击的标签值

    def __init__(self, parent=None):
        super().__init__()
        self.__parent = parent
        self.column = 4  # 信息显示列数
        self.setupUi(self)
        self.uiInit()
        self.slot = RightWidgetSlot(self)
        self.bind()

    def uiInit(self):
        self.pushButton_copy.setIcon(FIF.COPY)
        self.pushButton_open.setIcon(FIF.FOLDER)
        self.pushButton_full.setIcon(FIF.FIT_PAGE)
        self.checkBox.setOnText('启用自动暂停')
        self.checkBox.setOffText('关闭自动暂停')
        self.checkBox_zoom.setOnText('启用缩放')
        self.checkBox_zoom.setOffText('关闭缩放')
        # 图片显示窗口
        self.image_widget = ImageWidget(parent=self)
        self.horizontalLayout.addWidget(self.image_widget)

    def bind(self):
        self.tagClicked.connect(lambda key_word: AppCore().getSignal('search').emit(key_word))
        self.pushButton_copy.clicked.connect(self.slot.pushButton_copy)
        self.pushButton_open.clicked.connect(self.slot.pushButton_open)
        self.pushButton_full.clicked.connect(self.image_widget.showFullScreen)
        self.checkBox_zoom.checkedChanged.connect(self.slot.checkBox_zoom)

    def setImage(self, image):
        self.image_widget.set_image(ImageLoad(image))

    def setTags(self, image_info: pd.Series):
        """显示标签"""
        tags = image_info['标签']
        row = -1
        self.clear_layout(self.gridLayout_tags)  # 清空已有标签显示
        for label in self.groupBox_info.findChildren(QLabel):  # 清空显示
            if '_value' in label.objectName():
                label.setText('')
        for index, tag in enumerate(tags.split(';')):
            col = index % self.column
            if col == 0: row += 1
            button = TransparentPushButton(tag)
            button.clicked.connect(lambda _, value=tag: self.tagClicked.emit(value))
            self.gridLayout_tags.addWidget(button, row, col, 1, 1)
        self.label_id_value.setText(image_info['id'])
        self.label_category_value.setText(image_info['类别'])
        self.label_purity_value.setText(image_info['分级'])
        self.label_data_value.setText(str(image_info['日期']))
        self.label_file_size_value.setText(f"{round(image_info['文件大小'] / 1024 / 1024, 2)}MB")
        self.label_local_path_value.setText(image_info['本地路径'])
        self.label_remote_path_value.setText(image_info['远程路径'])

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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.groupBox_image.setMinimumHeight(self.height())


class RightWidgetSlot:
    def __init__(self, parent: RightWidget):
        self.parent = parent
        self.wallpaper_api = WPAPI()
        self.bind()

    def bind(self):
        self.parent.image_widget.mouseWheelSignal.connect(self.mousePause)
        self.parent.image_widget.mousePressSignal.connect(self.mousePause)
        self.parent.image_widget.mouseLeaveSignal.connect(self.mouseStart)
        self.parent.image_widget.mouseDoubleSignal.connect(self.mouseStart)
        self.parent.image_widget.fullScreenSignal.connect(self.fullScreenSignal)

    def fullScreenSignal(self, value):
        if self.parent.checkBox.isChecked():
            if value:
                if not self.wallpaper_api.isPause:
                    self.wallpaper_api.pause()
            else:
                if self.wallpaper_api.isPause:
                    self.wallpaper_api.pause()

    def mousePause(self):
        """暂停"""
        if self.parent.checkBox.isChecked() and not self.wallpaper_api.isPause:
            self.wallpaper_api.pause()

    def mouseStart(self):
        """恢复播放"""
        if self.parent.checkBox.isChecked() and self.wallpaper_api.isPause:
            self.wallpaper_api.pause()

    def pushButton_open(self):
        local_path = self.parent.label_local_path_value.text()
        if local_path:
            file.open_file_use_explorer(local_path)

    def pushButton_copy(self):
        local_path = self.parent.label_local_path_value.text()
        if local_path:
            general.copy_files_to_clipboard(local_path)

    def checkBox_zoom(self, checked):
        if checked:
            self.parent.image_widget.enable_zoom_and_drag()
        else:
            self.parent.image_widget.disable_zoom_and_drag()
