"""下载子窗口"""
from SubWidget.Home.ImportPack import *
from SubWidget.Home.DesignFile.DownloadPage import Ui_DownloadWidget


class DownloadPage(QWidget, Ui_DownloadWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__parent = parent
        self.setupUi(self)
        self.slot = DownloadSlot(self, self.__parent)
        # 所有子控件继承样式
        self.setStyleSheet("""
                    DownloadPage, DownloadPage * {
                        background-color: transparent;
                    }
                """)
        self.uiInit()
        self.bind()

    def uiInit(self):
        self.pushButton_select_all.setIcon(FIF.CHECKBOX)
        self.pushButton_delete.setIcon(FIF.CLOSE)
        self.label_save_path_value.setText(WH.Config.SAVE_DIR)

    def addDownload(self, image_url: tuple | list):
        """
        添加图像下载
        :param image_url:[(key,url)]
        """
        self.tableWidget_download.addImageUrl(image_url)

    def bind(self):
        """信号连接"""
        self.label_save_path_value.clicked.connect(self.slot.label_save_path_value)
        self.pushButton_set_save_path.clicked.connect(self.slot.pushButton_set_save_path)
        self.pushButton_select_all.clicked.connect(self.slot.pushButton_select_all)
        self.pushButton_start.clicked.connect(self.slot.pushButton_start)
        self.pushButton_delete.clicked.connect(self.slot.pushButton_delete)


class DownloadSlot:

    def __init__(self, parent: DownloadPage, top_parent):
        self.parent = parent
        self.top_parent = top_parent

    def label_save_path_value(self):
        save_dir = WH.Config.SAVE_DIR
        file.open_file_use_explorer(save_dir)

    def pushButton_set_save_path(self):
        save_dir = get_exist_dir('选择保存目录', WH.Config.SAVE_DIR)
        if save_dir:
            WH.Config.SAVE_DIR = save_dir
            self.parent.label_save_path_value.setText(save_dir)
        else:
            TeachingTip.create(
                target=self.parent.pushButton_set_save_path, icon=InfoBarIcon.ERROR, title='选择为空', content='已取消',
                isClosable=True, duration=1000, parent=self.top_parent,
                tailPosition=TeachingTipTailPosition.BOTTOM)

    def pushButton_select_all(self):
        if self.parent.pushButton_select_all.text() == '全选':
            self.parent.pushButton_select_all.setText('取消全选')
            self.parent.tableWidget_download.selectAllRows(True)
        else:
            self.parent.pushButton_select_all.setText('全选')
            self.parent.tableWidget_download.selectAllRows(False)

    def pushButton_start(self):
        self.parent.tableWidget_download.startDownload()

    def pushButton_delete(self):
        self.parent.tableWidget_download.delDownload()
