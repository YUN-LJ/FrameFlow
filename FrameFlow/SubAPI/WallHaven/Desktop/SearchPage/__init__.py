"""搜索窗口"""
from SubAPI.WallHaven.ImportPack import *
from SubAPI.WallHaven.Desktop.SearchPage.DesignFile.SearchPage import Ui_SearchPage
from SubAPI.WallHaven.Desktop.SearchPage.SearchConfig import SearchConfig
from SubAPI.WallHaven import api


class SearchPage(FluentWidgetFromUI, Ui_SearchPage):

    def __init__(self, parent=None):
        super().__init__(parent)
        parent = self if parent is None else parent
        self.slot = SearchSlot(self, parent)
        self.uiInit()
        self.bind()

    def uiInit(self):
        self.pushButton_expand.setIcon(FIF.MENU)

        self.widget_search_sidebar = SidebarWidgetCover(self.tableWidget_image)
        self.widget_search_sidebar.collapseSignal.connect(
            lambda: QTimer.singleShot(10, lambda: self.pushButton_expand.setEnabled(True))
        )
        self.search_config = SearchConfig(self)
        self.widget_search_sidebar.addWidget(self.search_config)

        self.setStyleSheet("""SearchPage, SearchPage * {background-color: transparent;}""")
        # for checkBox, color in zip(self.checkBoxsPurity, [QColor(0, 255, 0), QColor(255, 255, 0), QColor(170, 0, 0)]):
        #     checkBox.setTextColor(color, color)

    def bind(self):
        """信号连接"""
        self.pushButton_expand.clicked.connect(self.slot.pushButton_expand)
        self.search_config.pushButton_latest.clicked.connect(self.slot.pushButton_latest)
        self.search_config.pushButton_hot.clicked.connect(self.slot.pushButton_hot)
        self.lineEdit.searchSignal.connect(self.slot.lineEdit)
        self.lineEdit.returnPressed.connect(self.slot.lineEdit)
        self.lineEdit.clearSignal.connect(self.slot.clearTable)
        self.spinBox.valueChanged.connect(self.slot.spinBox)
        # 安装事件过滤器,用来执行自定义事件,让其事件先被self捕获
        self.lineEdit.installEventFilter(self)

    def getPurity(self) -> str:
        return self.search_config.wallhaven_class.getPurity()

    def getCategories(self) -> str:
        return self.search_config.wallhaven_class.getCategories()

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
        self.search_dialog: Optional[LoadBarDialog] = None  # 搜索对话框
        self.is_built_search = False  # 是否为内置搜索,搜索热门、最新等启用
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
        signal.searchSignal.connect(self.submit_search_task)
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

    def create_search_task(self, text, page=None, sorting=None, add_history=True) -> api.SearchTask:
        """
        创建搜索任务
        :param text:关键词
        :param page:页码
        :param sorting:根据什么排序,默认根据添加时间排序,views预览量,favorites收藏量,relevance关系,hot热门
        :param add_history:添加到历史搜索
        """
        page = page or 1
        sorting = sorting or 'date_added'
        # 构建搜索参数
        params = api.get_search_params()
        params.q = text
        params.page = page
        params.sorting = sorting
        params.purity = self.parent.getPurity()
        params.categories = self.parent.getCategories()
        # 创建搜索任务
        task = api.SearchTask(
            params,
            use_network=api.Config.USE_NETWORK,
            add_history=add_history,
            enable_tags_search=api.Config.USE_TAGS)
        return task

    def submit_search_task(self, task: api.SearchTask):
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

    def __search_stop(self, value: api.SearchTask):
        QTimer.singleShot(300, self.__close_dialog)
        if self.search_dialog is not None:
            self.search_dialog.setText('已停止搜索')

    @info_bar_decorator
    def lineEdit(self, value: int | str = None, is_top=False):
        """
        :param value:参数,int类型为指定页码,str类型为指定搜索关键词
        :param is_top:是否跳转
        """
        if self.search_dialog is not None:
            return None, '等待当前搜索完成', self.top_parent
        if isinstance(value, str):
            text = value
            self.is_built_search = False
        else:
            text = self.parent.lineEdit.text()
        page = value if isinstance(value, int) else 1
        if text or self.is_built_search:
            task = self.create_search_task(text, page)
            self.submit_search_task(task)
            if is_top:
                self.parent.tableWidget_image.scrollToTopSignal.emit(
                    self.parent.tableWidget_image.pageToRowIndex(page)
                )
            return None, '等待搜索结果...', self.top_parent
        return False, '请输入关键词', self.top_parent

    def clearTable(self):
        self.is_built_search = False
        SEARCH_DATA.clear()
        self.parent.tableWidget_image.clearContents()
        self.parent.label_page_info.setText('')

    def _spinBox(self):
        self.lineEdit(self.parent.spinBox.value(), True)

    def spinBox(self):
        self.spinbox_timer.start(500)

    def pushButton_expand(self):
        self.parent.widget_search_sidebar.toggle()
        self.parent.pushButton_expand.setEnabled(False)

    def pushButton_latest(self):
        self.is_built_search = True
        task = self.create_search_task('', add_history=False)
        self.submit_search_task(task)
        self.parent.tableWidget_image.scrollToTopSignal.emit(1)

    def pushButton_hot(self):
        self.is_built_search = True
        task = self.create_search_task('', sorting='hot', add_history=False)
        self.submit_search_task(task)
        self.parent.tableWidget_image.scrollToTopSignal.emit(1)


def start():
    win = SearchPage()
    win.show()
    return win


if __name__ == '__main__':
    from SubAPI import StartAPI, StartEnum

    start_api = StartAPI(func=start, console_level=StartEnum.LogLevel.DEBUG)
    start_api.start_thread()
