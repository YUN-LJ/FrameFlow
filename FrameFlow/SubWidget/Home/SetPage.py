"""设置子窗口"""
from SubWidget.ImportPack import *
from SubWidget.Home.DesignFile.SetPage import Ui_set_page


class SetPage(QWidget, Ui_set_page):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__parent = parent
        self.setupUi(self)
        self.slot = SetSlot(self, self.__parent)  # 槽函数
        # 所有子控件继承样式
        self.setStyleSheet("""SetPage, SetPage * {background-color: transparent;}""")
        self.uiInit()
        self.bind()

    def uiInit(self):
        self.spinBox_thread_num.setValue(WH.Config.THREAD_NUM)
        self.spinBox_history.setValue(WH.Config.SEARCH_HISTORY_COUNT)
        self.lineEdit_api.setText(WH.Config.API_KEY)
        self.lineEdit_proxy.setText(WH.Config.PROXIES_URL)

    def bind(self):
        self.pushButton_thread_num.clicked.connect(self.slot.pushButton_thread_num)
        self.pushButton_proxy.clicked.connect(self.slot.pushButton_proxy)
        self.pushButton_api.clicked.connect(self.slot.pushButton_api)
        self.pushButton_output.clicked.connect(self.slot.pushButton_output)
        self.pushButton_input.clicked.connect(self.slot.pushButton_input)
        self.spinBox_history.valueChanged.connect(self.slot.spinBox_history)
        self.spinBox_history.setValue(WH.Config.SEARCH_HISTORY_COUNT)


class SetSlot:
    def __init__(self, parent: SetPage, top_parent):
        self.parent = parent
        self.top_parent = top_parent

    def pushButton_thread_num(self):
        num = self.parent.spinBox_thread_num.value()
        WHAPI.set_thread_num(num)
        if self.parent.isVisible():
            InfoBar.new(
                icon=InfoBarIcon.SUCCESS, title='设置成功', content=f'已成功修改线程数量 {num}',
                orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP,
                duration=1000, parent=self.top_parent)

    def pushButton_proxy(self):
        ico = InfoBarIcon.ERROR
        title = '设置失败'
        content = '连接失败'
        proxies = self.parent.lineEdit_proxy.text()
        if WH.set_proxies_url(proxies):
            ico = InfoBarIcon.SUCCESS
            title = '设置成功'
            if not WH.Config.PROXIES_URL:
                content = f'已取消代理服务器'
            else:
                content = f'已成功设置代理服务器{WH.Config.PROXIES}'
        if self.parent.isVisible():
            InfoBar.new(
                icon=ico, title=title, content=content,
                orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP,
                duration=1000, parent=self.top_parent)

    def pushButton_api(self):
        ico = InfoBarIcon.ERROR
        title = '设置失败'
        content = '连接失败'
        api_key = self.parent.lineEdit_api.text()
        if WH.set_api_key(api_key):
            ico = InfoBarIcon.SUCCESS
            title = '设置成功'
            content = f'已成功设置API密钥{WH.Config.API_KEY}'
        if self.parent.isVisible():
            InfoBar.new(
                icon=ico, title=title, content=content,
                orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP,
                duration=1000, parent=self.top_parent)

    def pushButton_output(self):
        icon = InfoBarIcon.ERROR
        title = '导出失败'
        content = '数据未加载完成'
        if self.parent.comboBox_output.currentText() == '图像信息':
            save_path = ImageInfo.to_excel()
        elif self.parent.comboBox_output.currentText() == '收藏夹数据':
            save_path = KeyWord.to_excel()
        if save_path:
            icon = InfoBarIcon.SUCCESS
            title = '导出成功'
            content = f'保存在{save_path}'
        if self.parent.isVisible():
            InfoBar.new(
                icon=icon, title=title, content=content, orient=Qt.Horizontal,
                isClosable=True, position=InfoBarPosition.TOP,
                duration=1000, parent=self.top_parent)
        if save_path:
            FileBase(save_path).open_use_explorer()

    def pushButton_input(self):
        icon = InfoBarIcon.ERROR
        title = '导入失败'
        content = '未选择文件或数据未加载'
        path = get_exist_files('选择文件', GlobalValue.config_dir, ext="excel(*.xls;*.xlsx);;All file(*)")
        if path:
            path = path[0]
            if self.parent.comboBox_input.currentText() == '图像信息':
                state = ImageInfo.load_from_excel(path)
            elif self.parent.comboBox_input.currentText() == '收藏夹数据':
                state = KeyWord.load_from_excel(path)
            if state:
                icon = InfoBarIcon.SUCCESS
                title = '导入成功'
                content = f'成功导入{path}'
        if self.parent.isVisible():
            InfoBar.new(
                icon=icon, title=title, content=content, orient=Qt.Horizontal,
                isClosable=True, position=InfoBarPosition.TOP,
                duration=1000, parent=self.top_parent)

    def spinBox_history(self, value):
        WH.Config.SEARCH_HISTORY_COUNT = value
