"""表格"""
from SubAPI.WallPaper.ImportPack import *
from SubAPI.WallPaper import api
from SubAPI.WallPaper.Desktop.KeyTable.DesignFile.KeyTable import Ui_table_widget


class TableWidget(FluentWidgetFromUI, Ui_table_widget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stackedWidget.setCurrentIndex(api.Config.IMAGE_PLAY_MODE)
