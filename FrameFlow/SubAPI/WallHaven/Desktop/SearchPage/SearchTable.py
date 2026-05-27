"""表格控制文件"""
from SubAPI.WallHaven.ImportPack import *
from SubAPI.WallHaven import api
from SubAPI.WallHaven.api.Tools import SearchTask
from SubAPI.WallHaven.api.WorkFlow import DownloadWorkFlow, ThumbWorkFlow
from SubAPI.Settings.Desktop.ImageTabel import ImageTableData, ImageTable

PAGE_SIZE = 24  # 每一页数量,如果服务器返回数量不改动的话
MIN_COLUMN_WIDTH = 200  # 最小列宽
MAX_COLUMN_WIDTH = 300  # 最大列宽
TIMEOUT = 200  # 定时器超时时间ms


class SearchCell(ImageCell):
    """图像单元格"""
    thumbStartSignal = Signal(ThumbWorkFlow)  # 略缩图加载开始
    thumbFinishedSignal = Signal(ThumbWorkFlow)  # 略缩图加载完成

    def __init__(self, parent: 'SearchTable'):
        super().__init__(parent)
        self.work_flow: ThumbWorkFlow = None  # 任务流
        self.parent = parent
        self.data_model = self.parent.data_model
        self.__uiInit()
        self.__bind()

    def __uiInit(self):
        self.button = PrimaryToolButton(FIF.VIEW)
        self.button.clicked.connect(self.viewImage)

        self.button_copy = PrimaryToolButton(FIF.COPY)
        self.button_copy.clicked.connect(lambda _: FileBase(self.image_local_path).copy_to_clipboard())
        self.button_copy.hide()

        self.button_open = PrimaryToolButton(FIF.FOLDER)
        self.button_open.clicked.connect(lambda _: FileBase(self.image_local_path).open_use_explorer())
        self.button_open.hide()

        self.button_open.setFixedSize(30, 30)
        self.button_copy.setFixedSize(30, 30)
        self.button.setFixedSize(30, 30)
        # 添加控件
        self.layout_title.setSpacing(5)
        self.layout_title.addWidget(self.button_open)
        self.layout_title.addWidget(self.button_copy)
        self.layout_title.addWidget(self.button)
        self.thumbStartSignal.connect(self.thumbStart)
        self.thumbFinishedSignal.connect(self.thumbFinished)

    def __bind(self):
        def check_box_state_changed(state: bool):
            row = self.data_model.getRowIndexByImageID(self.image_id)
            self.data_model.setCellData(row, 0, bool(state))

        self.check_box.stateChanged.connect(check_box_state_changed)
        self.__load_thumb_timer = debouncer_timer(self._loadThumb)

    def setImageInfo(self, search_info: pd.Series):
        """
        设置图像信息
        :param search_info:图像搜索数据
        """
        if not isinstance(search_info, pd.Series):
            return
        self.search_info = search_info
        self.checked_state = search_info['选择']
        self.key_word = search_info['关键词']
        self.image_url = search_info['远程路径']
        self.thumb_url = search_info['略缩图_原']
        self.categories = search_info['类别']
        self.setText(search_info['id'])
        self.setColor(search_info['分级'])
        self.checkUI()
        # 加载略缩图
        if not self.__load_thumb_timer.isActive() and not self.image_widget.isShowImage():
            self.loadThumb()

    def checkUI(self):
        """检查UI是否需要变化"""
        self.setState(self.checked_state)
        self.image_local_path = api.ImageData(self.image_id, self.search_info['文件扩展名']).image_path
        if self.image_local_path:
            self.button_copy.show()
            self.button_open.show()
        else:
            self.button_copy.hide()
            self.button_open.hide()

    def setText(self, text):
        """设置标题"""
        super().setText(text)
        self.image_id = text if text else None

    def setColor(self, purity) -> bool:
        color = api.Config.COLOR_DICT.get(purity, None)
        if color is not None:
            super().setColor(color)
            self.purity = purity
            return True
        return False

    def thumbStart(self, _):
        self.setImageText('加载图片中...')

    def thumbFinished(self, task: ThumbWorkFlow):
        """略缩图加载完成时"""
        if isinstance(task, ThumbWorkFlow):
            result = task.result()
            try:
                if result is not None and self.image_id == task.image_id:
                    self.setImage(result.generate_thumb())
            except Exception as e:
                task.start(priority=2)
                print(f"{self.__class__.__name__} 略缩图加载错误: {e}")
                self.setImageText('加载图片失败')
        else:
            self.setImageText('停止加载图片')

    def _loadThumb(self):
        if self.thumb_url:
            self.work_flow = ThumbWorkFlow(self.thumb_url)
            self.work_flow.start_signal.bridge_signal(self.thumbStartSignal)
            self.work_flow.finish_signal.bridge_signal(self.thumbFinishedSignal)
            self.work_flow.stop_signal.bridge_signal(self.thumbFinishedSignal)
            self.work_flow.start(priority=2)

    def loadThumb(self):
        self.__load_thumb_timer.start(TIMEOUT)

    def stopThumb(self):
        if self.__load_thumb_timer.isActive():
            self.__load_thumb_timer.stop()
        if self.work_flow is not None:
            self.work_flow.stop()
            self.work_flow.clear()

    def viewImage(self):
        def sub_func(key_word):
            image_dialog.accept()
            params = api.get_search_params()
            params.q = key_word
            task = SearchTask(params, use_network=api.Config.USE_NETWORK,
                              enable_tags_search=True, add_history=True)
            SignalConfig.WallHavenSignal.search_signal.searchSignal.emit(task)

        from SubAPI.WallHaven.Desktop.SearchPage.DialogWidget import ImageDialog
        image_dialog = ImageDialog(self.search_info, self.data_model.getDataFrame())
        image_dialog.tagClicked.connect(sub_func)
        image_dialog.exec()
        image_dialog.deleteLater()

    def deleteLater(self):
        """确保资源删除干净"""
        # 由于表格会在刷新视图时删除掉不可见区域单元格
        self.stopThumb()
        super().deleteLater()


class SearchRoundMenu(RoundMenu):
    """右键菜单"""

    def __init__(self, row_index: int, pos: QPoint, parent: 'SearchTable'):
        super().__init__(parent=parent)
        self.parent = parent
        self.data_model = parent.data_model
        self.row_data = parent.data_model.getRowData(row_index)
        # 逐个添加动作，Action 继承自 QAction，接受 FluentIconBase 类型的图标
        self.addAction(Action(FIF.CHECKBOX, '全选', triggered=self.selectAll))
        self.addAction(Action(FIF.CHECKBOX, '取消全选', triggered=self.dissectAll))
        self.addAction(Action(FIF.SYNC, '刷新略缩图', triggered=print))
        self.addAction(Action(FIF.COPY, '复制ID', triggered=self.copyImageID))
        self.addAction(Action(FIF.COPY, '复制图像URL', triggered=self.copyImageURL))
        self.addAction(Action(FIF.COPY, '复制图像地址', triggered=self.copyImagePath))
        self.addAction(Action(FIF.DOWNLOAD, '下载选择项', triggered=self.downloadSelect))
        self.addAction(Action(FIF.DELETE, '删除选择项', triggered=self.deleteSelect))
        # 显示菜单
        self.exec(pos)

    def selectAll(self):
        """全选"""

        def finished(task: SearchTask):
            result: pd.DataFrame = task.result()
            if result is not None:
                result['选择'] = True
                self.data_model.refreshData(task)

        params = api.get_search_params()
        params.q = self.row_data['关键词']
        task = SearchTask(params, use_network=api.Config.USE_NETWORK,
                          enable_tags_search=api.Config.USE_TAGS, search_all=True)
        task.finish_signal.connect(finished)
        SignalConfig.WallHavenSignal.search_signal.searchSignal.emit(task)

    def dissectAll(self):
        """取消全选"""
        self.data_model.disSelect()

    def copyImageID(self):
        """复制图像ID"""
        copy_text_to_clipboard(self.row_data['id'])

    def copyImageURL(self):
        """复制图像URL"""
        copy_text_to_clipboard(self.row_data['远程路径'])

    @info_bar_decorator
    def copyImagePath(self):
        """复制图像路径"""
        image = api.ImageData(self.row_data['id'], self.row_data['文件扩展名'])
        if image.image_path:
            image_path = image.image_path
            copy_text_to_clipboard(image_path)
            return True, f'已复制图像{self.row_data['id']}到剪切板', self.parent
        else:
            return False, f'未下载图像{self.row_data['id']}', self.parent

    @info_bar_decorator
    def downloadSelect(self):
        """下载选择项"""
        df = self.data_model.getDataFrame()
        select = df[df['选择'] == True]
        content = f'这{len(select)}项'
        if select.empty:
            select = [self.data_model.getRowDataByImageID(self.row_data['id'])]
            content = f'图片{self.row_data['id']}'
        message_box = MessageBox('下载选择项', f'确定下载{content}吗？', GlobalValue.TOP_WINDOWS)
        if message_box.exec():
            for idx, search_info in select.iterrows():
                params = DownloadWorkFlow.Params(
                    search_info['id'], search_info['关键词'], url=search_info['远程路径'])
                DownloadWorkFlow(params)
            SignalConfig.WallHavenSignal.download_signal.refreshViewSignal.emit()
            self.data_model.clearSelect()
            return True, f'已添加{content}任务', self.parent
        else:
            return False, '已取消下载', self.parent

    @info_bar_decorator
    def deleteSelect(self):
        """删除选择项"""
        df = self.data_model.getDataFrame()
        df = df.loc[df['选择'] == True]
        select = df['选择'].tolist()
        content = f'删除这{len(select)}项'
        if not select:
            select = [self.row_data['id']]
            content = f'删除图片{self.row_data['id']}'
        message_box = MessageBox('删除选择项', f'确定{content}吗？', GlobalValue.TOP_WINDOWS)
        if message_box.exec():
            with IMAGE_INFO as df:
                image_info = df[df['id'].isin(select)].copy(deep=True)
            for _, row in image_info.iterrows():
                api.ImageData(row['id'], row['文件扩展名']).del_image()
            self.data_model.clearSelect()
            return True, f'已{content}', self.parent
        else:
            return False, '已取消删除', self.parent


class SearchTableData(ImageTableData):
    """表格数据"""

    def __init__(self, parent: 'SearchTable'):
        super().__init__(parent=parent)
        self.current_params = None
        SignalConfig.WallHavenSignal.search_signal.finishedSignal.connect(self.refreshData)

    def rowCount(self) -> int:
        if self._dataframe.empty:
            return 0
        try:
            total = self._dataframe.loc[0, '总数']
            # 确保返回合理的整数值
            if pd.isna(total) or total < 0:
                return 0
            return int(total)
        except (KeyError, IndexError, ValueError):
            return 0

    def refreshData(self, task: SearchTask):
        if task.result() is None:
            return None
        data = task.result()
        if '选择' not in data.columns:
            data.insert(0, '选择', False)
        if self.current_params == task.params:
            with self._lock:
                # 合并旧数据选择数据
                data = pd.concat([self._dataframe, data]).drop_duplicates(
                    subset=['id'], keep='last').sort_values('日期', ascending=False)
            data.reset_index(drop=True, inplace=True)
        self.current_params = task.params
        self.setDataFrame(data)

    def data(self, index: int) -> str | None:
        if index >= self.rowCount():
            return None
        # 转为页内相对索引
        page = index // PAGE_SIZE + 1
        virtual_index = index % PAGE_SIZE
        with self._lock:
            data = self._dataframe[self._dataframe['当前页码'] == page].copy(deep=True)
        data.reset_index(drop=True, inplace=True)
        try:
            value = data.iloc[virtual_index]
            return value
        except IndexError:
            self.dataIndexError.emit(index, 1)
            return None

    def getRowDataByImageID(self, image_id: str) -> pd.Series | None:
        with self._lock:
            data = self._dataframe[self._dataframe['id'] == image_id]
            if data.empty:
                return None
            return data.iloc[0]

    def getRowIndexByImageID(self, image_id: str) -> int:
        with self._lock:
            data = self._dataframe[self._dataframe['id'] == image_id]
            if data.empty:
                return -1
            return data.index[0]

    def getAllPage(self) -> list[int]:
        with self._lock:
            return self._dataframe['当前页码'].unique().tolist()

    def clearSelect(self):
        """清空选择"""
        with self._lock:
            self._dataframe['选择'] = False
        self.dataRefresh.emit()

    def selectAll(self):
        """全选"""
        with self._lock:
            self._dataframe['选择'] = True
        self.dataRefresh.emit()

    def disSelect(self):
        """取消全选"""
        with self._lock:
            self._dataframe['选择'] = False
        self.dataRefresh.emit()


class SearchTableDelegate(ListDelegateBase):
    """表格代理"""

    def __init__(self, parent: 'SearchTable'):
        super().__init__(parent)

    def createWidget(self, parent, index: int):
        return SearchCell(parent)

    def setWidgetData(self, parent, widget, value):
        if isinstance(widget, SearchCell):
            widget.setImageInfo(value)


class SearchTable(ImageTable):
    """表格数据展示"""
    currentPageSignal = Signal(int)  # 发送当前处于哪一页
    loadNextPageSignal = Signal(int)  # 发送加载页面请求

    def __init__(self, parent=None):
        super().__init__(parent, SearchRoundMenu)
        # 必要参数
        self.data_model = SearchTableData(self)  # 数据模型
        self.column_delegate = SearchTableDelegate(self)  # 列代理
        # 设置表格参数
        self.setBufferRows(0)  # 设置缓冲行
        self.setTableData(self.data_model)
        self.setDelegateColumn(self.column_delegate)
        self.verticalHeader().setVisible(False)
        self.enableColumnsCountToContents(True, MIN_COLUMN_WIDTH, MAX_COLUMN_WIDTH)
        self.current_params = None
        self.__next_page = 1
        self._search_finished = False
        # 信号连接
        self.signal = SignalConfig.WallHavenSignal.search_signal
        self.signal.startSignal.connect(self.__start_signal)
        self.signal.finishedSignal.connect(self.__finished_signal)
        self.__load_next_page_timer = debouncer_timer(self.loadNextPageSlot)
        self.data_model.dataIndexError.connect(self.loadNextPageSlotLazy)

    def loadNextPageSlot(self):
        """数据索引错误槽"""
        self.loadNextPageSignal.emit(self.__next_page)

    def loadNextPageSlotLazy(self, index, _):
        """数据索引错误槽"""
        page = index // PAGE_SIZE + 1
        if page != self.__next_page:
            self._search_finished = False
            self.__next_page = page
            self.__load_next_page_timer.start(TIMEOUT)

    def __start_signal(self, task: SearchTask):
        self._search_finished = False
        if self.current_params != task.params:
            self.clearContents()
            self.current_params = task.params
            self.verticalScrollBar().setValue(0)

    def __finished_signal(self, task: SearchTask):
        if task.result() is None:
            return
        self._search_finished = True

    def searchKeyWord(self, task: SearchTask):
        """
        搜索关键词
        :param task:搜索任务
        """
        # 桥接信号
        task.start_signal.bridge_signal(self.signal.startSignal)
        task.progress_signal.bridge_signal(self.signal.progressSignal)
        task.finish_signal.bridge_signal(self.signal.finishedSignal)
        task.stop_signal.bridge_signal(self.signal.stopSignal)
        task.start(priority=2)  # 开始任务

    def _loadVisible(self):
        if not self._search_finished:
            return None
        super()._loadVisible()
        visible_rows = self.getVisibleRow()
        if visible_rows:
            current_page = min(visible_rows) * self.columnCount() // 24 + 1
            self.currentPageSignal.emit(current_page)

    def clearContents(self):
        """清理资源"""
        self.data_model.clearData()
        self.column_delegate.deleteWidgetAll()
        super().clearContents()
