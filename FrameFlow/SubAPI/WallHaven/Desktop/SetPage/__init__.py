"""设置窗口"""
from SubAPI.WallHaven.ImportPack import *
from SubAPI.Settings.Desktop.SetCard import MenuCardLineEdit, MenuCardSpinBox, MenuCardComboBox
from SubAPI.WallHaven import api


class SetPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.uiInit()

    def uiInit(self):
        # 主布局
        self.view_layout = QVBoxLayout(self)
        self.setLayout(self.view_layout)

        # 保存目录
        self.lineEdit_save_dir = MenuCardLineEdit('保存目录', self.parent())
        self.lineEdit_save_dir.setGetValueFunc(lambda: api.Config.SAVE_DIR)
        self.lineEdit_save_dir.setSetValueFunc(api.set_save_dir)
        self.lineEdit_save_dir.enableDirChoose()
        self.view_layout.addWidget(self.lineEdit_save_dir)

        # 代理设置
        self.lineEdit_proxy = MenuCardLineEdit('代理设置', self.parent())
        self.lineEdit_proxy.lineEdit.setPlaceholderText('例如: 127.0.0.1:1080')
        self.lineEdit_proxy.setGetValueFunc(lambda: api.Config.PROXIES_URL)
        self.lineEdit_proxy.setSetValueFunc(api.set_proxies_url)
        self.view_layout.addWidget(self.lineEdit_proxy)

        # API设置
        self.lineEdit_api = MenuCardLineEdit('API设置', self.parent())
        self.lineEdit_api.lineEdit.setPlaceholderText('请在wallhaven个人账户中获取')
        self.lineEdit_api.setGetValueFunc(lambda: api.Config.API_KEY)
        self.lineEdit_api.setSetValueFunc(api.set_api_key)
        self.view_layout.addWidget(self.lineEdit_api)

        # 导出数据
        self.comboBox_output = MenuCardComboBox('导出数据', self.parent())
        self.comboBox_output.addComboBoxItems(['图像信息', '收藏夹数据'])
        self.comboBox_output.setGetValueFunc(lambda: '')
        self.comboBox_output.setSetValueFunc(self._comboBox_output)
        self.view_layout.addWidget(self.comboBox_output)

        # 导入数据
        self.comboBox_input = MenuCardComboBox('导入数据', self.parent())
        self.comboBox_input.addComboBoxItems(['图像信息', '收藏夹数据'])
        self.comboBox_input.setGetValueFunc(lambda: '')
        self.comboBox_input.setSetValueFunc(self._comboBox_input)
        self.view_layout.addWidget(self.comboBox_input)

        # 历史记录数量
        self.spinBox_history = MenuCardSpinBox('历史记录数量', self.parent())
        self.spinBox_history.setGetValueFunc(lambda: api.Config.SEARCH_HISTORY_COUNT)
        self.spinBox_history.setSetValueFunc(api.set_search_history_count)
        self.view_layout.addWidget(self.spinBox_history)

        # 填充容器
        self.view_layout.addStretch()

    @staticmethod
    def _comboBox_output(text: str):
        """导出数据"""
        if text == '图像信息':
            output_path = IMAGE_INFO.to_excel()
            FileBase(output_path).open_use_explorer()
            return True
        elif text == '收藏夹数据':
            output_path = KEY_WORD.to_excel()
            FileBase(output_path).open_use_explorer()
            return True
        return False

    @staticmethod
    def _comboBox_input(text: str):
        """导入数据"""
        data_path = get_exist_files('选择文件', dir_path=GlobalValue.CONFIG_DIR, ext='xlsx文件(*.xlsx);;All file(*)')
        if data_path:
            data_path = data_path[0]
        else:
            return False

        if text == '图像信息' and IMAGE_INFO.load_from_excel(data_path):
            return True
        elif text == '收藏夹数据' and KEY_WORD.load_from_excel(data_path):
            return True
        return False


def start():
    win = SetPage()
    win.show()
    return win


if __name__ == '__main__':
    from SubAPI import StartAPI, StartEnum

    start_api = StartAPI(func=start, console_level=StartEnum.LogLevel.DEBUG)
    start_api.start_thread()
