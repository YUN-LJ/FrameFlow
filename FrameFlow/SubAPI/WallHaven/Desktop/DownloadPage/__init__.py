"""下载窗口"""
from SubAPI.WallHaven.ImportPack import *
from SubAPI.WallHaven.Desktop.DownloadPage.DesignFile.DownloadPage import Ui_DownloadWidget
from SubAPI.WallHaven.api.WorkFlow import DownloadWorkFlow


class DownloadPage(FluentWidgetFromUI, Ui_DownloadWidget):
    """
    实例化DownloadWorkFlow后,需要将save参数设置为True
    该窗口会自动显示下载任务
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__parent = parent
        self.slot = DownloadSlot(self, self.__parent)
        self.uiInit()
        self.bind()

    def uiInit(self):
        self.pushButton_start.setIcon(FIF.PLAY)
        self.pushButton_stop.setIcon(FIF.STOP_WATCH)
        self.pushButton_delete.setIcon(FIF.DELETE)
        self.pushButton_sync.setIcon(FIF.SYNC)

        self.setStyleSheet("DownloadPage, DownloadPage * {background-color: transparent;}")

    def addDownload(self, params: list[DownloadWorkFlow.Params] | DownloadWorkFlow.Params):
        """
        添加图像下载
        :param params:下载参数,支持列表/单个参数
        """
        if isinstance(params, DownloadWorkFlow.Params):
            DownloadWorkFlow(params)
        else:
            for param in params:
                DownloadWorkFlow(param)

    def bind(self):
        """信号连接"""
        self.pushButton_start.clicked.connect(self.slot.pushButton_start)
        self.pushButton_stop.clicked.connect(self.slot.pushButton_stop)
        self.pushButton_delete.clicked.connect(self.slot.pushButton_delete)
        self.pushButton_sync.clicked.connect(self.slot.pushButton_sync)


class DownloadSlot:

    def __init__(self, parent: DownloadPage, top_parent):
        self.parent = parent
        self.top_parent = top_parent

    def pushButton_start(self):
        self.parent.tableWidget_download.startDownload()

    def pushButton_stop(self):
        self.parent.tableWidget_download.stopDownload()

    def pushButton_delete(self):
        self.parent.tableWidget_download.deleteDownload()

    def pushButton_sync(self):
        """刷新"""
        self.parent.tableWidget_download.data_model.refreshDataLazy()


def start():
    # 创建窗口
    win = DownloadPage()
    win.show()
    # 创建测试样本
    image_ids = ['1qj5e1', '6lq3m7', 'o5k319', 'gpymve', 'o5p5rl']
    params = DownloadWorkFlow.Params
    [DownloadWorkFlow(params(image_id, 'test')) for image_id in image_ids]
    return win


if __name__ == '__main__':
    from SubAPI import StartAPI

    start_api = StartAPI(func=start, console_level='DEBUG')
    start_api.start_thread()
