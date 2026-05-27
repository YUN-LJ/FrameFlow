"""搜索窗口"""
from SubAPI.WallHaven.ImportPack import *
from SubAPI.WallHaven.Desktop.SearchPage.DesignFile.SearchPage import Ui_SearchPage
from SubAPI.WallHaven import api


class SearchPage(FluentWidgetFromUI, Ui_SearchPage):

    def __init__(self, parent=None):
        super().__init__(parent)
        parent = self if parent is None else parent
        self.slot = SearchSlot(self, parent)
        self.uiInit()
        self.bind()

    def uiInit(self):
        self.checkBox_use_network.setOffText('本地搜索')
        self.checkBox_use_network.setOnText('联网搜索')
        self.checkBox_use_tags.setOffText('检索关键词')
        self.checkBox_use_tags.setOnText('检索标签')
        self.widget_search_params.hide()
        self.pushButton_expand.setIcon(FIF.MENU)

        self.checkBoxsCategories = [self.checkBox_general, self.checkBox_anime, self.checkBox_people]
        self.checkBoxsPurity = [self.checkBox_sfw, self.checkBox_sketchy, self.checkBox_nsfw]
        self.setStyleSheet("""SearchPage, SearchPage * {background-color: transparent;}""")
        for checkBox, color in zip(self.checkBoxsPurity, [QColor(0, 255, 0), QColor(255, 255, 0), QColor(170, 0, 0)]):
            checkBox.setTextColor(color, color)

    def bind(self):
        """信号连接"""
        self.pushButton_expand.clicked.connect(self.slot.pushButton_expand)
        self.lineEdit.searchSignal.connect(self.slot.lineEdit)
        self.lineEdit.returnPressed.connect(self.slot.lineEdit)
        self.lineEdit.clearSignal.connect(self.slot.clearTable)
        self.spinBox.valueChanged.connect(self.slot.spinBox)
        # 安装事件过滤器,用来执行自定义事件,让其事件先被self捕获
        self.lineEdit.installEventFilter(self)

        # 根据配置文件设置UI状态
        self.checkBox_use_network.checkedChanged.connect(self.slot.checkBox_use_network)
        self.checkBox_use_network.setChecked(api.Config.USE_NETWORK)
        self.checkBox_use_tags.checkedChanged.connect(self.slot.checkBox_use_tags)
        self.checkBox_use_tags.setChecked(api.Config.USE_TAGS)
        for obj in self.checkBoxsCategories:
            obj.stateChanged.connect(self.slot.checkBoxsCategories)
        for obj in self.checkBoxsPurity:
            obj.stateChanged.connect(self.slot.checkBoxsPurity)
        # 设置选中状态
        purity = api.get_search_params().purity
        for index, obj in enumerate(self.checkBoxsPurity):
            obj.setChecked(int(purity[index]))
        categories = api.get_search_params().categories
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
        if (obj == self.lineEdit and event.type() == QEvent.MouseButtonPress and
                event.button() == Qt.MouseButton.RightButton):
            # 创建弹出窗口
            popup = SimpleCardWidget(self)
            popup.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
            popup.setWindowOpacity(0.8)  # 0.0完全透明，1.0不透明
            # 创建滚动区域
            scroll = ScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setFixedWidth(self.lineEdit.width())  # 与输入框同宽
            # 内容容器
            content = QWidget(self)
            layout = QVBoxLayout(content)
            layout.setContentsMargins(0, 0, 0, 0)
            # 添加按钮
            for text in api.get_search_history():
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

    def __del__(self):
        """清理资源"""
        api.set_purity(self.getPurity())
        api.set_category(self.getCategories())


class SearchSlot:
    """槽函数类"""

    def __init__(self, parent: SearchPage, top_parent):
        self.parent = parent
        self.top_parent = top_parent
        self.search_dialog: LoadBarDialog = None  # 搜索对话框
        self.signal_connect()

        # 防抖器
        self.spinbox_timer = debouncer_timer(self._spinBox)

    def signal_connect(self):
        """信号连接"""
        signal = SignalConfig.WallHavenSignal.search_signal
        signal.startSignal.connect(self.__search_start)
        signal.progressSignal.connect(self.__search_progress)
        signal.finishedSignal.connect(self.__search_finished)
        signal.stopSignal.connect(self.__search_stop)
        signal.searchSignal.connect(self.search)
        self.parent.tableWidget_image.currentPageSignal.connect(self.currentPageSolt)
        self.parent.tableWidget_image.loadNextPageSignal.connect(self.loadNextPageSolt)

    def currentPageSolt(self, page: int):
        self.parent.spinBox.blockSignals(True)
        self.parent.spinBox.setValue(page)
        self.parent.spinBox.blockSignals(False)

    def loadNextPageSolt(self, page: int):
        """加载当前页面"""
        if page <= self.parent.spinBox.maximum():
            self.lineEdit(page)

    def search(self, task: api.SearchTask):
        """发送搜索任务"""
        self.parent.lineEdit.setText(task.params.q)
        api.set_purity(task.params.purity)
        api.set_category(task.params.categories)
        self.parent.tableWidget_image.searchKeyWord(task)

    def __close_dialog(self):
        try:
            if self.search_dialog is not None:
                self.search_dialog.accept()
                self.search_dialog.deleteLater()
        except RuntimeError:
            pass
        finally:
            self.search_dialog = None

    def __create_dialog(self, use_indeter):
        if self.search_dialog is None:
            self.search_dialog = LoadBarDialog('正在搜索...', GlobalValue.TOP_WINDOWS, use_indeter)

    def __search_start(self, task: api.SearchTask):
        self.__create_dialog(not task.search_all)
        if not self.search_dialog.exec():
            task.stop()
            self.__close_dialog()

    def __search_progress(self, task: api.SearchTask):
        if self.search_dialog is not None:
            self.search_dialog.progress.setValue(task.progress.get_progress())

    def __search_finished(self, task: api.SearchTask):
        QTimer.singleShot(300, self.__close_dialog)
        if task.result() is not None:
            if self.search_dialog is not None:
                self.search_dialog.setText('搜索完成')
            page = task.result().loc[0, '当前页码']
            max_page = task.result().loc[0, '总页数']
            total = task.result().loc[0, '总数']
            self.parent.label_page_info.setText(f'{page}/{max_page}|{total}')
            # 设置页码最大值
            self.parent.spinBox.setMaximum(max_page)
        else:
            if self.search_dialog is not None:
                self.search_dialog.setText('搜索失败!')

    def __search_stop(self, value: bool):
        QTimer.singleShot(300, self.__close_dialog)
        if self.search_dialog is not None:
            self.search_dialog.setText('已停止搜索')

    @info_bar_decorator
    def lineEdit(self, value: int | str = None, is_top=False):
        """
        :param is_top:是否跳转
        """
        if self.search_dialog is not None:
            return None, '等待当前搜索完成', self.top_parent
        text = value if isinstance(value, str) else self.parent.lineEdit.text()
        page = value if isinstance(value, int) else 1
        if text:
            params = api.get_search_params()
            params.q = text
            params.page = page
            params.purity = self.parent.getPurity()
            params.categories = self.parent.getCategories()
            task = api.SearchTask(
                params, use_network=api.Config.USE_NETWORK, add_history=True,
                enable_tags_search=api.Config.USE_TAGS)
            self.search(task)
            if is_top:
                self.parent.tableWidget_image.scrollToTopSignal.emit(page)
            return None, '等待搜索结果...', self.top_parent
        return False, '请输入关键词', self.top_parent

    def clearTable(self):
        SEARCH_DATA.clear()
        self.parent.tableWidget_image.clearContents()

    def _spinBox(self):
        self.lineEdit(self.parent.spinBox.value(), True)

    def spinBox(self):
        self.spinbox_timer.start(500)

    def pushButton_expand(self):
        self.parent.widget_search_params.toggle()

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
        checked = bool(api.Config.API_KEY) if self.parent.checkBox_use_network.isChecked() else True
        self.parent.checkBox_nsfw.setEnabled(checked)

    def checkBox_use_tags(self, checked):
        SEARCH_DATA.clear()
        api.Config.USE_TAGS = checked

    def checkBox_use_network(self, checked):
        SEARCH_DATA.clear()
        if checked:
            api.Config.USE_NETWORK = True
        else:
            api.Config.USE_NETWORK = False


def start():
    win = SearchPage()
    win.show()
    return win


if __name__ == '__main__':
    from SubAPI import StartAPI

    start_api = StartAPI(func=start, console_level='DEBUG')
    start_api.start_thread()
