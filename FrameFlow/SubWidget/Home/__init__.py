"""
主页
View->UI文件
ViewLayer->中间层负责处理连接View和WorkerLayer
WorkerLayer->具体的工作层
"""
from SubWidget.Home.ImportPack import *
from SubWidget.Home.SearchPage import SearchPage
from SubWidget.Home.DownloadPage import DownloadPage
from SubWidget.Home.KeyWordPage import KeyWordPage
from SubWidget.Home.SetPage import SetPage


class HomeWin(TopWidget):
    switchPageSignal = Signal(QWidget)  # 发送需要切换页面的对象即可切换到指定页面

    def __init__(self, parent=None):
        self.__parent = self if parent is None else parent
        super().__init__(self.__parent)
        AppCore().addSignal('Home_switchPage', self.switchPageSignal)
        self.uiInit()
        self.bind()

    def uiInit(self):
        self.search_page = SearchPage(self.__parent)
        self.download_page = DownloadPage(self.__parent)
        self.key_page = KeyWordPage(self.__parent)
        self.set_page = SetPage(self.__parent)
        self.addSubInterface(self.search_page, 'search_page', '搜索')
        self.addSubInterface(self.download_page, 'download_page', '下载')
        self.addSubInterface(self.key_page, 'key_page', '收藏')
        self.addSubInterface(self.set_page, 'set_page', '设置')
        self.topWidget.setCurrentItem(self.search_page.objectName())

    def switchPage(self, widget: QWidget):
        self.stackedWidget.setCurrentWidget(widget)
        self.topWidget.setCurrentItem(widget.objectName())

    def bind(self):
        self.switchPageSignal.connect(self.switchPage)
        self.search_page.downloadSignal.connect(self.download_page.addDownload)
        self.key_page.downloadSignal.connect(self.download_page.addDownload)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.key_page.tableWidget.stopUpdate()
        WH.save_config(self.search_page.getPurity(), self.search_page.getCategories())
        WHAPI.stop()
