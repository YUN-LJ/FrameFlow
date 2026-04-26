"""弹窗类"""
from SubWidget.ImportPack import *
from SubWidget.Home.SlotFunc import SearchPageCtrl as SPC
from SubWidget.Home.SlotFunc.WorkFlow import DownloadWorkFlow
from SubWidget.Home.DesignFile.ImageDialog import Ui_Image
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from SubWidget.Home.SearchPage import SearchPage


class SearchDialog(LoadDialog):

    def __init__(self, parent: Optional['SearchPage'], top_parent):
        super().__init__(parent=top_parent)
        self.parent = parent
        self.top_parent = top_parent

    def searchStart(self, task: WH.SearchTask):
        """搜索开始"""
        self.setText(f'正在搜索:{task.params.q}的第{task.params.page}页')
        self.yesButton.hide()
        self.cancelButton.show()
        if not self.exec():
            task.stop()

    def searchProgress(self, task: WH.SearchTask):
        """搜索进度"""
        self.progress.show()
        self.progress_indeter.hide()
        self.progress.setValue(task.progress.get_progress())
        self.setText(f'正在搜索:{task.params.q}的第{task.progress.finished}页')

    def searchFinished(self, task: WH.SearchTask):
        """搜索完成"""
        result = task.result()
        if result is not None:
            self.parent.label_page_info.setText(
                f'页码{task.params.page}/'
                f'{result['总页数'].values[0]}|'
                f'总计{result['总数'].values[0]}')
            self.setText('搜索成功!')
            self.yesButton.show()
            self.cancelButton.hide()
            self.parent.spinBox.setValue(result['当前页码'].values[0])
            self.parent.spinBox.setMaximum(result['总页数'].values[0])
        else:
            self.parent.label_page_info.setText('')
            self.setText('搜索失败!')
        QTimer.singleShot(500, self.accept)


class ImageDialog(Ui_Image, MessageBoxBase):
    startSignal = Signal(WH.ImageInfoTask)
    progressSignal = Signal(TaskProgress)  # 进度条更新信号
    finishedSignal = Signal(bool)
    tagClicked = Signal(str)  # 标签被点击时会发送当前被点击的标签值

    def __init__(self, current_cell: SPC.Cell, parent: SPC.Table, top_parent):
        super().__init__(top_parent)
        self.current_cell = current_cell
        self.parent = parent
        self.top_parent = top_parent
        self.column = 4
        self.startSignal.connect(self.__start)
        self.progressSignal.connect(self.__progress)
        self.finishedSignal.connect(self.__finished)
        self.uiInit()
        self.bind()
        self.hideCancelButton()
        self.loadImage(self.current_cell)

    def uiInit(self):
        widget = SimpleCardWidget(self)
        self.setupUi(widget)
        self.image_widget = ImageWidget(parent=self)
        self.image_widget.setMinimumHeight(0)
        self.horizontalLayout.addWidget(self.image_widget)
        self.viewLayout.addWidget(widget)
        self.pushButton_full.setIcon(FIF.FIT_PAGE)
        self.pushButton_copy.setIcon(FIF.COPY)
        self.resizeSize()
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

        def switch_images(index):
            icon = InfoBarIcon.ERROR
            title = '超过范围'
            content = '无图片'
            if 0 <= index < len(self.parent.all_cells):
                self.loadImage(self.parent.all_cells[index])
                icon = InfoBarIcon.SUCCESS
                title = '切换成功'
                content = f'正在加载 {self.work_flow.image_data.image_id}'
            InfoBar.new(
                icon=icon, title=title, content=content, orient=Qt.Horizontal,
                isClosable=True, position=InfoBarPosition.TOP,
                duration=1000, parent=self)

        def pushButton_copy():
            icon = InfoBarIcon.ERROR
            title = '温馨提示'
            content = '正在加载！'
            if self.work_flow.image_data.copy_image():
                icon = InfoBarIcon.SUCCESS
                title = '复制成功'
                content = f'已复制到剪切板 {self.work_flow.image_data.image_id}'
            InfoBar.new(
                icon=icon, title=title, content=content, orient=Qt.Horizontal,
                isClosable=True, position=InfoBarPosition.TOP,
                duration=1000, parent=self)

        AppCore().getSignal('resize').connect(self.resizeSize)
        self.pushButton_copy.clicked.connect(pushButton_copy)  # 将当前的图像数据复制到剪切板中
        self.pushButton_full.clicked.connect(pushButton_full)
        self.pushButton_back.clicked.connect(lambda _: switch_images(
            self.parent.all_cells.index(self.current_cell) - 1))
        self.pushButton_next.clicked.connect(lambda _: switch_images(
            self.parent.all_cells.index(self.current_cell) + 1))

        shortcut_back = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        shortcut_back.activated.connect(self.pushButton_back.click)
        shortcut_next = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        shortcut_next.activated.connect(self.pushButton_next.click)

    def loadImage(self, cell: SPC.Cell):
        """加载图像"""
        self.current_cell = cell
        # 初始化任务
        if hasattr(self, 'work_flow'):
            self.work_flow.stop()
        self.work_flow = DownloadWorkFlow(cell.key_word, cell.image_url, False)
        self.work_flow.setSignal(self.startSignal, self.progressSignal, self.finishedSignal)
        self.work_flow.start()

    def __start(self):
        self.progressBar.setValue(0)
        self.progressBar.show()
        self.clear_layout(self.gridLayout_tags)
        for label in self.scrollAreaWidgetContents.findChildren(QLabel):
            if '_value' in label.objectName():
                label.setText('')
        self.image_widget.set_text('加载中...')
        self.image_widget.setMinimumHeight(0)

    def __progress(self, value: TaskProgress):
        self.progressBar.setValue(value.get_progress())

    def __finished(self, value: bool):
        if value and self.work_flow.image_data.get_image() is not None:
            self.progressBar.hide()
            self.displayTags(self.work_flow.image_data.get_image_info())
            self.image_widget.set_image(self.work_flow.image_data.get_image())
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
        self.widget.setMinimumWidth(self.top_parent.width() * 0.8)
        self.widget.setMinimumHeight(self.top_parent.height() * 0.8)
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


class DelDialog(LoadDialog):
    startSignal = Signal(Task)
    progressSignal = Signal(TaskProgress)
    finishedSignal = Signal(Task)

    def __init__(self, parent: Optional['SearchPage'], top_parent):
        super().__init__(parent=top_parent, show_progress=True)
        self.parent = parent
        self.top_parent = top_parent
        self.image_ids = None  # 正在删除的图片
        self.startSignal.connect(self.__start)
        self.progressSignal.connect(self.__progress)
        self.finishedSignal.connect(self.__finished)

    def __start(self):
        self.yesButton.hide()
        self.cancelButton.show()
        self.setText(f'正在删除 {len(self.image_ids)} 张图片')

    def __progress(self, value: TaskProgress):
        self.progress.setValue(value.get_progress())

    def __finished(self, value: Task):
        if value:
            self.yesButton.show()
            self.cancelButton.hide()
            self.setText(f'成功删除 {len(self.image_ids)} 张图片')
            QTimer.singleShot(1500, lambda: self.accept())
        else:
            self.setText(f'删除失败 {len(self.image_ids)} 张图片')
            QTimer.singleShot(1500, lambda: self.reject())

    def delImage(self, image_ids: list):
        """删除图像"""
        self.image_ids = image_ids
        task = WH.del_image_file(image_ids)
        task.start_signal.connect(self.startSignal.emit)
        task.progress_signal.connect(self.progressSignal.emit)
        task.finish_signal.connect(self.finishedSignal.emit)
        task.start()
        return self.exec()
