"""
壁纸播放
View->UI文件
ViewLayer->中间层负责处理连接View和WorkerLayer
WorkerLayer->具体的工作层
"""
from SubWidget.ImportPack import *
from SubWidget.WallPaper.DesignFile.MainWidget import Ui_wallpaper
from SubWidget.WallPaper.LeftWidget import LeftWidget
from SubWidget.WallPaper.RightWidget import RightWidget


class WallPaperWin(QWidget, Ui_wallpaper):
    startPlaySignal = Signal()  # 播放开始信号
    pausePlaySignal = Signal()  # 播放停止信号
    playImageSignal = Signal(WP.ImageProcessTask)  # 播放的图片信号

    def __init__(self, parent=None):
        self.__parent = self if parent is None else parent
        super().__init__(self.__parent)
        self.slot = WallPaperSlot(self, self.__parent)
        self.setupUi(self)
        self.uiInit()
        # 所有子控件继承样式
        self.setStyleSheet("""WallPaperWin, WallPaperWin * {background-color: transparent;}""")
        self.bind()

    def uiInit(self):
        # 设置按钮图标
        self.pushButton_set.setIcon(FIF.SETTING)
        self.pushButton_play.setIcon(FIF.PLAY)
        self.checkBox_use_tag.setOnText('使用标签')
        self.checkBox_use_tag.setOffText('使用关键词')
        self.checkBox_use_tag.hide()
        # 创建左右滑动窗口
        self.splitter = LeftandRightSplitter(self.horizontalLayout, parent=self.__parent)
        self.left_widget = LeftWidget(self)
        self.right_widget = RightWidget(self)
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        # 防抖定时器
        self.spinBox_time_timer = QTimer()
        self.spinBox_time_timer.setSingleShot(True)
        self.spinBox_time_timer.timeout.connect(self.slot.spinBox_time_timer)

    def bind(self):
        # 控件信号连接
        self.lineEdit_search.searchSignal.connect(self.slot.lineEdit_search)
        self.lineEdit_search.returnPressed.connect(self.slot.lineEdit_search)
        self.comboBox_mode.currentIndexChanged.connect(self.slot.comboBox_mode)
        self.comboBox.currentIndexChanged.connect(self.slot.comboBox)
        self.pushButton_play.clicked.connect(self.slot.pushButton_play)
        self.pushButton_select.clicked.connect(self.slot.pushButton_select)
        self.pushButton_cancel_select.clicked.connect(self.slot.pushButton_cancel_select)
        self.spinBox_time.valueChanged.connect(lambda _: self.spinBox_time_timer.start(500))
        self.checkBox_use_tag.checkedChanged.connect(self.slot.checkBox_use_tag)

        # 设置UI初始值
        self.spinBox_time.setValue(WP.Config.IMAGE_TIME)
        self.comboBox_mode.setCurrentIndex(WP.Config.IMAGE_PLAY_MODE)
        self.comboBox.setCurrentIndex(WP.Config.IMAGE_PLAY_SORT)

    def closeEvent(self, event):
        super().closeEvent(event)
        WP.save_config()
        WPAPI().stop()


class WallPaperSlot:

    def __init__(self, parent: WallPaperWin, top_parent):
        self.parent = parent
        self.top_parent = top_parent
        self.wallpaper_api = WPAPI()
        self.bind()

    def bind(self):
        """信号连接"""
        self.parent.startPlaySignal.connect(self.startPlaySignal)
        self.parent.pausePlaySignal.connect(self.pausePlaySignal)
        self.parent.playImageSignal.connect(self.playImageSignal)
        self.wallpaper_api.start_signal.connect(lambda _: self.parent.startPlaySignal.emit())
        self.wallpaper_api.pause_signal.connect(lambda _: self.parent.pausePlaySignal.emit())
        self.wallpaper_api.play_image_signal.connect(lambda value: self.parent.playImageSignal.emit(value))

    def lineEdit_search(self, key_word=None):
        key_word = self.parent.lineEdit_search.text() if key_word is None else key_word
        icon = InfoBarIcon.ERROR
        title = '失败'
        content = f'{key_word} 不存在'
        if self.parent.comboBox_mode.currentIndex() == WP.Config.IMAGE_KEY_MODE:
            if self.parent.left_widget.tableWidget_key.searchKey(key_word):
                icon = InfoBarIcon.SUCCESS
                title = '成功'
                content = f'已将{key_word}定位到首行'
        if self.parent.isVisible():
            TeachingTip.create(
                target=self.parent.lineEdit_search, icon=icon, title=title, content=content,
                isClosable=True, duration=1000, parent=self.top_parent,
                tailPosition=TeachingTipTailPosition.BOTTOM)

    def comboBox_mode(self, index):
        if index == WP.Config.IMAGE_KEY_MODE:
            self.parent.checkBox_use_tag.show()
        else:
            self.parent.checkBox_use_tag.hide()
        self.parent.left_widget.stackedWidget.setCurrentIndex(index)
        self.wallpaper_api.set_image_play_mode(index)

    def checkBox_use_tag(self, checked):
        if checked:
            for cell in self.parent.left_widget.tableWidget_key.all_cells.values():
                cell.checkBox.setEnabled(False)
            self.wallpaper_api.image_key_mode.enable_tags_mode(True)
        else:
            for cell in self.parent.left_widget.tableWidget_key.all_cells.values():
                cell.checkBox.setEnabled(True)
            self.wallpaper_api.image_key_mode.enable_tags_mode(False)

    def comboBox(self, index):
        self.wallpaper_api.set_sample(bool(index))

    def startPlaySignal(self):
        self.parent.pushButton_play.setIcon(FIF.PAUSE)
        self.parent.pushButton_play.setText('停止')

    def pausePlaySignal(self):
        if self.parent.pushButton_play.text() == '播放':
            self.parent.pushButton_play.setIcon(FIF.PAUSE)
            self.parent.pushButton_play.setText('停止')
        else:
            self.parent.pushButton_play.setIcon(FIF.PLAY)
            self.parent.pushButton_play.setText('播放')

    def pushButton_play(self):
        if not self.wallpaper_api.image_play.isRunning:
            self.wallpaper_api.start()
        else:
            self.wallpaper_api.pause()

    def pushButton_select(self):
        key_word = self.parent.lineEdit_search.text()
        icon = InfoBarIcon.ERROR
        title = '失败'
        content = f'{key_word} 不存在'
        if self.parent.comboBox_mode.currentIndex() == WP.Config.IMAGE_KEY_MODE:
            if key_word:
                if self.parent.left_widget.tableWidget_key.searchKey(key_word):
                    self.parent.left_widget.tableWidget_key.selectCell(key_word)
                    icon = InfoBarIcon.SUCCESS
                    title = '成功'
                    content = f'已成功选择{key_word}开头的关键词'
            else:
                self.parent.left_widget.tableWidget_key.selectCell()
                icon = InfoBarIcon.SUCCESS
                title = '成功'
                content = f'已成功选择全部的关键词'
        if self.parent.isVisible():
            TeachingTip.create(
                target=self.parent.pushButton_select, icon=icon, title=title, content=content,
                isClosable=True, duration=1000, parent=self.top_parent,
                tailPosition=TeachingTipTailPosition.BOTTOM)

    def pushButton_cancel_select(self):
        key_word = self.parent.lineEdit_search.text()
        icon = InfoBarIcon.ERROR
        title = '失败'
        content = f'{key_word} 不存在'
        if self.parent.comboBox_mode.currentIndex() == WP.Config.IMAGE_KEY_MODE:
            if key_word:
                if self.parent.left_widget.tableWidget_key.searchKey(key_word):
                    self.parent.left_widget.tableWidget_key.cancelSelectCell(key_word)
                    icon = InfoBarIcon.SUCCESS
                    title = '成功'
                    content = f'已成功取消{key_word}开头的关键词'
            else:
                self.parent.left_widget.tableWidget_key.cancelSelectCell()
                icon = InfoBarIcon.SUCCESS
                title = '成功'
                content = f'已成功取消全部的关键词'
        if self.parent.isVisible():
            TeachingTip.create(
                target=self.parent.pushButton_cancel_select, icon=icon, title=title, content=content,
                isClosable=True, duration=1000, parent=self.top_parent,
                tailPosition=TeachingTipTailPosition.BOTTOM)

    def spinBox_time_timer(self):
        value = self.parent.spinBox_time.value()
        self.wallpaper_api.set_image_play_time(value)

    def playImageSignal(self, task: WP.ImageProcessTask):
        finished, total = self.wallpaper_api.image_key_mode.get_play_progress()
        self.parent.label_progress.setText(f'当前播放进度:{finished}/{total}')
        self.parent.right_widget.setImage(task.image_original)
        if task.image_info is not None:
            self.parent.right_widget.setTags(task.image_info)
