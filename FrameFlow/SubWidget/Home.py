"""
主页
各个Page结尾的为子窗口
SlotFunc内为各窗口控件文件(数据层与显示层分离设计)
WorkFlow为具体工作流
"""
from SubWidget.ImportPack import *
from SubAPI.WallHaven.Desktop.SearchPage import SearchPage
from SubAPI.WallHaven.Desktop.DownloadPage import DownloadPage
from SubAPI.WallHaven.Desktop.LikePage import LikePage


class HomeWin(TopWidget):

    def __init__(self, parent=None):
        self.__parent = self if parent is None else parent
        super().__init__(self.__parent)
        self.uiInit()
        self.bind()

    def uiInit(self):
        self.search_page = SearchPage(self.__parent)
        self.download_page = DownloadPage(self.__parent)
        self.key_page = LikePage(self.__parent)
        self.addSubInterface(self.search_page, 'search_page', '搜索')
        self.addSubInterface(self.download_page, 'download_page', '下载')
        self.addSubInterface(self.key_page, 'like_page', '收藏')
        self.topWidget.setCurrentItem(self.search_page.objectName())

    def bind(self):
        TopWindowSignal.home_signal.switchPageSignal.connect(self.switchPage)
