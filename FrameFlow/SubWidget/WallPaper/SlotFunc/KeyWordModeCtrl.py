"""关键词模式控制文件"""
from SubWidget.WallPaper.ImportPack import *
from SubWidget.Home.SlotFunc.WorkFlow import ThumbWorkFlow
from SubWidget.WallPaper.SlotFunc.WorkFlow import WaitInfoLoadWorkFlow
from typing import Optional


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
        if checked:
            if self not in self.parent.selected_cells:
                self.parent.selected_cells.append(self)
                WPAPI().select_key(self.key_word, self.image_info)
        else:
            if self in self.parent.selected_cells:
                self.parent.selected_cells.remove(self)
                WPAPI().deselect_key(self.key_word)

    def setKeyWord(self, key_info: pd.Series):
        self.key_info = key_info
        self.key_word = key_info['关键词']
        self.setText(self.key_word)
        if self.key_word in WP.Config.IMAGE_CHOICE_KEY:
            self.checkBox.setChecked(True)

    def thumbStart(self, task: WH.DownloadTask):
        self.setImageText('加载图片中...')
        self.image_loading = True

    def thumbFinished(self, task: WH.DownloadTask):
        """略缩图加载完成时"""
        result = task.result()
        if result is not None and self in self.parent.all_cells:
            self.setImage(result.get_thumb())
        else:
            self.image_loading = False

    def filterThumbUrl(self):
        if self.image_info is not None:
            # 随机一张竖屏照片作为略缩图,如果没有的话选取比例最接近1的
            filter_data = self.image_info[self.image_info['比例'] < 1]
            if filter_data.empty:
                self.thumb_url = self.image_info.sort_values('比例')['本地路径'].values[0]
            else:
                self.thumb_url = filter_data.sample()['本地路径'].values[0]

    def loadThumb(self):
        if self.thumb_url:
            self.work_flow = ThumbWorkFlow(
                self.thumb_url, self.key_word, self.thumbStartSignal, self.thumbFinishedSignal)
            self.work_flow.start()

    def loadImageInfo(self):
        self.image_info = WP.get_image_info_by_key(self.key_word).sort_values('日期', ignore_index=True)
        self.filterThumbUrl()  # 筛选某一种图片作为略缩图路径
        self.setTitle(f'总计{self.image_info.shape[0]}/{self.key_info[KeyWord.columns.total]}')
        if self.image_info.shape[0] != self.key_info[KeyWord.columns.total]:
            self.setColor('red')
        else:
            self.setColor('white')

    def resetLoadThumb(self):
        """重新加载略缩图"""
        self.filterThumbUrl()
        self.loadThumb()

    def loadCellInfo(self) -> bool:
        if ImageInfo.is_loaded():
            self.loadImageInfo()
            self.loadThumb()
            return True
        return False


class KeyTable(GroupBoxTable):
    __timer_start_signal = Signal()  # 定时器启动信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.enableRowVisibleCheck(True)
        self.setColumnCount(3)
        self.mouseRightClickedSignal.connect(self.showRoundMenu)
        # 实例属性
        self.all_cells: list[Cell] = []  # 全部单元格
        self.selected_cells: list[Cell] = []  # 被选中的单元格
        self.key_word_queue = Queue()  # 待提交的任务
        self.__timer_isRunning = False
        self.__timer_start_signal.connect(lambda: QTimer.singleShot(0, self.__submit_task))
        self.work_flow = WaitInfoLoadWorkFlow(self)
        self.work_flow.finished.connect(self.addKeyWord)
        self.work_flow.start()

    def showRoundMenu(self, row, col, pos: QPoint):
        cell: Cell = self.cellWidget(row, col)
        menu = RoundMenu(parent=self)
        # 逐个添加动作，Action 继承自 QAction，接受 FluentIconBase 类型的图标
        menu.addAction(Action(FIF.UPDATE, '重新略缩图', triggered=cell.resetLoadThumb))
        # 显示菜单
        menu.exec(pos)

    def addKeyWord(self, key_data: pd.DataFrame):
        """添加收藏夹数据"""
        for index, row_data in key_data.iterrows():
            self.key_word_queue.put(row_data)
        if not self.__timer_isRunning:
            self.__timer_start_signal.emit()

    def createCell(self, key_info: pd.Series) -> Cell:
        cell = Cell(key_info, self)
        self.all_cells.append(cell)
        return cell

    def searchKey(self, key_wrod):
        pass

    def __submit_task(self):
        try:
            self.__timer_isRunning = True
            key_info: pd.Series = self.key_word_queue.get(timeout=1)
            self.addWidget(lambda value=key_info: self.createCell(value))
            self.calculateRowHeight()  # 修正布局
            self.getShowRowSignal()  # 触发略缩图更新
            interval = 10 if self.isVisible() else 100
            QTimer.singleShot(interval, self.__submit_task)
        except Empty:
            self.__timer_isRunning = False

    def getShowRowSignal(self, emit=True):
        rows = super().getShowRowSignal(emit)
        column = self.columnCount()
        for cell in self.all_cells[rows[0] * column:rows[-1] * column + column]:
            if not cell.image_loading:
                cell.loadCellInfo()
