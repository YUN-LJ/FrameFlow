"""下载界面控制文件"""
from SubAPI.WallHaven.ImportPack import *
from SubAPI.WallHaven import api
from SubAPI.WallHaven.api.WorkFlow import UpdateWorkFlow, SerialUpdateWorkFlow

ROW_HEIGHT = 80
TIMEOUT = 50  # 定时器超时时间ms


# 进度单元格
class LikeTableProgressCell(QWidget):
    """更新进度条"""

    def __init__(self, parent: 'LikeTable' = None):
        super().__init__(parent)
        self.parent = parent
        self.progress = ProgressRing(self)
        self.progress.setTextVisible(True)
        size = min(int(ROW_HEIGHT * 0.5),
                   int(parent.columnWidth(parent.columnCount() - 1) * 0.5))
        self.progress.setFixedSize(QSize(size, size))
        self.progress.setStrokeWidth(4)
        self.label = CaptionLabel(self)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.progress, 0, Qt.AlignmentFlag.AlignVCenter)
        self.layout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignVCenter)

    def setValue(self, value):
        self.progress.setValue(value)

    def setText(self, text):
        self.label.setText(text)


# 右键菜单
class LikeRoundMenu(RoundMenu):
    """右键菜单"""

    def __init__(self, row_data: pd.Series, pos: QPoint, parent: 'LikeTable'):
        self.parent = parent
        super().__init__(parent=parent)
        self.row_data = row_data
        # 逐个添加动作，Action 继承自 QAction，接受 FluentIconBase 类型的图标
        self.addAction(Action(FIF.SEARCH, '搜索关键词', triggered=self.searchKeyWord))
        self.addAction(Action(FIF.COPY, '复制关键词', triggered=self.copyKeyWord))
        self.addAction(Action(FIF.CHECKBOX, '全选', triggered=self.selectAll))
        self.addAction(Action(FIF.CHECKBOX, '全选后续项', triggered=self.selectLater))
        self.addAction(Action(FIF.CHECKBOX, '取消全选', triggered=self.dissectAll))
        self.addAction(Action(FIF.DELETE, '删除关键词', triggered=self.deleteKeyWord))
        # 显示菜单
        self.exec(pos)

    def searchKeyWord(self):
        params = api.get_search_params()
        params.q = self.row_data['关键词']
        params.purity = self.row_data['分级码']
        params.categories = self.row_data['类别码']
        task = api.SearchTask(
            params, use_network=api.Config.USE_NETWORK, add_history=True, enable_tags_search=api.Config.USE_TAGS)
        SignalConfig.WallHavenSignal.search_signal.searchSignal.emit(task)

    def copyKeyWord(self):
        """复制图像关键词"""
        copy_text_to_clipboard(self.row_data['关键词'])

    @info_bar_decorator
    def selectAll(self):
        """全选"""
        row_count = self.parent.data_model.rowCount()
        for row in range(row_count):
            self.parent.data_model.setCellData(row, 0, True)
        return True, f'已选择{row_count}项任务', self.parent

    @info_bar_decorator
    def selectLater(self):
        """全选后续项"""
        row_index = self.parent.data_model.getKeyWordRowIndex(self.row_data['关键词'])
        row_count = self.parent.data_model.rowCount()
        for row in range(row_index, row_count):
            self.parent.data_model.setCellData(row, 0, True)
        return True, f'已选择{row_count - row_index}项任务', self.parent

    @info_bar_decorator
    def dissectAll(self):
        """取消全选"""
        row_count = self.parent.data_model.rowCount()
        for row in range(row_count):
            self.parent.data_model.setCellData(row, 0, False)
        return True, f'已取消选择{row_count}项任务', self.parent

    @info_bar_decorator
    def deleteKeyWord(self):
        """删除关键词"""
        key_word = self.row_data['关键词']
        message = MessageBox('确认删除', f'是否删除{key_word}？', GlobalValue.TOP_WINDOWS)
        if message.exec() and self.parent.delKeyWord(key_word):
            return True, f'已删除{key_word}', self.parent
        return False, f'已取消', self.parent


# 表格三件套
class LikeTableData(DataFrameModelBase):
    """表格数据模型,内部连接了KEY_WORD数据变化信号"""
    workflowTaskStartSignal = Signal(object)
    workflowTaskProgressSignal = Signal(object)
    workflowTaskFinishSignal = Signal(object)
    workflowTaskStopSignal = Signal(object)

    def __init__(self, parent: 'LikeTable' = None):
        super().__init__(parent=parent)
        self.__parent = parent
        self.setColumnCount(len(DataConfig.key_word_columns) + 2)
        # 创建后端工作流
        self._create_work_flow()
        self.dataChange.connect(self._select_workflow)
        # 创建防抖定时器
        self.__data_change_timer = ReuseTimer(TIMEOUT // 1000, self._load_key_word)
        self.__data_change_timer.setSingleShot(True)
        # 绑定数据加载和改变信号
        KEY_WORD.load_callback(lambda _: self._data_change_lazy())
        KEY_WORD.change_signal.connect(lambda _: self._data_change_lazy())

    def _select_workflow(self, row, col, value):
        """选择后端工作流"""
        if col == 0:
            row_data = self.getRowData(row)
            if value:
                self.work_flow.add_task(row_data['关键词'], row_data['分级码'], row_data['类别码'])
            else:
                self.work_flow.del_task(row_data['关键词'], row_data['分级码'], row_data['类别码'])

    def _create_work_flow(self):
        def current_task_start_slot(task: UpdateWorkFlow | api.KeyWordTask):
            if isinstance(task, UpdateWorkFlow):
                key_word = task.key_word
                text = '更新开始'
                self.__parent.scrollToTopSignal.emit(key_word)
                row = self.getKeyWordRowIndex(key_word)
                col = self.columnCount() - 1
                self.setCellData(row, col, f'0;{text}')
            elif isinstance(task, api.KeyWordTask):
                key_word = task.params.q
                text = '对比完成'
                row = self.getKeyWordRowIndex(key_word)
                col = self.columnCount() - 1
                self.setCellData(row, col, f'0;{text}')

        def current_task_progress_slot(task: UpdateWorkFlow):
            text = f'搜索中' if task.get_progress_state == task.SEARCH_STATE else '下载中'
            row = self.getKeyWordRowIndex(task.key_word)
            col = self.columnCount() - 1
            self.setCellData(row, col,
                             f'{task.progress.get_progress()};'
                             f'{text}:{task.progress.finished}/{task.progress.total}')
            SignalConfig.WallHavenSignal.download_signal.refreshViewSignal.emit()

        def current_task_finish_slot(task: UpdateWorkFlow):
            text = '更新失败' if task.result() is None else '更新成功'
            row = self.getKeyWordRowIndex(task.key_word)
            col = self.columnCount() - 1
            self.setCellData(row, col, f'100;{text}')
            if task.result():
                self.setCellData(row, 0, False)

        def current_task_stop_slot(task: UpdateWorkFlow):
            row = self.getKeyWordRowIndex(task.key_word)
            col = self.columnCount() - 1
            self.setCellData(row, col, '0;更新取消')

        self.work_flow = SerialUpdateWorkFlow()  # 用于批量更新关键词
        signal = SignalConfig.WallHavenSignal.like_signal
        self.work_flow.start_signal.bridge_signal(signal.startSignal)
        self.work_flow.progress_signal.bridge_signal(signal.progressSignal)
        self.work_flow.finish_signal.bridge_signal(signal.finishSignal)
        self.work_flow.stop_signal.bridge_signal(signal.stopSignal)

        self.workflowTaskStartSignal.connect(current_task_start_slot)
        self.workflowTaskProgressSignal.connect(current_task_progress_slot)
        self.workflowTaskFinishSignal.connect(current_task_finish_slot)
        self.workflowTaskStopSignal.connect(current_task_stop_slot)

        last_progress = {}

        def queue_current_task_progress(task: UpdateWorkFlow):
            progress = task.progress.get_progress()
            now = time.time()
            last_value, last_time = last_progress.get(task.key_word, (None, 0))
            if progress != last_value or now - last_time >= 0.2:
                last_progress[task.key_word] = (progress, now)
                self.workflowTaskProgressSignal.emit(task)

        self.work_flow.current_task_start_signal.connect(self.workflowTaskStartSignal.emit)
        self.work_flow.current_task_progress_signal.connect(queue_current_task_progress)
        self.work_flow.current_task_finish_signal.connect(self.workflowTaskFinishSignal.emit)
        self.work_flow.current_task_stop_signal.connect(self.workflowTaskStopSignal.emit)

    def _load_key_word(self):
        with KEY_WORD as df:
            if df.empty:
                return
            data = df.copy(deep=True)
        with self._lock:
            if not self._dataframe.empty:
                # 使用表合并，以关键词为关键列，data表为主
                data = pd.merge(
                    data,
                    self._dataframe[['关键词', '选择', '更新状态']],
                    on='关键词',
                    how='left'
                )
                # 对于合并后缺失的值，使用默认值填充
                if '选择' in data.columns:
                    data['选择'] = data['选择'].fillna(False).astype(bool)
                else:
                    data['选择'] = False

                if '更新状态' in data.columns:
                    data['更新状态'] = data['更新状态'].fillna('0;')
                else:
                    data['更新状态'] = '0;'
                # 确保"选择"列在第一列，"更新状态"列在最后列
                columns = ['选择'] + [col for col in data.columns if col not in ['选择', '更新状态']] + ['更新状态']
                data = data[columns]
            else:
                data.insert(0, '选择', False)
                data['更新状态'] = '0;'
        self.setDataFrame(data)

    def _data_change_lazy(self):
        self.__data_change_timer.start(TIMEOUT // 1000)

    def getKeyWordRowIndex(self, key_word) -> int:
        """获取关键词所在行索引"""
        with self._lock:
            return self._dataframe[self._dataframe['关键词'] == key_word].index[0]

    def getWorkFlowArgs(self, key_word) -> tuple[str, int, int]:
        """根据关键词获取后端工作流参数"""
        with self._lock:
            row_data = self._dataframe[self._dataframe['关键词'] == key_word].iloc[0]
            return row_data['关键词'], row_data['分级码'], row_data['类别码']

    def getAllKeyWord(self, select=False) -> list[str]:
        """
        返回按关键词忽略大小写排序后的列表
        :param select:是否只返回已选择的
        """
        with self._lock:
            if select:
                mask = self._dataframe['选择'] == True
                return self._dataframe[mask]['关键词'].sort_values(
                    key=lambda x: x.str.lower(), ignore_index=True).tolist()
            return self._dataframe['关键词'].sort_values(
                key=lambda x: x.str.lower(), ignore_index=True).tolist()


class LikeTableDelegate(DelegateBase):
    """表格控件代理"""

    def __init__(self, parent: 'LikeTable' = None):
        super().__init__(parent)
        self.__parent = parent
        self.__data_model = parent.data_model
        # self.setGeometry(self.GEOMETRY_CENTER, fixed_width=50, fixed_height=50)

    def createWidget(self, parent, row, col):
        if col == self.__parent.columnCount() - 1:
            widget = LikeTableProgressCell(parent)
        else:
            widget = CheckBox(parent)
            widget.stateChanged.connect(lambda checked, r=row, c=col:
                                        self.__data_model.setCellData(r, c, bool(checked)))
        return widget

    def setWidgetData(self, parent, widget, value):
        if isinstance(widget, LikeTableProgressCell):
            value, text = value.split(';')
            widget.setValue(int(value))
            widget.setText(text)
        elif isinstance(widget, CheckBox):
            widget.setChecked(value)


class LikeTable(TableWidgetBase):
    """表格数据展示"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # 必要参数
        self.data_model = LikeTableData(self)  # 数据模型
        self.column_delegate = LikeTableDelegate(self)  # 列代理
        # 设置表格参数
        self.setTableData(self.data_model)
        self.horizontalHeader().setVisible(True)
        self.setDelegateColumn(0, self.column_delegate)
        self.setDelegateColumn(self.columnCount() - 1, self.column_delegate)
        self.setFixedRowHeight(ROW_HEIGHT)
        # 信号连接
        self.mouseRightClickedSignal.connect(self.showRoundMenu)
        # 设置列宽模式
        self.setColumnSectionResizeMode(mode=QHeaderView.ResizeMode.ResizeToContents)
        self.setColumnSectionResizeMode(0, QHeaderView.ResizeMode.Fixed, 50)
        self.setColumnMinimumWidth(1)  # 设置第一列不小于当前可视内容最小宽度
        self.setColumnSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.setColumnSectionResizeMode(self.columnCount() - 1, QHeaderView.ResizeMode.Fixed, 100)

    def showRoundMenu(self, row, col, pos):
        menu = LikeRoundMenu(self.data_model.getRowData(row), pos, self)

    def scrollToTopSlot(self, key_word: str | int):
        if isinstance(key_word, int):
            row_index = key_word
        elif isinstance(key_word, str):
            row_index = self.data_model.getKeyWordRowIndex(key_word)
        else:
            row_index = -1
        index = self.model().index(row_index, 0)
        self.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtTop)

    def startSerialWorkFlow(self):
        """启动串行任务执行流"""
        data = self.data_model.getDataFrame()

        def sub_func():
            # 确保已选择任务在队列中
            for _, row_data in data.iterrows():
                if row_data.iloc[0]:
                    self.data_model.work_flow.add_task(row_data['关键词'], row_data['分级码'], row_data['类别码'])
                else:
                    self.data_model.work_flow.del_task(row_data['关键词'], row_data['分级码'], row_data['类别码'])
            if not self.data_model.work_flow.isRunning:
                self.data_model.work_flow.start(priority=4)

        Thread(target=sub_func, daemon=True).start()

    def stopSerialWorkFlow(self):
        """停止串行任务执行流"""
        self.data_model.work_flow.stop()

    def searchKeyWord(self, key_word) -> bool:
        with KEY_WORD as df:
            if key_word in df['关键词'].values:  # 精准搜索
                self.scrollToTopSlot(key_word)
                return True
            else:  # 模糊搜索
                key_word = key_word.lower()
                row_index = None
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
                    self.scrollToTopSlot(int(row_index))
                    return True
            return False

    def addKeyWord(self, key_word) -> api.KeyWordTask | None:
        """添加关键词"""

        def sub_func(task: api.KeyWordTask):
            if task.result() is not None:
                self.searchKeyWord(task.params.q)

        with KEY_WORD as df:
            if key_word in df['关键词'].tolist():
                return None
        params = api.get_search_params()
        params.q = key_word
        task = api.KeyWordTask(params, use_cache=False)
        task.finish_signal.connect(sub_func)
        task.start(priority=4)
        return task

    def delKeyWord(self, key_word=None) -> bool:
        if key_word is None:
            key_word = self.data_model.getAllKeyWord(True)
        else:
            key_word = [key_word]
        for key in key_word:
            KEY_WORD.del_data(key)
        return True


if __name__ == '__main__':
    from SubAPI import start_desktop


    def start():
        table_widget = LikeTable()
        table_widget.setFixedRowHeight(ROW_HEIGHT)

        table_widget.show()
        return table_widget


    start_desktop(start)
