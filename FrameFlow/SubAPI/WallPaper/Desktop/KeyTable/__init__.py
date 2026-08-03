"""表格"""
from SubAPI.WallPaper.ImportPack import *
from SubAPI.WallPaper import api
from SubAPI.WallPaper.Desktop.KeyTable.DesignFile.KeyTable import Ui_table_widget

INFO_BAR_PARENT = None


def set_info_bar_parent(parent):
    global INFO_BAR_PARENT
    INFO_BAR_PARENT = parent


class TableWidget(FluentWidgetFromUI, Ui_table_widget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.slot = TableSlot(self)
        self.stackedWidget.setCurrentIndex(api.Config.IMAGE_PLAY_MODE)
        self.__bind()

    def __bind(self):
        self.lineEdit_search.searchSignal.connect(self.slot.lineEdit_search)
        self.lineEdit_search.returnPressed.connect(self.slot.lineEdit_search)
        self.pushButton_select.clicked.connect(self.slot.pushButton_select)
        self.pushButton_cancel_select.clicked.connect(self.slot.pushButton_cancel_select)

    @staticmethod
    def set_info_bar_parent(parent):
        set_info_bar_parent(parent)


class TableSlot:
    """表格槽"""

    def __init__(self, parent: TableWidget):
        self.parent = parent

    @property
    def info_bar_parent(self):
        return INFO_BAR_PARENT or self.parent

    @info_bar_decorator
    def lineEdit_search(self, key_word=None):
        key_word = self.parent.lineEdit_search.text() if key_word is None else key_word
        if self.parent.stackedWidget.currentIndex() == api.Config.IMAGE_KEY_MODE:
            if self.parent.tableWidget_key.searchKey(key_word):
                return True, f'定位{key_word}到首行', self.info_bar_parent
        return False, f'{key_word} 不存在', self.info_bar_parent

    @info_bar_decorator
    def pushButton_select(self):
        key_word = self.parent.lineEdit_search.text()
        if self.parent.stackedWidget.currentIndex() == api.Config.IMAGE_KEY_MODE:
            if key_word:
                if self.parent.tableWidget_key.searchKey(key_word):
                    self.parent.tableWidget_key.selectCell(key_word)
                    return True, f'已选择{key_word}开头的关键词', self.info_bar_parent
        return False, f'{key_word} 不存在', self.info_bar_parent

    @info_bar_decorator
    def pushButton_cancel_select(self):
        key_word = self.parent.lineEdit_search.text()
        if self.parent.stackedWidget.currentIndex() == api.Config.IMAGE_KEY_MODE:
            if key_word:
                if self.parent.tableWidget_key.searchKey(key_word):
                    self.parent.tableWidget_key.cancelSelectCell(key_word)
                    return True, f'已取消选择{key_word}开头的关键词', self.info_bar_parent
        return False, f'{key_word} 不存在', self.info_bar_parent
