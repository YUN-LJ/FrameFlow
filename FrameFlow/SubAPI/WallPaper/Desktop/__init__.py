"""
壁纸播放,主窗口
"""
from SubAPI.WallPaper.ImportPack import *
from SubAPI.WallPaper import api
from SubAPI.WallPaper.Desktop.DesignFile.MainWidget import Ui_wallpaper
from SubAPI.WallPaper.Desktop.KeyTable import TableWidget
from SubAPI.WallPaper.Desktop.SetPage import SetWidget


class WallPaperWin(FluentWidgetFromUI, Ui_wallpaper):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.slot = WallPaperSlot(self)
        self.uiInit()
        self.bind()

    def uiInit(self):
        # 设置按钮图标
        self.pushButton_back.setIcon(FIF.CARE_LEFT_SOLID)
        self.pushButton_next.setIcon(FIF.CARE_RIGHT_SOLID)
        self.pushButton_table_list.setIcon(FIF.MENU)
        self.pushButton_set.setIcon(FIF.SETTING)
        self.pushButton_play.setIcon(FIF.PLAY_SOLID)

        # 分类包窗口
        self.widget_tables = SidebarWidgetCover(self.widget_image_display, SidebarWidgetCover.LEFT)
        self.widget_tables_content = TableWidget(self.widget_tables)
        self.widget_tables_content.set_info_bar_parent(self)
        self.widget_tables.collapseSignal.connect(
            lambda: QTimer.singleShot(10, lambda: self.pushButton_table_list.setEnabled(True))
        )  # 防止展开时重复触发
        self.widget_tables.addWidget(self.widget_tables_content)

        # 设置窗口
        self.widget_sets = SidebarWidgetCover(self.widget_image_display, SidebarWidgetCover.RIGHT)
        self.widget_sets_content = SetWidget(self.widget_sets)
        self.widget_sets.collapseSignal.connect(
            lambda: QTimer.singleShot(10, lambda: self.pushButton_set.setEnabled(True))
        )  # 防止展开时重复触发
        self.widget_sets.addWidget(self.widget_sets_content)

    def bind(self):
        # 控件信号连接
        self.pushButton_play.clicked.connect(self.slot.pushButton_play)
        self.pushButton_set.clicked.connect(self.slot.pushButton_set)
        self.pushButton_table_list.clicked.connect(self.slot.pushButton_table_list)

    def copyCurrentImage(self):
        """复制当前图片"""
        self.widget_image_display.pushButton_copy.click()

    def playCurrentImage(self):
        """播放/暂停当前图片"""
        self.pushButton_play.click()


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

    def startPlaySignal(self):
        self.parent.pushButton_play.setIcon(FIF.PAUSE_BOLD)

    def pausePlaySignal(self, paused: bool):
        """paused:是否暂停"""
        icon = FIF.PLAY_SOLID if paused else FIF.PAUSE_BOLD
        self.parent.pushButton_play.setIcon(icon)

    def pushButton_play(self):
        if not self.wallpaper_api.isRunning:
            self.wallpaper_api.start()
        elif self.wallpaper_api.isPause:
            self.wallpaper_api.resume()
        else:
            self.wallpaper_api.pause()

    def pushButton_set(self):
        self.parent.widget_sets.toggle()
        self.parent.pushButton_set.setEnabled(False)

    def pushButton_table_list(self):
        self.parent.widget_tables.toggle()
        self.parent.pushButton_table_list.setEnabled(False)

    def playImageSignal(self, task: api.ImageProcessTask):
        finished, total = self.wallpaper_api.image_key_mode.get_play_progress()
        if task.image_info is not None:
            self.parent.widget_image_display.setTags(task.image_info)
        self.parent.widget_image_display.setImage(task.image_original)
        self.parent.label_progress.setText(f'当前播放进度:{finished}/{total}')
        self.parent.progressBar.setValue(int((finished / total) * 100))


def start():
    win = WallPaperWin()
    win.resize(800, 500)
    win.show()
    return win


if __name__ == '__main__':
    from SubAPI import StartAPI, StartEnum

    start_api = StartAPI(func=start, console_level=StartEnum.LogLevel.DEBUG)
    start_api.start_thread()
