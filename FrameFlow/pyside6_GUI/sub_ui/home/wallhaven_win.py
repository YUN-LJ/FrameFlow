"""wallhaven模块的UI"""
from pyside6_GUI.sub_ui.home.ImportPack import *


class WallHavenWin(TopWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__parent = parent if parent is not None else self
        self.wallhaven_api = WallHavenAPI()
        self.uiInit()

    def uiInit(self):
        self.search_page = SearchPage(self.wallhaven_api, self.__parent)
        self.download = QWidget(self)
        self.key_word = QWidget(self)
        self.set_page = QWidget(self)
        # 添加控件
        self.addSubInterface(self.search_page, 'search_page', '搜索')
        self.addSubInterface(self.download, 'download', '下载')
        self.addSubInterface(self.key_word, 'key_word', '收藏夹')
        self.addSubInterface(self.set_page, 'set_page', '设置')

        # 设置当前显示
        self.topWidget.setCurrentItem(self.search_page.objectName())  # 设置当前显示

    def closeEvent(self, event):
        super().closeEvent(event)
        self.search_page.wallhaven_api.stop()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    w = WallHavenWin()
    w.show()
    app.exec()
