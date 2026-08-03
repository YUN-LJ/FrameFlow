"""关键词模式控制文件"""
from SubAPI.WallPaper import api
from SubAPI.WallPaper.ImportPack import *
from SubAPI.Settings.Desktop.ImageTabel import (
    ImageTableData, ImageTable, ImageTableCell
)

ThumbWorkFlow = WHAPI.WorkFlow.ThumbWorkFlow
MIN_COLUMN_WIDTH = 120  # 最小列宽
MAX_COLUMN_WIDTH = 150  # 最大列宽
TIMEOUT = 50


class KeyWordCell(ImageTableCell):
    """单元格"""
    all_thumb_url = {}  # 关键词:用于生成略缩图的本地原图路径

    def __init__(self, parent: 'KeyWordTable'):
        super().__init__(parent)
        self.parent = parent
        self.data_model = self.parent.data_model
        self.enableMouseFocus(False)  # 关闭鼠标焦点动画
        self.view_layout.setContentsMargins(0, 0, 0, 0)

        # 连接信号
        self.checkedChanged.connect(self.checkedChangedSlot)
        self.doubleClicked.connect(lambda: self.checkedChangedSlot(not self.checkBox.isChecked()))

        self.hideInfo()

    def checkedChangedSlot(self, checked: bool):
        row = self.data_model.getKeyWordRowIndex(self.key_word)
        self.data_model.setCellData(row, 0, checked)
        self.checked_state = checked

    def setKeyWordInfo(self, key_info: pd.Series):
        if not isinstance(key_info, pd.Series):
            return
        self.checked_state = key_info['选择']
        self.key_word = key_info['关键词']  # 关键词
        self.purity = key_info['分级码']
        self.categories = key_info['类别码']
        self._loadImageInfo(key_info)
        self.checkUI()

        # 加载略缩图
        if not self.isShowImage():
            try:
                self.startThumb()
            except RuntimeError:
                pass

    def checkUI(self):
        if hasattr(self, 'key_word') and hasattr(self, 'checked_state'):
            self.setText(self.key_word)
            self.setState(self.checked_state)

    def _filterThumbUrl(self, sample=True) -> str:
        """
        筛选略缩图加载地址
        :param sample:是否随机
        """
        # 随机一张竖屏照片作为略缩图,如果没有的话选取比例最接近1的
        filter_data = self.image_info[self.image_info['比例'] < 1]  # 筛选竖屏照片

        thumb_url = ''

        if filter_data.empty:
            all_image_url = self.image_info.sort_values('比例')
            if not all_image_url.empty:
                thumb_url = all_image_url.iloc[0]['本地路径']
        elif sample:
            thumb_url = filter_data.sample().iloc[0]['本地路径']
        else:
            thumb_url = filter_data.iloc[0]['本地路径']

        if thumb_url is not None:
            self.__class__.all_thumb_url[self.key_word] = thumb_url
        return thumb_url

    def _loadImageInfo(self, key_info: pd.Series):
        """加载信息"""
        self.image_info = api.get_image_info_by_key(self.key_word).sort_values('日期', ignore_index=True)
        thumb_url = self.__class__.all_thumb_url.get(self.key_word, None)
        if thumb_url is None:
            thumb_url = self._filterThumbUrl(False)  # 筛选某一张图片作为略缩图路径
            if thumb_url:
                self.setThumbUrl(thumb_url)
        else:
            self.setThumbUrl(thumb_url)
        image_info_total = self.image_info.shape[0]
        key_info_total = key_info[KEY_WORD.columns.total]
        self.setTitle(f'总计{image_info_total}/{key_info_total}')
        if image_info_total != key_info_total:
            self.setColor('red')
        else:
            self.setColor(MainWidget.CURRENT_THEME)


class KeyWordRoundMenu(RoundMenu):
    """右键菜单"""

    def __init__(self, row_index: int, pos: QPoint, parent: 'KeyWordTable'):
        super().__init__(parent=parent)
        self.parent = parent
        self.data_model = parent.data_model
        self.row_data = parent.data_model.getRowData(row_index)
        # 逐个添加动作，Action 继承自 QAction，接受 FluentIconBase 类型的图标
        self.addAction(Action(FIF.SEARCH, '搜索关键词', triggered=self.searchKeyWord))
        self.addAction(Action(FIF.CHECKBOX, '全选', triggered=self.selectAll))
        self.addAction(Action(FIF.CHECKBOX, '取消全选', triggered=self.dissectAll))
        self.addAction(Action(FIF.SYNC, '刷新略缩图', triggered=self.refreshThumb))
        self.addAction(Action(FIF.COPY, '复制关键词', triggered=self.copyKeyWord))
        # 显示菜单
        self.exec(pos)

    def searchKeyWord(self):
        params = WHAPI.get_search_params()
        params.q = self.row_data['关键词']
        params.purity = self.row_data['分级码']
        params.categories = self.row_data['类别码']
        task = WHAPI.SearchTask(
            params, use_network=WHAPI.Config.USE_NETWORK, add_history=True, enable_tags_search=WHAPI.Config.USE_TAGS)
        SignalConfig.WallHavenSignal.search_signal.searchSignal.emit(task)

    @info_bar_decorator
    def selectAll(self):
        """全选"""
        self.data_model.selectAll()
        return True, f"已选择{self.data_model.rowCount()}个关键词", GlobalValue.TOP_WINDOWS

    @info_bar_decorator
    def dissectAll(self):
        """取消全选"""
        self.data_model.disSelect()
        return True, f"已取消选择{self.data_model.rowCount()}个关键词", GlobalValue.TOP_WINDOWS

    def refreshThumb(self):
        pass

    def copyKeyWord(self):
        """复制图像关键词"""
        copy_text_to_clipboard(self.row_data['关键词'])


class KeyWordTableData(ImageTableData):
    """表格数据"""

    def __init__(self, parent: 'KeyWordTable'):
        super().__init__(parent=parent)
        self.wall_paper_api = api.WallPaperAPI()
        self._choose_change_timer = debouncer_reuse_timer(self._chooseChange)
        self._refresh_data_lazy = debouncer_reuse_timer(self.refreshData)
        self.dataChange.connect(self.chooseChangeLazy)
        self.dataRefresh.connect(self.chooseChangeLazy)
        self._load_choose_key = False  # 本地选择关键词是否已加载

        KEY_WORD.load_callback(self.refreshDataLazy)
        KEY_WORD.change_signal.connect(self.refreshDataLazy)
        IMAGE_INFO.load_callback(
            lambda: Task(self.__load_choose_keys, GlobalValue.GLOBAL_TASK_MANAGE).start())

    def __load_choose_keys(self):
        while not self.column_choose_name in self._dataframe.columns: time.sleep(1)
        self.chooseData(api.Config.IMAGE_CHOICE_KEY)
        self._load_choose_key = True

    def refreshData(self):
        with KEY_WORD as df:
            data = df.copy(deep=True)
        with self._lock:
            if not self._dataframe.empty:
                # 使用表合并，以关键词为关键列，data表为主
                data = pd.merge(data, self._dataframe[['关键词', '选择']], on='关键词', how='left')
                # 对于合并后缺失的值，使用默认值填充
                data['选择'] = data['选择'].fillna(False).astype(bool)
                # 确保"选择"列在第一列，"更新状态"列在最后列
                columns = ['选择'] + [col for col in data.columns if col != '选择']
                data = data[columns]
            else:
                data.insert(0, '选择', False)
        self.setDataFrame(data)

    def refreshDataLazy(self):
        self._refresh_data_lazy.start(TIMEOUT // 50)

    def _chooseChange(self):
        with self._lock:
            all_key_word = self._dataframe[['选择', '关键词']].copy(deep=True)
        select = all_key_word.loc[all_key_word['选择'] == True, '关键词'].tolist()
        diselect = all_key_word.loc[all_key_word['选择'] == False, '关键词'].tolist()
        if select:
            self.wall_paper_api.select_key(select)
        if diselect and self._load_choose_key:  # 确保本地选择关键词已加载
            self.wall_paper_api.deselect_key(diselect)

    def chooseChangeLazy(self):
        self._choose_change_timer.start(TIMEOUT // 50)

    def chooseData(self, key_word: str | list, choose: bool = True):
        with self.Lock:
            if self.column_choose_name in self._dataframe.columns:
                if isinstance(key_word, str):
                    key_word = [key_word]
                self._dataframe.loc[self._dataframe['关键词'].isin(key_word), '选择'] = choose
                self.dataRefresh.emit()
                return True

    def getKeyWordRowIndex(self, key_word) -> int:
        """获取关键词所在行索引"""
        with self._lock:
            return self._dataframe[self._dataframe['关键词'] == key_word].index[0]


class KeyWordDelegate(ListDelegateBase):
    def __init__(self, parent: 'KeyWordTable' = None):
        super().__init__(parent)

    def createWidget(self, parent, index: int):
        return KeyWordCell(parent)

    def setWidgetData(self, parent, widget, value):
        if isinstance(widget, KeyWordCell):
            if isinstance(value, pd.Series):
                widget.setKeyWordInfo(value)
            elif isinstance(value, bool):
                widget.checked_state = value
                widget.checkUI()


class KeyWordTable(ImageTable):

    def __init__(self, parent=None):
        super().__init__(parent, KeyWordRoundMenu)
        # 必要参数
        self.data_model = KeyWordTableData(self)  # 数据模型
        self.column_delegate = KeyWordDelegate(self)  # 列代理
        # 设置表格参数
        self.setBufferRows(1)  # 设置缓冲行
        self.setTableData(self.data_model)
        self.setDelegateColumn(self.column_delegate)
        self.verticalHeader().setVisible(False)
        self.enableColumnsCountToContents(True, MIN_COLUMN_WIDTH, MAX_COLUMN_WIDTH)
        self.mouseRightClickedSignal.connect(self.showRoundMenu)

    def _fuzzy_search(self, key_word: str) -> pd.DataFrame | None:
        with KEY_WORD as df:
            key_word = key_word.lower()
            # 先找以key_word开头的
            mask_start = df['关键词'].str.contains(f'^{re.escape(key_word)}', regex=True, case=False, na=False)
            if mask_start.any():
                return df[mask_start]
            else:
                # 如果没有开头匹配，找包含key_word的
                mask_contains = df['关键词'].str.contains(re.escape(key_word), regex=True, case=False, na=False)
                if mask_contains.any():
                    return df[mask_contains]
            return None

    def searchKey(self, key_word: str) -> bool:
        with KEY_WORD as df:
            if key_word in df['关键词'].values:  # 精准搜索
                row_index = df[df['关键词'] == key_word].index[0]
                self.scrollToTopSlot(row_index // self.columnCount())
                return True
        # 模糊搜索
        df = self._fuzzy_search(key_word)
        if df is not None:
            row_index = df.index[0]
            self.scrollToTopSlot(row_index // self.columnCount())
            return True
        return False

    def selectCell(self, key_word: str = None):
        """条件选择"""

        def sub_func(key_word):
            with KEY_WORD as data:
                df = data.copy(deep=True)
            if key_word is None:
                for key_word in df['关键词'].tolist():
                    self.selected_cell.append(key_word)
            else:
                # 模糊搜索
                df = self._fuzzy_search(key_word)
                if df is not None:
                    self.data_model.chooseData(df['关键词'])

        Thread(target=sub_func, args=(key_word,), daemon=True).start()

    def cancelSelectCell(self, key_word: str = None):
        """条件取消选择"""

        def sub_func(key_word):
            with KEY_WORD as data:
                df = data.copy(deep=True)
            if key_word is None:
                for key_word in df['关键词'].tolist():
                    self.selected_cell.remove(key_word)
            else:
                # 模糊搜索
                df = self._fuzzy_search(key_word)
                if df is not None:
                    self.data_model.chooseData(df['关键词'], False)

        Thread(target=sub_func, args=(key_word,), daemon=True).start()
