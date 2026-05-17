"""设置窗口"""
from SubAPI.WallHaven.ImportPack import *
from SubAPI.WallHaven.Desktop.SetPage.DesignFile.SetPage import Ui_set_page
from SubAPI.WallHaven import api


class SetPage(HeaderCardWidget, Ui_set_page):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.slot = SetPageSlot(self)
        self.set_widget = QWidget(self)
        self.setupUi(self.set_widget)
        self.uiInit()
        self.bind()

    def uiInit(self):
        self.setTitle(f'{api.Config.PACK_NAME}设置')
        self.viewLayout.addWidget(self.set_widget)
        self.slot.loadData()

    def bind(self):
        """信号连接"""
        self.pushButton_save_dir.clicked.connect(self.slot.pushButton_save_dir)
        self.pushButton_api.clicked.connect(self.slot.pushButton_api)
        self.pushButton_proxy.clicked.connect(self.slot.pushButton_proxy)
        self.pushButton_output.clicked.connect(self.slot.pushButton_output)
        self.pushButton_input.clicked.connect(self.slot.pushButton_input)
        self.pushButton_history_num.clicked.connect(self.slot.pushButton_history_num)


class SetPageSlot:
    """槽函数类"""

    def __init__(self, parent: SetPage):
        self.parent = parent

    def loadData(self):
        """加载本地配置数据"""
        self.parent.lineEdit_save_dir.setText(api.Config.SAVE_DIR)
        self.parent.lineEdit_proxy.setText(api.Config.PROXIES_URL)
        self.parent.lineEdit_api.setText(api.Config.API_KEY)
        self.parent.spinBox_history.setValue(api.Config.SEARCH_HISTORY_COUNT)

    @info_bar_decorator
    def pushButton_save_dir(self):
        """修改保存目录"""
        save_dir = get_exist_dir('选择保存目录', dir_path=api.Config.SAVE_DIR)
        if save_dir:
            self.parent.lineEdit_save_dir.setText(save_dir)
            api.set_save_dir(save_dir)
            return True, '保存目录设置成功', self.parent
        return False, '未选择目录', self.parent

    @info_bar_decorator
    def pushButton_api(self):
        """修改API"""
        api_key = self.parent.lineEdit_api.text()
        if api.set_api_key(api_key):
            return True, 'API设置成功', self.parent
        return False, 'API设置失败', self.parent

    @info_bar_decorator
    def pushButton_proxy(self):
        """修改代理"""
        proxy_url = self.parent.lineEdit_proxy.text()
        if api.set_proxies_url(proxy_url):
            return True, '代理设置成功', self.parent
        return False, '代理设置失败', self.parent

    @info_bar_decorator
    def pushButton_output(self):
        """导出数据"""
        if self.parent.comboBox_output.text() == '图像信息':
            output_path = IMAGE_INFO.to_excel()
            FileBase(output_path).open_use_explorer()
            return True, '图像信息导出成功', self.parent
        elif self.parent.comboBox_output.text() == '收藏夹数据':
            output_path = KEY_WORD.to_excel()
            FileBase(output_path).open_use_explorer()
            return True, '收藏夹数据导出成功', self.parent
        return False, '导出数据失败', self.parent

    @info_bar_decorator
    def pushButton_input(self):
        """导入数据"""
        data_path = get_exist_files('选择文件', ext='xlsx文件(*.xlsx);;All file(*)')
        if self.parent.comboBox_input.text() == '图像信息' and IMAGE_INFO.load_from_excel(data_path):
            return True, '图像信息导入成功', self.parent
        elif self.parent.comboBox_input.text() == '收藏夹数据' and KEY_WORD.load_from_excel(data_path):
            return True, '收藏夹数据导入成功', self.parent
        return False, '导入数据失败', self.parent

    @info_bar_decorator
    def pushButton_history_num(self):
        """设置历史记录数量"""
        api.set_search_history_count(self.parent.spinBox_history.value())
        return True, '历史记录数量设置成功', self.parent


if __name__ == '__main__':
    from SubAPI import start_desktop


    def start():
        win = SetPage()
        win.show()
        return win


    start_desktop(start)
