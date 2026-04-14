"""下载界面控制文件"""
from SubWidget.ImportPack import *
from ImportFile import Config
from SubWidget.Home.SlotFunc.WorkFlow import UpdateWorkFlow, SerialWorkFlow

ROW_HEIGHT = 80


class Row(QObject):
    """一行数据"""
    progressSignal = Signal(object)  # 进度条更新信号
    startSignal = Signal(WH.SearchTask)
    finishedSignal = Signal(bool)
    stopSignal = Signal(bool)

    def __init__(self, value: pd.Series, parent: 'Table' = None):
        super().__init__(parent)
        self.__parent = parent
        self.isUpdate = False  # 是否已更新
        self.setRowData(value)
        self.uiInit()
        # 信号连接
        self.startSignal.connect(self.__start)
        self.progressSignal.connect(self.__progress)
        self.finishedSignal.connect(self.__finished)
        self.stopSignal.connect(self.__stop)
        # 工作流
        self.work_flow = self.__parent.table_data.getWorkFlow(self.key_word)
        self.work_flow.setSignal(self.startSignal, self.progressSignal, self.finishedSignal, self.stopSignal)
        if self.work_flow.isRunning:
            self.__start()

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
        if self.key_word in self.__parent.selected_rows:
            self.checkbox.setChecked(True)
        self.checkbox.stateChanged.connect(self.__checkBoxSlot)
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

    def __checkBoxSlot(self, checked):
        if checked:
            self.__parent.selected_rows.append(self.key_word)
        else:
            self.__parent.selected_rows.remove(self.key_word)

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
                self.__parent.ensurerDataConsistency(self.work_flow.local_key_data)
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


class SelectRow(QObject):
    """关键词选择管理类"""
    keyAppendSignal = Signal(str)  # 关键词选中信号
    keyRemoveSignal = Signal(str)  # 关键词取消信号

    def __init__(self, parent: 'Table'):
        super().__init__()
        self._items = []  # 内部存储
        self.__parent = parent

    def append(self, key_word: str, emit: bool = True):
        """添加关键词"""
        if key_word not in self._items:
            self._items.append(key_word)
            self.__parent.work_flow.add_task(self.__parent.table_data.getWorkFlow(key_word))
            if emit:
                self.keyAppendSignal.emit(key_word)

    def remove(self, key_word: str, emit: bool = True):
        """移除关键词"""
        if key_word in self._items:
            self._items.remove(key_word)
            self.__parent.work_flow.del_task(self.__parent.table_data.getWorkFlow(key_word))
            if emit:
                self.keyRemoveSignal.emit(key_word)

    def __contains__(self, key_word: str) -> bool:
        """支持 in 操作符"""
        return key_word in self._items

    def __len__(self) -> int:
        """支持 len() 函数"""
        return len(self._items)

    def get_items(self) -> list[str]:
        """获取所有项目（返回副本）"""
        return self._items.copy()


class TableData(QThread):
    """表格数据层"""
    finished = Signal()  # 完成信号

    def __init__(self, parent: 'Table'):
        super().__init__(parent)
        self.all_work_flow: dict[str, UpdateWorkFlow] = {}

    def getWorkFlow(self, key_word: str) -> UpdateWorkFlow:
        if key_word in self.all_work_flow:
            return self.all_work_flow[key_word]

    def createWorkFlow(self, key_word, purity, categories) -> UpdateWorkFlow:
        """创建/修改已存在工作流的参数"""
        if key_word in self.all_work_flow:
            work_flow = self.all_work_flow[key_word]
            work_flow.params.purity = purity
            work_flow.params.categories = categories
        else:
            work_flow = UpdateWorkFlow(key_word, purity, categories)
            self.all_work_flow[key_word] = work_flow
        return work_flow

    def run(self):
        if KeyWord.is_loaded(1):
            with KeyWord.lock:
                df = KeyWord.data()[['关键词', '分级码', '类别码']].values.tolist()
            for key_word, purity, categories in df:
                self.createWorkFlow(key_word, purity, categories)
            self.finished.emit()


class Table(TableRow):
    """表格数据展示"""
    submit_download_task = Signal(list)  # 提交需要下载的任务,[(关键词,url)]

    def __init__(self, parent=None):
        super().__init__(parent)
        header = GlobalValue.key_word_columns.copy()
        header.append('更新状态')
        self.setColumnHeader(header)
        self.enableResizeRowsToContents(False)
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
        self.selected_rows = SelectRow(self)  # 被选中的任务
        self.selected_rows.keyAppendSignal.connect(lambda key_word: self.__selectedRowsSlot(key_word, True))
        self.selected_rows.keyRemoveSignal.connect(lambda key_word: self.__selectedRowsSlot(key_word, False))
        self.table_data = TableData(self)
        self.table_data.finished.connect(self.loadVisible)
        self.table_data.start()

    def __selectedRowsSlot(self, key_word: str, checked: bool):
        row = self.all_rows.get(key_word, None)
        if row is not None:
            row.checkbox.setChecked(checked)

    def loadVisible(self, rows: list = None):
        """加载当前可见区域单元格"""
        if not KeyWord.is_loaded():
            return
        with KeyWord.lock:
            data_len = KeyWord.data().shape[0]
        if self.rowCount() != data_len:
            self.setRowCount(data_len)
        rows = self.visibleRow(False) if rows is None else rows
        for row in rows:
            with KeyWord.lock:
                row_data = KeyWord.data().iloc[row].copy(deep=True)
            # 检查行是否为空
            checkbox: CheckBox = self.cellWidget(row, 0)
            if checkbox is None or checkbox.text() != row_data['关键词']:
                cell = Row(row_data, self)
                self.all_rows[cell.key_word] = cell
                self.addRow(row, cell.row_data)
                self.resizeRowsToContents()

    def ensurerDataConsistency(self, row_data: pd.DataFrame) -> bool:
        """确保数据一致"""
        row = self.all_rows[row_data.loc[0, '关键词']]
        row.setRowData(row_data.iloc[0])
        row_index, _ = self.getWidgetCoord(row.checkbox, column_index=0)
        self.changeRowItem(row_index, row.row_data)
        return True

    def resizeRowsToContents(self):
        super().resizeRowsToContents()
        for index_row in range(self.rowCount()):
            self.setRowHeight(index_row, ROW_HEIGHT)

    def showEvent(self, event):
        super().showEvent(event)
        self.loadVisible()

    def showRoundMenu(self, row, col, pos: QPoint):
        def sub_func():
            nonlocal key_word
            if Config.TOP_WINDOWS is not None:
                load_dialog = MessageBox(
                    '确认删除',
                    f'是否删除关键词{key_word}?',
                    parent=Config.TOP_WINDOWS)
                if load_dialog.exec():
                    self.delKeyWord(key_word)

        checkbox = self.cellWidget(row, 0)
        if checkbox is not None:
            key_word = checkbox.text()
            menu = RoundMenu(parent=self)
            # 逐个添加动作，Action 继承自 QAction，接受 FluentIconBase 类型的图标
            menu.addAction(
                Action(FIF.SEARCH, '搜索关键词', triggered=lambda: AppCore().getSignal('search').emit(key_word)))
            menu.addAction(Action(FIF.DELETE, '删除关键词', triggered=sub_func))
            # 显示菜单
            pos.setX(pos.x() + (menu.width() / 4))
            pos.setY(pos.y() + (menu.height() / 4))
            menu.exec(pos)

    def searchKey(self, key_word) -> bool:
        with KeyWord.lock:
            if key_word in KeyWord.data()['关键词'].values:  # 精准搜索
                row_index = KeyWord.data()[KeyWord.data()['关键词'] == key_word].index[0]
                index = self.model().index(row_index, 0)
                self.scrollTo(index, QAbstractItemView.PositionAtTop)
                return True
            else:  # 模糊搜索
                key_word = key_word.lower()
                row_index = None
                # 方法1：分步匹配，优先开头匹配
                df = KeyWord.data()
                # 先找以key_word开头的
                mask_start = df['关键词'].str.contains(f'^{re.escape(key_word)}', regex=True, case=False, na=False)
                if mask_start.any():
                    row_index = df[mask_start].index[0]
                else:
                    # 如果没有开头匹配，找包含key_word的
                    mask_contains = df['关键词'].str.contains(re.escape(key_word), regex=True, case=False, na=False)
                    if mask_contains.any():
                        row_index = df[mask_contains].index[0]
                if row_index is not None:
                    index = self.model().index(row_index, 0)
                    self.scrollTo(index, QAbstractItemView.PositionAtTop)
                    return True
            return False

    def selectAllRows(self, value=True):
        with KeyWord.lock:
            df = KeyWord.data()['关键词'].tolist()
        for key_word in df:
            if value:
                self.selected_rows.append(key_word)
            else:
                self.selected_rows.remove(key_word)

    def addKeyWord(self, key_data: pd.DataFrame):
        """添加收藏夹数据"""
        self.table_data.start()
        self.table_data.finished.disconnect()
        self.table_data.finished.connect(lambda key_word=key_data.loc[0, '关键词']: self.searchKey(key_word))
        self.table_data.finished.connect(self.loadVisible)

    def delKeyWord(self, key_word=None):
        if key_word is None:
            for key_word in self.selected_rows.get_items():
                KeyWord.del_data(key_word)
                row = self.all_rows.get(key_word, None)
                if row is not None:
                    row_index, _ = self.getWidgetCoord(row.checkbox, column_index=0)
                    # 清除元素
                    del self.all_rows[key_word]
                    self.delRow(row_index)
        else:
            KeyWord.del_data(key_word)
            row = self.all_rows.get(key_word, None)
            if row is not None:
                row_index, _ = self.getWidgetCoord(row.checkbox, column_index=0)
                # 清除元素
                del self.all_rows[key_word]
                self.delRow(row_index)

    def updateKeyWord(self, value: bool = True):
        if value:
            if not self.work_flow.isRunning:
                self.work_flow.start()
        else:
            self.work_flow.stop()
