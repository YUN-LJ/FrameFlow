"""关键词模式控制文件"""
from ImportFile import Config
from qfluentwidgets import qconfig, Theme
from SubWidget.ImportPack import *
from SubWidget.Home.SlotFunc.WorkFlow import ThumbWorkFlow
from SubWidget.WallPaper.SlotFunc.WorkFlow import WaitInfoLoadWorkFlow
from typing import Optional

THEME = Config.DARK if Config.CURRENT_THEME == 'Light' else Config.LIGHT


class Cell(GroupBoxCell):
    """单元格"""
    thumbStartSignal = Signal(WH.DownloadTask)  # 略缩图加载开始
    thumbFinishedSignal = Signal(WH.DownloadTask)  # 略缩图加载完成

    def __init__(self, key_info: pd.Series, parent: Optional['KeyTable']):
        super().__init__(parent)
        self.key_info = key_info  # 关键词信息
        self.parent = parent
        self.key_word = None  # 关键词
        self.image_info: pd.DataFrame = None  # 所属该关键词的全部图像数据
        self.thumb_url = None  # 所属该关键词的某一种照片
        # 信号连接
        self.thumbStartSignal.connect(self.thumbStart)
        self.thumbFinishedSignal.connect(self.thumbFinished)
        self.checkBox.stateChanged.connect(self.checkBoxSlot)
        # 设置数据
        self.setKeyWord(key_info)

    def checkBoxSlot(self, checked):
        if self.key_word is not None:
            if checked:
                self.parent.selected_cells.append(self.key_word, emit=False)
            else:
                self.parent.selected_cells.remove(self.key_word, emit=False)

    def setKeyWord(self, key_info: pd.Series):
        self.key_info = key_info
        self.key_word = key_info['关键词']
        self.setText(self.key_word)
        if self.key_word in self.parent.selected_cells:
            self.checkBox.setChecked(True)

    def thumbStart(self, task: WH.DownloadTask):
        self.setImageText('加载图片中...')
        self.image_loading = True

    def thumbFinished(self, task: WH.DownloadTask):
        """略缩图加载完成时"""
        result = task.result()
        if result is not None and self in self.parent.all_cells.values():
            self.setImage(result.get_thumb())
        else:
            self.image_loading = False

    def filterThumbUrl(self):
        if self.image_info is not None:
            # 随机一张竖屏照片作为略缩图,如果没有的话选取比例最接近1的
            filter_data = self.image_info[self.image_info['比例'] < 1]
            if filter_data.empty:
                thumb_url = self.image_info.sort_values('比例')['本地路径']
                if not thumb_url.empty:
                    self.thumb_url = thumb_url.values[0]
            else:
                self.thumb_url = filter_data.sample()['本地路径'].values[0]

    def loadThumb(self):
        """加载略缩图"""
        if self.thumb_url:
            self.work_flow = ThumbWorkFlow(
                self.thumb_url, self.key_word, self.thumbStartSignal, self.thumbFinishedSignal)
            self.work_flow.start()

    def loadImageInfo(self):
        """加载信息"""
        self.image_info = WP.get_image_info_by_key(self.key_word).sort_values('日期', ignore_index=True)
        self.filterThumbUrl()  # 筛选某一种图片作为略缩图路径
        self.setTitle(f'总计{self.image_info.shape[0]}/{self.key_info[KeyWord.columns.total]}')
        if self.image_info.shape[0] != self.key_info[KeyWord.columns.total]:
            self.setColor('red')
        else:
            self.setColor(THEME)

    def resetLoadThumb(self):
        """重新加载略缩图"""
        self.filterThumbUrl()
        self.loadThumb()

    def loadCellInfo(self) -> bool:
        """加载略缩图和信息"""
        if ImageInfo.is_loaded():
            self.loadImageInfo()
            self.loadThumb()
            return True
        return False


class SelectCell(QObject):
    """关键词选择管理类"""
    keyAppendSignal = Signal(str)  # 关键词选中信号
    keyRemoveSignal = Signal(str)  # 关键词取消信号

    def __init__(self, selected: list = None):
        super().__init__()
        self._items = []  # 内部存储

        if selected:
            for key_word in selected:
                self.append(key_word, emit=False)

    def append(self, key_word: str, emit: bool = True):
        """添加关键词"""
        if key_word not in self._items:
            self._items.append(key_word)
            WPAPI().select_key(key_word)
            if emit:
                self.keyAppendSignal.emit(key_word)

    def remove(self, key_word: str, emit: bool = True):
        """移除关键词"""
        if key_word in self._items:
            self._items.remove(key_word)
            WPAPI().deselect_key(key_word)
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


class KeyTable(TableCell):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.verticalHeader().setVisible(True)  # 隐藏垂直表头即左侧表头
        self.setColumnCount(3)
        self.mouseRightClickedSignal.connect(self.showRoundMenu)
        qconfig.themeChanged.connect(self.themeChange)
        # 实例属性
        self.all_cells: dict[str, Cell] = {}  # 全部单元格
        self.selected_cells = SelectCell(WP.Config.IMAGE_CHOICE_KEY)  # 被选中的单元格
        self.selected_cells.keyAppendSignal.connect(lambda key_word: self.__selectedCellsSlot(key_word, True))
        self.selected_cells.keyRemoveSignal.connect(lambda key_word: self.__selectedCellsSlot(key_word, False))
        self.work_flow = WaitInfoLoadWorkFlow(self)
        self.work_flow.finished.connect(self.loadVisible)
        self.work_flow.start()

    def __selectedCellsSlot(self, key_word: str, checked: bool):
        row = self.all_rows.get(key_word, None)
        if row is not None:
            row.checkBox.setChecked(checked)

    def themeChange(self, theme: Theme):
        global THEME
        THEME = Config.DARK if theme.value == 'Light' else Config.LIGHT
        rows = super().visibleRow(False)
        column = self.columnCount()
        if rows:
            for cell in list(self.all_cells.values())[rows[0] * column:rows[-1] * column + column]:
                cell.setColor(THEME)

    def loadVisible(self, rows: list = None):
        """加载当前可见区域单元格"""
        if not KeyWord.is_loaded():
            return
        with KeyWord.lock:
            data_len = KeyWord.data().shape[0]
        self.setRowCount(data_len)
        rows = self.visibleRow(False) if rows is None else rows
        column = self.columnCount()
        for row in rows:
            for col in range(column):
                index = row * column + col
                current_cell: Cell = self.cellWidget(row, col)
                if index < data_len:
                    with KeyWord.lock:
                        cell_data = KeyWord.data().iloc[index].copy(deep=True)
                    if current_cell is None or current_cell.key_word != cell_data['关键词']:
                        cell = Cell(cell_data, self)
                        cell.loadCellInfo()
                        self.all_cells[cell.key_word] = cell
                        self.setCellWidget(row, col, cell)
                        self.resizeRowsToContents()
                else:
                    if current_cell is not None:
                        self.setCellWidget(row, col, QWidget())

    def showEvent(self, event):
        super().showEvent(event)
        self.loadVisible()

    def showRoundMenu(self, row, col, pos: QPoint):
        cell: Cell = self.cellWidget(row, col)
        menu = RoundMenu(parent=self)
        # 逐个添加动作，Action 继承自 QAction，接受 FluentIconBase 类型的图标
        menu.addAction(Action(
            FIF.SEARCH, '搜索关键词', triggered=lambda: AppCore().getSignal('search').emit(cell.key_word)))
        menu.addAction(Action(FIF.UPDATE, '重新略缩图', triggered=cell.resetLoadThumb))
        # 显示菜单
        menu.exec(pos)

    def searchKey(self, key_word: str) -> bool:
        with KeyWord.lock:
            if key_word in KeyWord.data()['关键词'].values:  # 精准搜索
                row_index = KeyWord.data()[KeyWord.data()['关键词'] == key_word].index[0]
                index = self.model().index(self.getLenToRow(row_index), 0)
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
                    index = self.model().index(self.getLenToRow(row_index), 0)
                    self.scrollTo(index, QAbstractItemView.PositionAtTop)
                    return True
            return False

    def selectCell(self, key_word: str = None):
        def sub_func(key_word):
            with KeyWord.lock:
                df = KeyWord.data().copy(deep=True)
            if key_word is None:
                for key_word in df['关键词'].tolist():
                    self.selected_cells.append(key_word)
            else:
                key_word = key_word.lower()
                # 先找以key_word开头的
                mask_start = df['关键词'].str.contains(f'^{re.escape(key_word)}', regex=True, case=False, na=False)
                for index, row_data in df[mask_start].iterrows():
                    self.selected_cells.append(row_data['关键词'])

        Thread(target=sub_func, args=(key_word,), daemon=True).start()

    def cancelSelectCell(self, key_word: str = None):
        def sub_func(key_word):
            with KeyWord.lock:
                df = KeyWord.data().copy(deep=True)
            if key_word is None:
                for key_word in df['关键词'].tolist():
                    self.selected_cells.remove(key_word)
            else:
                key_word = key_word.lower()
                # 先找以key_word开头的
                mask_start = df['关键词'].str.contains(f'^{re.escape(key_word)}', regex=True, case=False, na=False)
                for index, row_data in df[mask_start].iterrows():
                    self.selected_cells.remove(row_data['关键词'])

        Thread(target=sub_func, args=(key_word,), daemon=True).start()
