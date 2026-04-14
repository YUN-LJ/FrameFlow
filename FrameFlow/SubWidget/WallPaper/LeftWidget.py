"""左侧布局"""
from SubWidget.ImportPack import *
from SubWidget.WallPaper.DesignFile.LeftWidget import Ui_leftwidget


class LeftWidget(Ui_leftwidget, QWidget):

    def __init__(self, parent=None):
        super().__init__()
        self.__parent = parent
        self.setupUi(self)
        self.stackedWidget.setCurrentIndex(WP.Config.IMAGE_PLAY_MODE)
