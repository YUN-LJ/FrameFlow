"""
壁纸播放
View->UI文件
ViewLayer->中间层负责处理连接View和WorkerLayer
WorkerLayer->具体的工作层
"""
from SubWidget.WallPaper.ImportPack import *
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
        self.comboBox_mode.currentIndexChanged.connect(self.slot.comboBox_mode)
        self.comboBox.currentIndexChanged.connect(self.slot.comboBox)
        self.pushButton_play.clicked.connect(self.slot.pushButton_play)
        self.spinBox_time.valueChanged.connect(lambda _: self.spinBox_time_timer.start(500))

        # 设置UI初始值
        self.spinBox_time.setValue(WP.Config.IMAGE_TIME)
        self.comboBox_mode.setCurrentIndex(WP.Config.IMAGE_PLAY_MODE)

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

    def comboBox_mode(self, index):
        self.parent.left_widget.stackedWidget.setCurrentIndex(index)
        self.wallpaper_api.set_image_play_mode(index)

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

    def spinBox_time_timer(self):
        value = self.parent.spinBox_time.value()
        self.wallpaper_api.set_image_play_time(value)

    def playImageSignal(self, task: WP.ImageProcessTask):
        self.parent.right_widget.setImage(task.image_original)
        if task.image_info is not None:
            self.parent.right_widget.setTags(task.image_info)
