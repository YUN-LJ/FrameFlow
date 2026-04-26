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
from SubWidget.WallPaper.SlotFunc.DialogWidget import SetDialog


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
        self.bind()

    def uiInit(self):
        # 设置按钮图标
        self.pushButton_set.setIcon(FIF.SETTING)
        self.pushButton_play.setIcon(FIF.PLAY)
        # 创建左右滑动窗口
        self.splitter = LeftandRightSplitter(self.horizontalLayout, parent=self.__parent)
        self.left_widget = LeftWidget(self)
        self.right_widget = RightWidget(self)
        self.splitter.setSizes([800, 500])
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        # 防抖定时器
        self.spinBox_time_timer = QTimer()
        self.spinBox_time_timer.setSingleShot(True)
        self.spinBox_time_timer.timeout.connect(self.slot.spinBox_time_timer)
        # 所有子控件继承样式
        self.setStyleSheet("""WallPaperWin, WallPaperWin * {background-color: transparent;}""")

    def bind(self):
        # 控件信号连接
        self.lineEdit_search.searchSignal.connect(self.slot.lineEdit_search)
        self.lineEdit_search.returnPressed.connect(self.slot.lineEdit_search)
        self.pushButton_set.clicked.connect(self.slot.pushButton_set)
        self.pushButton_play.clicked.connect(self.slot.pushButton_play)
        self.pushButton_select.clicked.connect(self.slot.pushButton_select)
        self.pushButton_cancel_select.clicked.connect(self.slot.pushButton_cancel_select)
        self.spinBox_time.valueChanged.connect(lambda _: self.spinBox_time_timer.start(500))
        # 设置UI初始值
        self.spinBox_time.setValue(WP.Config.IMAGE_TIME)

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
        if self.parent.left_widget.stackedWidget.currentIndex() == WP.Config.IMAGE_KEY_MODE:
            if self.parent.left_widget.tableWidget_key.searchKey(key_word):
                icon = InfoBarIcon.SUCCESS
                title = '成功'
                content = f'已将{key_word}定位到首行'
        if self.parent.isVisible():
            TeachingTip.create(
                target=self.parent.lineEdit_search, icon=icon, title=title, content=content,
                isClosable=True, duration=1000, parent=self.top_parent,
                tailPosition=TeachingTipTailPosition.BOTTOM)

    def startPlaySignal(self):
        self.parent.pushButton_play.setIcon(FIF.PAUSE)
        self.parent.right_widget.image_widget.enable_visibility_optimization()  # 可见性优化

    def pausePlaySignal(self):
        if self.parent.pushButton_play._icon == FIF.PLAY:
            self.parent.pushButton_play.setIcon(FIF.PAUSE)
            self.parent.right_widget.image_widget.enable_visibility_optimization()  # 可见性优化
        else:
            self.parent.pushButton_play.setIcon(FIF.PLAY)
            self.parent.right_widget.image_widget.disable_visibility_optimization()  # 关闭可见性优化

    def pushButton_set(self):
        set_dialog = SetDialog(self.parent)
        set_dialog.exec()

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
        if self.parent.left_widget.stackedWidget.currentIndex() == WP.Config.IMAGE_KEY_MODE:
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
        if self.parent.left_widget.stackedWidget.currentIndex() == WP.Config.IMAGE_KEY_MODE:
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
