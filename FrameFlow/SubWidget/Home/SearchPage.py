"""搜索子窗口"""
from SubWidget.ImportPack import *
from SubWidget.Home.SlotFunc import SearchPageCtrl as SPC
from SubWidget.Home.SlotFunc.DialogWidget import SearchDialog, DelDialog
from SubWidget.Home.DesignFile.SearchPage import Ui_SearchPage


class SearchPage(QWidget, Ui_SearchPage):
    downloadSignal = Signal(list)  # 下载按钮触发时[(关键词,url)]
    searchSignal = Signal(str)  # 发送关键词可切换到该页面并触发搜索

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__parent = parent
        self.setupUi(self)
        AppCore().addSignal('search', self.searchSignal)
        self.slot = SearchSlot(self, self.__parent)  # 槽函数
        # 弹窗
        self.search_dialog = SearchDialog(self, self.__parent)
        self.del_dialog = DelDialog(self, self.__parent)
        # 所有子控件继承样式
        self.setStyleSheet("""SearchPage, SearchPage * {background-color: transparent;}""")
        self.uiInit()
        self.bind()

    def uiInit(self):
        self.pushButton_select_all.setIcon(FIF.CHECKBOX)
        self.pushButton_download.setIcon(FIF.DOWNLOAD)
        self.pushButton_delete.setIcon(FIF.DELETE)
        self.pushButton_download.hide()
        self.tableWidget_image.setTopParent(self.__parent)
        self.checkBox_use_network.setOffText('本地搜索')
        self.checkBox_use_network.setOnText('联网搜索')
        self.checkBox_use_tags.setOffText('检索关键词')
        self.checkBox_use_tags.setOnText('检索标签')
        self.checkBoxsCategories = [self.checkBox_general, self.checkBox_anime, self.checkBox_people]
        self.checkBoxsPurity = [self.checkBox_sfw, self.checkBox_sketchy, self.checkBox_nsfw]

    def bind(self):
        """信号连接"""
        self.searchSignal.connect(self.slot.searchSiganl)
        self.lineEdit.searchSignal.connect(self.slot.lineEdit)
        self.lineEdit.returnPressed.connect(self.slot.lineEdit)
        self.lineEdit.clearSignal.connect(self.slot.lineEdit_clear)
        self.lineEdit.installEventFilter(self)  # 安装事件过滤器,用来执行自定义事件
        self.spinBox.valueChanged.connect(self.slot.lineEdit)
        self.pushButton_select_all.clicked.connect(self.slot.pushButton_select_all)
        self.pushButton_download.clicked.connect(self.slot.pushButton_download)
        self.pushButton_delete.clicked.connect(self.slot.pushButton_delete)
        # 根据配置文件设置UI状态
        self.checkBox_use_network.checkedChanged.connect(self.slot.checkBox_use_network)
        self.checkBox_use_network.setChecked(WH.Config.USE_NETWORK)
        self.checkBox_use_tags.checkedChanged.connect(self.slot.checkBox_use_tags)
        self.checkBox_use_tags.setChecked(WH.Config.USE_TAGS)
        for obj in self.checkBoxsCategories:
            obj.stateChanged.connect(self.slot.checkBoxsCategories)
        for obj in self.checkBoxsPurity:
            obj.stateChanged.connect(self.slot.checkBoxsPurity)
        # 设置选中状态
        purity = WH.get_search_params().purity
        for index, obj in enumerate(self.checkBoxsPurity):
            obj.setChecked(int(purity[index]))
        categories = WH.get_search_params().categories
        for index, obj in enumerate(self.checkBoxsCategories):
            obj.setChecked(int(categories[index]))

    def getPurity(self) -> str:
        return ''.join([
            str(int(self.checkBox_sfw.isChecked())),
            str(int(self.checkBox_sketchy.isChecked())),
            str(int(self.checkBox_nsfw.isChecked())),
        ])

    def getCategories(self) -> str:
        return ''.join([
            str(int(self.checkBox_general.isChecked())),
            str(int(self.checkBox_anime.isChecked())),
            str(int(self.checkBox_people.isChecked())),
        ])

    def eventFilter(self, obj, event):
        """事件过滤器,可动态添加事件"""
        if (obj == self.lineEdit and
                event.type() == QEvent.MouseButtonPress and
                event.button() == Qt.MouseButton.RightButton):
            # 创建弹出窗口
            popup = QWidget(self)
            popup.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
            popup.setWindowOpacity(0.8)  # 0.0完全透明，1.0不透明
            # 创建滚动区域
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setFixedWidth(self.lineEdit.width())  # 与输入框同宽
            # 内容容器
            content = QWidget(self)
            layout = QVBoxLayout(content)
            layout.setContentsMargins(0, 0, 0, 0)
            # 添加按钮
            for text in WH.get_search_history():
                btn = TransparentPushButton(text)
                btn.setMaximumHeight(40)
                btn.clicked.connect(lambda checked, value=text: self.lineEdit.setText(value))
                layout.addWidget(btn)
            scroll.setWidget(content)
            # 主布局
            main_layout = QHBoxLayout(popup)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.addWidget(scroll)
            # 定位在输入框下方
            pos = self.lineEdit.mapToGlobal(QPoint(0, self.lineEdit.height()))
            popup.setMaximumHeight(240)
            popup.move(pos)
            popup.show()
        return super().eventFilter(obj, event)


class SearchSlot:
    """槽函数类"""

    def __init__(self, parent: SearchPage, top_parent):
        self.parent = parent
        self.top_parent = top_parent

    def searchSiganl(self, text):
        AppCore().getSignal('Home_switchPage').emit(self.parent)
        self.lineEdit(text)

    def lineEdit(self, value: int | str = None):
        text = value if isinstance(value, str) else self.parent.lineEdit.text()
        page = value if isinstance(value, int) else 1
        if text is not None:
            self.parent.lineEdit.setText(text)
            self.parent.tableWidget_image.searchKeyWord(
                text, self.parent.getPurity(), self.parent.getCategories(), page,
                use_network=self.parent.checkBox_use_network.isChecked(),
                use_tags=self.parent.checkBox_use_tags.isChecked()
            )
        else:
            TeachingTip.create(
                target=self.parent.lineEdit, icon=InfoBarIcon.ERROR, title='缺少关键词', content='请输入关键词',
                isClosable=True, duration=1000, parent=self.top_parent,
                tailPosition=TeachingTipTailPosition.BOTTOM)

    def lineEdit_clear(self):
        self.parent.pushButton_select_all.setText('全选')
        self.parent.tableWidget_image.clearCell()

    def checkBoxsCategories(self):
        Categories = []
        for obj in self.parent.checkBoxsCategories:
            Categories.append(str(int(obj.isChecked())))
            obj.setEnabled(True)
        Categories = ''.join(Categories)
        if Categories.count('1') == 1:
            self.parent.checkBoxsCategories[Categories.find('1')].setEnabled(False)

    def checkBoxsPurity(self):
        Purity = []
        for obj in self.parent.checkBoxsPurity:
            Purity.append(str(int(obj.isChecked())))
            obj.setEnabled(True)
        Purity = ''.join(Purity)
        if Purity.count('1') == 1:
            self.parent.checkBoxsPurity[Purity.find('1')].setEnabled(False)
        checked = bool(WH.Config.API_KEY) if self.parent.checkBox_use_network.isChecked() else True
        self.parent.checkBox_nsfw.setEnabled(checked)

    def checkBox_use_tags(self, checked):
        WH.Config.USE_TAGS = checked

    def checkBox_use_network(self, checked):
        SearchData.clear()
        self.parent.tableWidget_image.clearCell()
        if checked:
            self.parent.pushButton_download.show()
            self.parent.pushButton_delete.hide()
            self.parent.checkBox_use_tags.hide()
            WH.Config.USE_NETWORK = True
        else:
            self.parent.pushButton_download.hide()
            self.parent.pushButton_delete.show()
            self.parent.checkBox_use_tags.show()
            WH.Config.USE_NETWORK = False

    def pushButton_select_all(self):
        text = self.parent.lineEdit.text()
        if text:
            if self.parent.pushButton_select_all.text() == '全选':
                self.parent.pushButton_select_all.setText('取消全选')
                self.parent.tableWidget_image.searchKeyWord(
                    text, self.parent.getPurity(), self.parent.getCategories(), self.parent.spinBox.value(),
                    search_all=True, use_network=self.parent.checkBox_use_network.isChecked(),
                    use_tags=self.parent.checkBox_use_tags.isChecked())
            else:
                self.parent.pushButton_select_all.setText('全选')
                self.parent.tableWidget_image.selectClear()
        else:
            TeachingTip.create(
                target=self.parent.pushButton_select_all, icon=InfoBarIcon.ERROR, title='错误', content='请先发起搜索',
                isClosable=True, duration=1000, parent=self.top_parent,
                tailPosition=TeachingTipTailPosition.BOTTOM)

    def pushButton_delete(self):
        icon = InfoBarIcon.ERROR
        title = '删除失败'
        content = '未选择任何图片'
        select_image = self.parent.tableWidget_image.selected_image_id
        if select_image:
            load_dialog = MessageBox(
                '确认删除',
                f'已选择{len(select_image)}张',
                parent=self.top_parent)
            if load_dialog.exec() and self.parent.del_dialog.delImage(select_image):
                icon = InfoBarIcon.SUCCESS
                title = '删除成功'
                content = f'成功删除:{len(select_image)}张'
                SearchData.clear()
                self.lineEdit()
            else:
                content = '已取消'
        InfoBar.new(
            icon=icon, title=title, content=content, orient=Qt.Horizontal,
            isClosable=True, position=InfoBarPosition.TOP,
            duration=1500, parent=self.top_parent)

    def pushButton_download(self):
        """下载"""
        icon = InfoBarIcon.ERROR
        title = '下载失败'
        content = '未选择任何图片'
        selected_image_id = self.parent.tableWidget_image.selected_image_id
        if selected_image_id:
            load_dialog = MessageBox(
                '确认下载',
                f'已选择{len(selected_image_id)}张',
                parent=self.top_parent)
            if load_dialog.exec():
                with SearchData.lock:
                    mask = SearchData.data()['id'].isin(selected_image_id)
                    success = SearchData.data()[mask].copy(deep=True).drop_duplicates(
                        subset=['id', '关键词'], keep='last'
                    ).reset_index(drop=True)
                if not success.empty:
                    self.parent.downloadSignal.emit(success[['关键词', '远程路径']].values.tolist())
                    icon = InfoBarIcon.SUCCESS
                    title = '提交成功'
                    content = f'成功提交:{success.shape[0]}张'
                    self.parent.tableWidget_image.selectClear()
            else:
                content = '已取消删除'
        InfoBar.new(
            icon=icon, title=title, content=content, orient=Qt.Horizontal,
            isClosable=True, position=InfoBarPosition.TOP,
            duration=1000, parent=self.top_parent)
        # TeachingTip.create(
        #     target=self.parent.pushButton_download, icon=icon, title=title, content=content,
        #     isClosable=True, duration=1000, parent=self.top_parent,
        #     tailPosition=TeachingTipTailPosition.BOTTOM)
