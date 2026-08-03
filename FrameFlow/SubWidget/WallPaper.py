"""壁纸播放窗口"""
from SubAPI.WallPaper.Desktop import WallPaperWin as backWin

from SubWidget.ImportPack import *


class WallPaperWin(backWin):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._add_timer = QTimer(self)
        self._add_timer.timeout.connect(self._addAction)
        self._add_timer.start(1000)

    def _addAction(self):
        if isinstance(Config.TRAY, TrayIcon):
            Config.TRAY.addAction(Action(FIF.PLAY, '播放/暂停', triggered=self.playCurrentImage))
            Config.TRAY.addAction(Action(FIF.COPY, '复制图像', triggered=self.copyCurrentImage))
            self._add_timer.stop()
