"""
设置窗口
"""
from SubWidget.ImportPack import *
from SubAPI.Settings.Desktop import BaseSetWin
from SubAPI.WallHaven.Desktop.SetPage import SetPage as WHSet


class SetsWin(BaseSetWin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.wallhaven_set = WHSet(self)
        self.addSetWidget(self.wallhaven_set)


if __name__ == '__main__':
    app = QApplication([])
    win = SetsWin()
    win.show()
    app.exec()
