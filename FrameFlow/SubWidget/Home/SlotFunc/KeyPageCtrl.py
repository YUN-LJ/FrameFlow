"""下载界面控制文件"""
from SubWidget.Home.ImportPack import *
from SubWidget.Home.SlotFunc.WorkFlow import UpdateWorkFlow, SerialWorkFlow
from typing import Optional

ROW_HEIGHT = 80


class Table(GroupBoxTable):
    """表格数据展示"""
    __timer_start_signal = Signal()  # 定时器启动信号
    submit_download_task = Signal(list)  # 提交需要下载的任务,[(关键词,url)]

    def __init__(self, parent=None):
        super().__init__(parent)
        header = GlobalValue.key_word_columns.copy()
        header.append('更新状态')
        self.setColumnHeader(header)
        self.enable_adaptive_row_height = False
        self.verticalScrollBar().setSingleStep(int(ROW_HEIGHT / 3))
        self.mouseRightClickedSignal.connect(self.showRoundMenu)
        # 设置列宽模式
        self.verticalHeader().setVisible(True)  # 显示左侧行头
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # 关键词
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # 最新日期
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)  # 上次更新
        self.horizontalHeader().setSectionResizeMode(self.columnCount() - 1, QHeaderView.Stretch)  # 最后一列
        # header.setSectionResizeMode(QHeaderView.Interactive) # 允许调整用户调整列宽

        self.work_flow = SerialWorkFlow()  # 用于批量更新关键词
        self.key_word_queue = Queue()  # 待提交的任务
        self.all_rows: dict[str, Row] = {}  # 全部行数据{关键词:一行数据}
        self.selected_rows: list[Row] = []  # 被选中的任务
        self.__timer_isRunning = False
        self.__timer_start_signal.connect(lambda: QTimer.singleShot(0, self.__submit_task))
        KeyWord.load_callback(self.addKeyWord)

    def showRoundMenu(self, row, col, pos: QPoint):
        key_word = self.cellWidget(row, 0).text()
        menu = RoundMenu(parent=self)
        # 逐个添加动作，Action 继承自 QAction，接受 FluentIconBase 类型的图标
        menu.addAction(Action(FIF.SEARCH, '搜索关键词', triggered=lambda: AppCore().getSignal('search').emit(key_word)))
        menu.addAction(Action(FIF.DELETE, '删除关键词', triggered=lambda: self.delKeyWord([key_word])))
        # 显示菜单
        pos.setX(pos.x() + (menu.width() / 2))
        pos.setY(pos.y() + (menu.height() / 2))
        menu.exec(pos)

    def searchKey(self, key_word) -> bool:
        if key_word in self.all_rows:  # 精准搜索
            row_index, _ = self.getWidgetCoord(self.all_rows[key_word].checkbox, 0)
            item = self.item(row_index, 1)
            self.scrollToItem(item, QAbstractItemView.PositionAtTop)
            return True
        else:
            for row in self.all_rows.values():  # 模糊搜索
                if row.checkbox.text().find(key_word) == 0:
                    row_index, _ = self.getWidgetCoord(row.checkbox, 0)
                    item = self.item(row_index, 1)
                    self.scrollToItem(item, QAbstractItemView.PositionAtTop)
                    return True
        return False

    def selectNotUpdateRows(self):
        """选择未完成更新的行"""
        for row in self.all_rows.copy().values():
            if not row.isUpdate:
                row.checkbox.setChecked(True)

    def selectAllRows(self, value=True):
        for row in self.all_rows.copy().values():
            row.checkbox.setChecked(value)

    def addKeyWord(self, key_data: pd.DataFrame):
        """添加收藏夹数据"""
        for index, row_data in key_data.iterrows():
            self.key_word_queue.put(row_data)
        if not self.__timer_isRunning:
            self.__timer_start_signal.emit()

    def delKeyWord(self, key_word: list = None):
        if key_word is None:
            for row in self.selected_rows:
                KeyWord.del_data(row.key_word)
                self.delRow(row.checkbox, column_index=0)
        else:
            for key in key_word:
                KeyWord.del_data(key)
                self.delRow(self.all_rows[key].checkbox, column_index=0)

    def updateKeyWord(self, value: bool = True):
        if value:
            self.work_flow.add_task([row.work_flow for row in self.selected_rows])
            if not self.work_flow.isRunning:
                self.work_flow.start()
        else:
            self.work_flow.stop()

    def rowCheckBoxSlot(self, checked, value: Optional['Row']):
        if checked:
            self.work_flow.add_task(value.work_flow)
            self.selected_rows.append(value)
        else:
            self.work_flow.del_task(value.work_flow)
            self.selected_rows.remove(value)

    def __submit_task(self):
        try:
            self.__timer_isRunning = True
            row_data: pd.Series = self.key_word_queue.get(timeout=1)
            row = self.all_rows.get(row_data['关键词'], None)
            if row is None:
                row = Row(row_data, self)
                row.checkbox.stateChanged.connect(
                    lambda checked, value=row: self.rowCheckBoxSlot(checked, value))
                self.all_rows[row_data['关键词']] = row
                self.addRow(row.row_data, height=ROW_HEIGHT)
                # 防止自动布局显示不全
                row.checkbox.setMinimumWidth(len(row.key_word) * 15)
            else:
                row.setRowData(row_data)
                row_index, _ = self.getWidgetCoord(row.checkbox)
                for index in range(1, 7):
                    item = self.item(row_index, index)
                    item.setText(row.row_data[index])
            QTimer.singleShot(10, self.__submit_task)
        except Empty:
            self.__timer_isRunning = False

    def stopUpdate(self):
        for row in self.all_rows.values():
            row.work_flow.stop()


class Row(QObject):
    """一行数据"""
    progressSignal = Signal(object)  # 进度条更新信号
    startSignal = Signal(WH.SearchTask)
    finishedSignal = Signal(bool)
    stopSignal = Signal(bool)

    def __init__(self, value: pd.Series, parent: Table = None):
        super().__init__(parent)
        self.__parent = parent
        self.isUpdate = False  # 是否已更新
        self.setRowData(value)
        # 信号连接
        self.startSignal.connect(self.__start)
        self.progressSignal.connect(self.__progress)
        self.finishedSignal.connect(self.__finished)
        self.stopSignal.connect(self.__stop)
        # 工作流
        self.work_flow = UpdateWorkFlow(
            self.key_word, self.purity, self.categories,
            self.startSignal, self.progressSignal, self.finishedSignal)
        self.work_flow.stop_signal.connect(self.stopSignal.emit)
        self.uiInit()

    @property
    def row_data(self):
        return [
            self.checkbox, self.total_page, self.total_image,
            self.date_last, self.date_update,
            self.purity, self.categories, self.widget
        ]  # 一行可添加至tabel表格中的数据

    def setRowData(self, value: pd.Series):
        self.pd_series = value
        self.key_word = value['关键词']
        self.total_page = str(value['总页数'])
        self.total_image = str(value['总数'])
        self.date_last = str(value['最新日期'])
        self.date_update = str(value['上次更新'])
        self.purity = value['分级码']
        self.categories = value['类别码']

    def uiInit(self):
        self.checkbox = CheckBox(text=self.key_word, parent=self.__parent)
        self.widget = QWidget(self.__parent)
        self.layout_v = QVBoxLayout(self.widget)
        self.layout_h = QHBoxLayout(self.widget)
        # 进度条
        self.progress = ProgressRing(self.widget)
        self.progress.setTextVisible(True)
        self.progress.setFixedSize(50, 50)
        self.progress.setStrokeWidth(2)
        # 进度条状态
        self.label = QLabel('', self.widget)
        # 按钮
        self.button = PrimaryToolButton(FIF.UPDATE)
        self.button.clicked.connect(self.__button_slot)

        self.layout_v.addLayout(self.layout_h)
        self.layout_v.addWidget(self.label)
        self.layout_h.addWidget(self.progress)
        self.layout_h.addWidget(self.button)

    def __button_slot(self):
        if self.button._icon == FIF.UPDATE:
            self.work_flow.start()
        elif self.button._icon == FIF.CLOSE:
            self.work_flow.stop()

    def __start(self):
        self.progress.setValue(0)
        self.label.setText('检查更新中')
        self.button.setIcon(FIF.CLOSE)
        self.checkbox.setChecked(True)
        row_index, _ = self.__parent.getWidgetCoord(self.checkbox, 0)
        item = self.__parent.item(row_index, 1)
        self.__parent.scrollToItem(item, QAbstractItemView.PositionAtTop)

    def __progress(self, value: WH.SearchTask | list | UpdateWorkFlow):
        if isinstance(value, WH.SearchTask):  # 搜索全部的云端数据
            self.progress.setValue(value.progress.get_progress())
            self.label.setText(f'搜索中:{value.progress.finished}/{value.progress.total}')
        elif isinstance(value, list):  # 提交需要下载的图像
            self.progress.setValue(0)
            self.label.setText('等待下载')
            self.__parent.submit_download_task.emit(value)
        elif isinstance(value, TaskProgress):  # 等待待下载图像
            self.progress.setValue(int((value.finished / value.total) * 100))
            self.label.setText(f'下载中{value.finished}/{value.total}')

    def __finished(self, value: bool):
        """任务完成"""
        if value:
            self.isUpdate = True
            self.progress.setValue(100)
            self.button.setIcon(FIF.UPDATE)
            self.label.setText('更新完成')
            # 更新UI数据
            if self.work_flow.local_key_data is not None:
                self.__parent.addKeyWord(self.work_flow.local_key_data)
            self.checkbox.setChecked(False)
        else:
            self.label.setText('更新失败')

    def __stop(self, value):
        self.checkbox.setChecked(False)
        self.button.setIcon(FIF.UPDATE)
        self.progress.setValue(0)
        self.label.setText('更新取消')

    def updateKey(self):
        """更新关键词"""
        self.work_flow.start()
