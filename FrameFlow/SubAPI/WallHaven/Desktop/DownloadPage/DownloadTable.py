"""下载界面控制文件"""
from SubAPI.WallHaven.ImportPack import *
from SubAPI.WallHaven.api.WorkFlow import DownloadWorkFlow, DownloadWorkFlowManage

ROW_HEIGHT = 60
TIMEOUT = 50  # 定时器超时时间ms


class DownloadTableProgressCell(QWidget):
    """更新进度条"""

    def __init__(self, parent: 'DownloadTable' = None):
        super().__init__(parent)
        self.parent = parent
        self.progress = ProgressBar(self)
        self.progress.setTextVisible(True)
        self.label = CaptionLabel(self)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 15, 0, 15)
        self.layout.addWidget(self.progress)
        self.layout.addWidget(self.label)

    def setValue(self, value):
        self.progress.setValue(value)

    def setText(self, text):
        self.label.setText(text)


class DownloadButtonCell(QWidget):
    """下载按钮"""

    def __init__(self, row, col, parent: 'DownloadTable' = None):
        super().__init__(parent=parent)
        self.row = row
        self.col = col
        self.data_model = parent.data_model
        self.button = PrimaryToolButton(self)
        self.button.setFixedSize(30, 30)
        self.button.clicked.connect(self.button_slot)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.button, 0, Qt.AlignmentFlag.AlignCenter)

    def button_slot(self):
        button_state = int(self.data_model.data(self.row, self.col))
        image_id = self.data_model.data(self.row, 1)
        work_flow = DownloadWorkFlowManage.get_work_flow(image_id)
        if work_flow is not None:
            if button_state in [0, 2]:
                work_flow.start()
            else:
                work_flow.stop()

    def setIcon(self, icon):
        self.button.setIcon(icon)


class DownloadRoundMenu(RoundMenu):
    """右键菜单"""

    def __init__(self, row_data: pd.Series, pos: QPoint, parent: 'DownloadTable'):
        self.parent = parent
        super().__init__(parent=parent)
        self.row_data = row_data
        # 逐个添加动作，Action 继承自 QAction，接受 FluentIconBase 类型的图标
        self.addAction(Action(FIF.CHECKBOX, '全选', triggered=self.selectAll))
        self.addAction(Action(FIF.CHECKBOX, '取消全选', triggered=self.dissectAll))
        self.addAction(Action(FIF.COPY, '复制ID', triggered=self.copyImageID))
        self.addAction(Action(FIF.COPY, '复制图像URL', triggered=self.copyImageURL))
        self.addAction(Action(FIF.DELETE, '删除任务', triggered=self.deleteTask))
        # 显示菜单
        self.exec(pos)

    def selectAll(self):
        """全选"""
        row_count = self.parent.data_model.rowCount()
        for row in range(row_count):
            self.parent.data_model.setCellData(row, 0, True)
        return True, f'已选择{row_count}项任务', self.parent

    def dissectAll(self):
        """取消全选"""
        row_count = self.parent.data_model.rowCount()
        for row in range(row_count):
            self.parent.data_model.setCellData(row, 0, False)
        return True, f'已取消选择{row_count}项任务', self.parent

    def copyImageID(self):
        """复制图像ID"""
        copy_text_to_clipboard(self.row_data['图像ID'])

    def copyImageURL(self):
        """复制图像URL"""
        work_flow = DownloadWorkFlowManage.get_work_flow(self.row_data['图像ID'])
        copy_text_to_clipboard(work_flow.params.url)

    def deleteTask(self):
        """删除任务"""
        self.parent.deleteDownload(self.row_data['图像ID'])


class DownloadTableData(DataFrameModelBase):
    """表格数据模型,内部连接了DownloadWorkFlowManage信号"""
    finishedSignal = Signal(DownloadWorkFlow)  # 内部下载任务完成时的信号

    def __init__(self, parent: 'DownloadTable' = None):
        super().__init__(parent=parent)
        self.setColumnCount(4)
        self.__parent = parent
        self.table_data = DownloadWorkFlowManage
        self.__refresh_data_timer = debouncer_reuse_timer(self.refreshData)
        self.__refresh_data_timer.name = 'DownloadTableData_refresh_data_timer'
        DownloadWorkFlowManage.appendWorkFlowSignal.connect(self.refreshDataLazy)
        DownloadWorkFlowManage.removeWorkFlowSignal.connect(self.refreshDataLazy)
        # 首次加载
        self.__bind_signal = False  # 是否绑定信号
        self.refreshDataLazy()

    def refreshData(self):
        def start_slot(task: DownloadWorkFlow):
            """任务开始"""
            image_id = task.params.image_id
            row = self.getImageIDRowIndex(image_id)
            # 连接其余信号
            task.progress_signal.connect(progress_slot, enable_strict_repeat=True)
            task.finish_signal.bridge_signal(self.finishedSignal, enable_strict_repeat=True)
            task.stop_signal.connect(stop_slot, enable_strict_repeat=True)
            self.setCellData(row, 3, 1)  # 设置按钮状态为停止任务

        @throttle_reuse_timer_decorator(timeout=TIMEOUT // 50)
        def progress_slot(task: DownloadWorkFlow):
            """任务进度"""
            image_id = task.params.image_id
            value = task.progress
            row = self.getImageIDRowIndex(image_id)
            size_text = f'{value.finished / 1024 / 1024:0.2f}MB/{value.total / 1024 / 1024:0.2f}MB' if value.total / 1024 / 1024 > 1 else f'{value.finished / 1024:0.2f}KB/{value.total / 1024:0.2f}KB'
            rate_text = f'速度:{value.rate / 1024 / 1024:0.2f}MB/S' if value.rate / 1024 / 1024 > 1.2 else f'速度:{value.rate / 1024:0.2f}KB/S'
            value = (f'{value.get_progress()};'
                     f'下载中:{size_text} '
                     f'速率:{rate_text} 总进度:{value.get_progress()}%')
            self.setCellData(row, 2, value)  # 设置按钮状态为停止任务

        @info_bar_decorator
        def finished_slot(task: DownloadWorkFlow):
            """任务完成"""
            image_id = task.params.image_id
            row = self.getImageIDRowIndex(image_id)

            if task.result() is not None:
                if row > -1:
                    self.setCellData(row, 2, '100;下载完成')
                    self.setCellData(row, 3, 2)  # 设置按钮状态为重试任务
                SignalConfig.WallHavenSignal.search_signal.refreshViewSignal.emit()
                task.clear()  # 清理资源
                return True, f'{image_id}下载完成', self.__parent
            else:
                if row > -1:
                    self.setCellData(row, 2, '0;下载失败')
                    self.setCellData(row, 3, 2)  # 设置按钮状态为重试任务
                return False, f'{image_id}下载失败', self.__parent

        def stop_slot(task: DownloadWorkFlow):
            """任务停止"""
            image_id = task.params.image_id
            row = self.getImageIDRowIndex(image_id)
            self.setCellData(row, 2, '0;下载取消')
            self.setCellData(row, 3, 0)  # 设置按钮状态为开始任务

        if not self.__bind_signal:
            self.finishedSignal.connect(finished_slot)
            self.__bind_signal = True
        data = []
        # 处理任务信号
        for work_flow in DownloadWorkFlowManage.get_all_work_flow_by_sorted():
            # 连接任务信号
            work_flow.start_signal.connect(start_slot, enable_strict_repeat=True)
            if work_flow.state.isRunning:
                start_slot(work_flow)
            data.append(work_flow.params.image_id)
        # 更新数据
        data = pd.DataFrame(data, columns=['图像ID'])
        with self._lock:
            key = '图像ID'
            choose = '选择'
            progress = '下载进度'
            button_status = '操作'
            if not self._dataframe.empty:
                # 使用表合并，以id为关键列，data表为主
                data = pd.merge(
                    data,
                    self._dataframe[[key, choose, progress, button_status]],
                    on=key,
                    how='left'
                )
                # 对于合并后缺失的值，使用默认值填充
                if choose in data.columns:
                    data[choose] = data[choose].fillna(False).astype(bool)
                else:
                    data[choose] = False

                if progress in data.columns:
                    data[progress] = data[progress].fillna('0;')
                else:
                    data[progress] = '0;'

                # 确保"选择"列在第一列，进度和按钮状态列在最后列
                columns = [choose] + [col for col in data.columns if col not in
                                      [choose, progress, button_status]] + [progress, button_status]
                data = data[columns]
            else:
                data.insert(0, choose, False)
                data[progress] = '0;'  # 进度;文本描述
                data[button_status] = 0  # 0:开始任务 1:停止任务 2:重试
        self.setDataFrame(data)
        super().refreshData()

    def refreshDataLazy(self):
        self.__refresh_data_timer.start(TIMEOUT // 500)

    def getImageIDRowIndex(self, image_id: str) -> int:
        """获取图像ID所在行索引，找不到返回-1"""
        with self._lock:
            if self._dataframe.empty:
                return -1
            result = self._dataframe[self._dataframe['图像ID'] == image_id]
            if result.empty:
                return -1
            return result.index[0]

    def getAllImageID(self, select=False) -> list[str]:
        """
        返回图像ID列表
        :param select:是否只返回已选择的
        """
        with self._lock:
            if select:
                mask = self._dataframe['选择'] == True
                return self._dataframe[mask]['图像ID'].tolist()
            return self._dataframe['图像ID'].tolist()


class DownloadTableDelegate(DelegateBase):
    """表格委托"""

    def __init__(self, parent: 'DownloadTable'):
        super().__init__(parent=parent)
        self.__parent = parent
        self.__data_model = parent.data_model

    def createWidget(self, parent, row: int, col: int):
        if col == 0:
            widget = CheckBox(parent)
            widget.stateChanged.connect(
                lambda checked, r=row, c=col:
                self.__data_model.setCellData(r, c, bool(checked)))
            return widget
        elif col == 2:
            widget = DownloadTableProgressCell(parent)
            return widget
        elif col == 3:
            widget = DownloadButtonCell(row, col, parent)
            return widget

    def setWidgetData(self, parent, widget, value):
        if isinstance(widget, DownloadTableProgressCell):
            value, text = value.split(';')
            widget.setValue(int(value))
            widget.setText(text)
        elif isinstance(widget, CheckBox):
            widget.setChecked(value)
        elif isinstance(widget, DownloadButtonCell):
            if value == 0:  # 开始任务
                widget.setIcon(FIF.PLAY)
            elif value == 1:  # 停止任务
                widget.setIcon(FIF.CLOSE)
            elif value == 2:  # 重试任务
                widget.setIcon(FIF.ROTATE)


class DownloadTable(TableWidgetBase):
    """表格数据展示"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # 必要参数
        self.data_model = DownloadTableData(self)
        self.column_delegate = DownloadTableDelegate(self)
        # 设置表格参数
        self.setTableData(self.data_model)
        self.horizontalHeader().setVisible(True)
        self.setDelegateColumn(0, self.column_delegate)
        self.setDelegateColumn(2, self.column_delegate)
        self.setDelegateColumn(3, self.column_delegate)
        self.setFixedRowHeight(ROW_HEIGHT)
        # 设置列宽模式
        self.verticalHeader().setVisible(True)  # 显示左侧行头
        self.setColumnSectionResizeMode(mode=QHeaderView.ResizeToContents)
        self.setColumnSectionResizeMode(0, QHeaderView.ResizeMode.Fixed, 50)
        self.setColumnMinimumWidth(2, 100)
        self.setColumnSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # 下载进度
        self.setColumnSectionResizeMode(3, QHeaderView.ResizeMode.Fixed, ROW_HEIGHT)  # 操作按钮
        self.mouseRightClickedSignal.connect(self.showRoundMenu)

    def showRoundMenu(self, row, col, pos: QPoint):
        menu = DownloadRoundMenu(self.data_model.getRowData(row), pos, self)

    def startDownload(self):
        """外部调用开始任务"""
        for image_id in self.data_model.getAllImageID(True):
            work_flow = DownloadWorkFlowManage.get_work_flow(image_id)
            if work_flow is not None:
                work_flow.start()

    def stopDownload(self):
        """外部调用停止任务"""
        for image_id in self.data_model.getAllImageID(True):
            work_flow = DownloadWorkFlowManage.get_work_flow(image_id)
            if work_flow is not None:
                work_flow.stop()

    def deleteDownload(self, image_ids: list | str = None):
        """
        外部调用删除任务
        :param image_ids:删除指定image_id的任务,否则删除选择的任务
        """
        if image_ids is None:
            image_ids = self.data_model.getAllImageID()
        elif isinstance(image_ids, str):
            image_ids = [image_ids]
        for image_id in image_ids:
            DownloadWorkFlowManage.del_work_flow(image_id)
