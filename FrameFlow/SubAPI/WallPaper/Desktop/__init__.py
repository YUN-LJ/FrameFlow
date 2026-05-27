"""
壁纸播放,主窗口
"""
from SubAPI.WallPaper.ImportPack import *
from SubAPI.WallPaper import api
from SubAPI.WallPaper.Desktop.DesignFile.MainWidget import Ui_wallpaper
from SubAPI.WallPaper.Desktop.KeyTable import TableWidget
from SubAPI.WallPaper.Desktop.ImageDisplay import ImageDisplay


class WallPaperWin(FluentWidgetFromUI, Ui_wallpaper):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.slot = WallPaperSlot(self)
        self.uiInit()
        self.bind()

    def uiInit(self):
        # 设置按钮图标
        self.pushButton_set.setIcon(FIF.SETTING)
        self.pushButton_play.setIcon(FIF.PLAY)
        # 创建左右滑动窗口
        self.splitter = SplitterWidget(parent=self)
        self.horizontalLayout_2.addWidget(self.splitter)
        # 添加左右窗口
        self.left_widget = TableWidget(self)
        self.right_widget = ImageDisplay(self)
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        # 设置初始比例（必须在添加子控件后）
        self.splitter.setSizes([200, 1000])
        # 隐藏设置窗口
        self.widget_sets.hide()
        # 防抖定时器
        self.spinBox_time_timer = debouncer_timer(self.slot.spinBox_time_timer)

    def bind(self):
        # 控件信号连接
        self.lineEdit_search.searchSignal.connect(self.slot.lineEdit_search)
        self.lineEdit_search.returnPressed.connect(self.slot.lineEdit_search)
        self.pushButton_play.clicked.connect(self.slot.pushButton_play)
        self.pushButton_select.clicked.connect(self.slot.pushButton_select)
        self.pushButton_set.clicked.connect(self.slot.pushButton_set)
        self.pushButton_cancel_select.clicked.connect(self.slot.pushButton_cancel_select)
        self.spinBox_time.valueChanged.connect(lambda _: self.spinBox_time_timer.start(500))
        # 设置UI初始值
        self.spinBox_time.setValue(api.Config.IMAGE_TIME)


class WallPaperSlot:

    def __init__(self, parent: WallPaperWin):
        self.parent = parent
        self.top_parent = GlobalValue.TOP_WINDOWS
        self.wallpaper_api = api.WallPaperAPI()
        self.signal_connect()

    def signal_connect(self):
        """信号连接"""
        signal = SignalConfig.WallPaperSignal.main_signal
        signal.startPlaySignal.connect(self.startPlaySignal)
        signal.pausePlaySignal.connect(self.pausePlaySignal)
        signal.playImageSignal.connect(self.playImageSignal)
        self.wallpaper_api.start_signal.connect(lambda _: signal.startPlaySignal.emit())
        self.wallpaper_api.pause_signal.connect(signal.pausePlaySignal.emit)
        self.wallpaper_api.play_image_signal.connect(signal.playImageSignal.emit)

    @info_bar_decorator
    def lineEdit_search(self, key_word=None):
        key_word = self.parent.lineEdit_search.text() if key_word is None else key_word
        if self.parent.left_widget.stackedWidget.currentIndex() == api.Config.IMAGE_KEY_MODE:
            if self.parent.left_widget.tableWidget_key.searchKey(key_word):
                return True, f'定位{key_word}到首行', self.parent
        return False, f'{key_word} 不存在', self.parent

    def startPlaySignal(self):
        self.parent.pushButton_play.setIcon(FIF.PAUSE)

    def pausePlaySignal(self, paused: bool):
        """paused:是否暂停"""
        icon = FIF.PLAY if paused else FIF.PAUSE
        self.parent.pushButton_play.setIcon(icon)

    def pushButton_play(self):
        if not self.wallpaper_api.isRunning:
            self.wallpaper_api.start()
        elif self.wallpaper_api.isPause:
            self.wallpaper_api.resume()
        else:
            self.wallpaper_api.pause()

    @info_bar_decorator
    def pushButton_select(self):
        key_word = self.parent.lineEdit_search.text()
        if self.parent.left_widget.stackedWidget.currentIndex() == api.Config.IMAGE_KEY_MODE:
            if key_word:
                if self.parent.left_widget.tableWidget_key.searchKey(key_word):
                    self.parent.left_widget.tableWidget_key.selectCell(key_word)
                    return True, f'已选择{key_word}开头的关键词', self.parent
        return False, f'{key_word} 不存在', self.parent

    @info_bar_decorator
    def pushButton_cancel_select(self):
        key_word = self.parent.lineEdit_search.text()
        if self.parent.left_widget.stackedWidget.currentIndex() == api.Config.IMAGE_KEY_MODE:
            if key_word:
                if self.parent.left_widget.tableWidget_key.searchKey(key_word):
                    self.parent.left_widget.tableWidget_key.cancelSelectCell(key_word)
                    return True, f'已取消选择{key_word}开头的关键词', self.parent
        return False, f'{key_word} 不存在', self.parent

    def pushButton_set(self):
        self.parent.widget_sets.toggle()

    def spinBox_time_timer(self):
        value = self.parent.spinBox_time.value()
        self.wallpaper_api.set_image_play_time(value)

    def playImageSignal(self, task: api.ImageProcessTask):
        finished, total = self.wallpaper_api.image_key_mode.get_play_progress()
        self.parent.label_progress.setText(f'当前播放进度:{finished}/{total}')
        self.parent.right_widget.setImage(task.image_original)
        if task.image_info is not None:
            self.parent.right_widget.setTags(task.image_info)


if __name__ == '__main__':
    from SubAPI import start_desktop


    def start():
        win = WallPaperWin()
        win.resize(800, 500)
        win.show()
        return win


    start_desktop(start)
