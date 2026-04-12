"""下载界面控制文件"""
from SubWidget.ImportPack import *
from SubWidget.Home.SlotFunc.WorkFlow import DownloadWorkFlow

ROW_HEIGHT = 60


class Row(QObject):
    """一行数据"""
    startSignal = Signal(WH.ImageInfoTask)
    progressSignal = Signal(TaskProgress)  # 进度条更新信号
    finishedSignal = Signal(bool)
    stopSignal = Signal(bool)

    def __init__(self, work_flow: DownloadWorkFlow, parent: 'Table'):
        super().__init__(parent)
        self.parent = parent
        self.key_word = work_flow.key_word
        self.url = work_flow.url
        # 信号连接
        self.startSignal.connect(self.__start)
        self.progressSignal.connect(self.__progress)
        self.finishedSignal.connect(self.__finished)
        self.startSignal.connect(self.__stop)
        # 工作流
        self.work_flow = work_flow
        self.work_flow.setSignal(self.startSignal, self.progressSignal, self.finishedSignal, self.stopSignal)
        self.uiInit()

    def uiInit(self):
        self.check_box = CheckBox(self.work_flow.image_data.image_id)  # 图像ID
        if self.work_flow in self.parent.selected_rows:
            self.check_box.setChecked(True)
        self.check_box.stateChanged.connect(self.__checkBoxSlot)
        self.widget = QWidget()  # 下载进度
        self.label = QLabel()
        self.progress = QProgressBar(minimum=0, maximum=100)
        self.progress.setTextVisible(True)
        self.progress_layout = QVBoxLayout(self.widget)
        self.progress_layout.addWidget(self.progress)
        self.progress_layout.addWidget(self.label)

        self.button = PrimaryToolButton(FIF.PLAY)  # 操作按钮
        self.button.setFixedSize(40, 40)
        self.button.clicked.connect(self.__button_slot)

    @property
    def rowData(self) -> list:
        return [self.check_box, self.widget, self.button]

    def __checkBoxSlot(self, checked):
        if checked:
            self.parent.selected_rows.append(self.work_flow)
        else:
            self.parent.selected_rows.remove(self.work_flow)

    def __button_slot(self):
        """操作按钮槽函数"""
        if self.button._icon == FIF.PLAY or self.button._icon == FIF.ROTATE:
            self.work_flow.start()
        elif self.button._icon == FIF.DELETE:
            self.work_flow.stop()
            self.parent.delDownload(self.work_flow)

    def __start(self, task: WH.ImageInfoTask):
        try:
            self.progress.setValue(0)
            self.label.setText('连接资源中')
            self.button.setIcon(FIF.DELETE)
        except RuntimeError:
            pass

    def __progress(self, value: TaskProgress):
        try:
            if self.button._icon == FIF.PLAY:
                self.button.setIcon(FIF.DELETE)
            self.progress.setValue(value.get_progress())
            size_text = f'{value.finished / 1024 / 1024:0.2f}MB/{value.total / 1024 / 1024:0.2f}MB' if value.total / 1024 / 1024 > 1 else f'{value.finished / 1024:0.2f}KB/{value.total / 1024:0.2f}KB'
            rate_text = f'速度:{value.rate / 1024:0.2f}MB/S' if value.rate / 1024 > 1.2 else f'速度:{value.rate:0.2f}KB/S'
            self.label.setText(f'{size_text} {rate_text}')
        except RuntimeError:
            pass

    def __finished(self, value: bool):
        """任务完成"""
        icon = InfoBarIcon.ERROR
        title = self.work_flow.image_data.image_id
        content = '下载失败'
        if value:
            try:
                self.progress.setValue(100)
                self.label.setText('下载成功')
                self.button.setEnabled(False)
            except RuntimeError:
                pass
            QTimer.singleShot(2000, lambda: self.parent.delDownload(self.work_flow))
            icon = InfoBarIcon.SUCCESS
            content = '下载成功'
        else:
            try:
                self.label.setText('下载失败')
                self.button.setIcon(FIF.ROTATE)
            except RuntimeError:
                pass
        if self.parent.isVisible():
            InfoBar.new(
                icon=icon, title=title, content=content, orient=Qt.Horizontal,
                isClosable=True, position=InfoBarPosition.TOP,
                duration=1000, parent=self.parent)

    def __stop(self, value: bool):
        try:
            self.check_box.setEnabled(False)
            self.button.setEnabled(False)
        except RuntimeError:
            pass
        self.parent.delDownload(self.work_flow)


class SelectRow(QObject):
    """关键词选择管理类"""
    keyAppendSignal = Signal(DownloadWorkFlow)  # 图像ID选中信号
    keyRemoveSignal = Signal(DownloadWorkFlow)  # 图像ID取消信号

    def __init__(self, parent: 'Table'):
        super().__init__()
        self._items = []  # 内部存储
        self.__parent = parent

    def append(self, work_flow: DownloadWorkFlow, emit: bool = True):
        """添加关键词"""
        if work_flow not in self._items:
            self._items.append(work_flow)
            if emit:
                self.keyAppendSignal.emit(work_flow)

    def remove(self, work_flow: DownloadWorkFlow, emit: bool = True):
        """移除关键词"""
        if work_flow in self._items:
            self._items.remove(work_flow)
            if emit:
                self.keyRemoveSignal.emit(work_flow)

    def __contains__(self, work_flow: DownloadWorkFlow) -> bool:
        """支持 in 操作符"""
        return work_flow in self._items

    def __len__(self) -> int:
        """支持 len() 函数"""
        return len(self._items)

    def get_items(self) -> list[DownloadWorkFlow]:
        """获取所有项目（返回副本）"""
        return self._items.copy()


class TableData(QThread):
    """表格数据层"""
    finished = Signal()  # 数据加载完成

    def __init__(self, parent: 'Table'):
        super().__init__(parent)
        self.wait_add_queue = Queue()  # 待添加任务(关键词,下载地址)
        self.all_work_flow = []
        self.__lock = Lock()

    def submit(self, image_url: list):
        """新增下载任务"""
        for download_args in image_url:
            self.wait_add_queue.put(download_args)
        if not self.isRunning():
            self.start()

    def work_flow_finished(self, work_flow):
        """任务完成后删除该任务"""
        with self.__lock:
            if work_flow in self.all_work_flow:
                self.all_work_flow.remove(work_flow)

    def createWorkFlow(self, key_word, image_url) -> DownloadWorkFlow:
        """创建/修改已存在工作流的参数"""
        work_flow = DownloadWorkFlow(key_word, image_url)
        work_flow.add_done_callback(lambda key=work_flow: self.work_flow_finished(key))
        with self.__lock:
            self.all_work_flow.append(work_flow)
        return work_flow

    def getWorkFlow(self, index=None) -> list[DownloadWorkFlow] | DownloadWorkFlow:
        with self.__lock:
            if index is None:
                return self.all_work_flow.copy()
            else:
                if index < len(self.all_work_flow):
                    return self.all_work_flow[index]

    def getWorkFlowCount(self) -> int:
        with self.__lock:
            return len(self.all_work_flow)

    def run(self):
        while self.isRunning():
            try:
                key_word, image_url = self.wait_add_queue.get(timeout=1)
                self.createWorkFlow(key_word, image_url)
            except Empty:
                self.finished.emit()
                break


class Table(TableRow):
    """表格数据展示"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnHeader(['图像ID', '下载进度', '操作'])
        self.enableResizeRowsToContents(False)
        self.verticalScrollBar().setSingleStep(int(ROW_HEIGHT / 3))
        # 设置列宽模式
        self.verticalHeader().setVisible(True)  # 显示左侧行头
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # 下载进度

        self.all_rows: dict[str, Row] = {}  # 全部行{url,Row}
        self.selected_rows = SelectRow(self)  # 被选中的任务
        self.selected_rows.keyAppendSignal.connect(lambda work_flow: self.__selectedRowsSlot(work_flow, True))
        self.selected_rows.keyRemoveSignal.connect(lambda work_flow: self.__selectedRowsSlot(work_flow, False))
        self.table_data = TableData(self)
        self.table_data.finished.connect(self.loadVisible)

    def __selectedRowsSlot(self, work_flow: DownloadWorkFlow, checked: bool):
        row = self.all_rows.get(work_flow.url, None)
        if row is not None:
            row.check_box.setChecked(checked)

    def loadVisible(self, rows: list = None):
        data_len = self.table_data.getWorkFlowCount()
        if self.rowCount() != data_len:
            self.setRowCount(data_len)
        rows = self.visibleRow(False) if rows is None else rows
        # 检查行是否为空
        for row_index in rows:
            work_flow = self.table_data.getWorkFlow(row_index)
            if work_flow is not None:
                checkbox: CheckBox = self.cellWidget(row_index, 0)
                if checkbox is None or checkbox.text() != work_flow.image_data.image_id:
                    row = Row(work_flow, self)
                    self.addRow(row_index, row.rowData)
                    row.check_box.setMinimumWidth(len(row.check_box.text()) * 15)
                    self.all_rows[row.url] = row

    def resizeRowsToContents(self):
        super().resizeRowsToContents()
        for index_row in range(self.rowCount()):
            self.setRowHeight(index_row, ROW_HEIGHT)

    def selectAllRows(self, value=True):
        for workflow in self.table_data.getWorkFlow():
            if value:
                self.selected_rows.append(workflow)
            else:
                self.selected_rows.remove(workflow)

    def startDownload(self):
        for work_flow in self.selected_rows.get_items():
            work_flow.start()

    def delDownload(self, work_flow: DownloadWorkFlow = None):
        if work_flow is None:
            for work_flow in self.selected_rows.get_items():
                work_flow.stop()
                self.selected_rows.remove(work_flow)
                self.table_data.work_flow_finished(work_flow)
                row = self.all_rows.get(work_flow.url, None)
                if row is not None:
                    row_index, _ = self.getWidgetCoord(row.check_box, 0)
                    if row_index > -1:
                        self.delRow(row_index)
        else:
            work_flow.stop()
            self.selected_rows.remove(work_flow)
            self.table_data.work_flow_finished(work_flow)
            row = self.all_rows.get(work_flow.url, None)
            if row is not None:
                row_index, _ = self.getWidgetCoord(row.check_box, 0)
                if row_index > -1:
                    self.delRow(row_index)
        self.loadVisible()

    def addImageUrl(self, image_url: tuple | list):
        """
        添加图像下载
        :param image_url:[(key,url)]
        """
        if isinstance(image_url, tuple):
            image_url = [image_url]
        self.table_data.submit(image_url)
