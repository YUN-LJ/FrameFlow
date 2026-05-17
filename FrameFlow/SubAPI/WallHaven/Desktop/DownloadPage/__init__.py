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


if __name__ == '__main__':
    from SubAPI import start_desktop
    from SubAPI.WallHaven import api

    # 创建测试样本
    image_ids = ['mlwj3m', 'e8ekxl', '7jw8po', 'qrgl87']

    # 打印图像数据信息
    # IMAGE_INFO.is_loaded(0)
    # with IMAGE_INFO as df:
    #     mask = df['id'].isin(image_ids)
    #     print(df.loc[mask, '本地路径'])

    params = DownloadWorkFlow.Params
    [DownloadWorkFlow(params(image_id, 'test')) for image_id in image_ids]


    def start():
        # 创建窗口
        win = DownloadPage()
        win.show()
        return win


    start_desktop(start)
