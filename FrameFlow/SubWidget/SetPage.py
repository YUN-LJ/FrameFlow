"""
设置窗口
"""
from SubWidget.ImportPack import *
from SubAPI.Settings.Desktop import BaseSetWin, MenuCard
from SubAPI.WallHaven.Desktop.SetPage import SetPage as WHSet
from SubAPI.WallHaven import api


class SetsWin(BaseSetWin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.wallhaven_set = MenuCard(f'{api.Config.PACK_NAME}设置', self)
        self.wallhaven_set.addContentWidget(WHSet(self))
        self.addSetCard(self.wallhaven_set)


if __name__ == '__main__':
    app = QApplication([])
    win = SetsWin()
    win.show()
    app.exec()
