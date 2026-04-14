"""搜索界面控制文件"""
from SubWidget.ImportPack import *
from SubWidget.Home.SlotFunc.WorkFlow import SearchWorkFlow, ThumbWorkFlow


class Cell(GroupBoxCell):
    """单元格"""
    thumbStartSignal = Signal(WH.DownloadTask)  # 略缩图加载开始
    thumbFinishedSignal = Signal(WH.DownloadTask)  # 略缩图加载完成

    def __init__(self, key_word, search_info: pd.Series, parent, top_parent):
        """
        :param key_word: 所属关键词
        :param image_id: 图像id
        :param image_url: 图像地址
        :param thumb_url: 略缩图地址
        :param purity: 分级
        :param categories: 分类
        """
        super().__init__(parent)
        self.work_flow = None  # 任务流
        self.parent = parent
        self.top_parent = top_parent
        self.button = PrimaryToolButton(FIF.VIEW)
        self.button.clicked.connect(self.viewImage)
        self.button_copy = PrimaryToolButton(FIF.COPY)
        self.button_copy.clicked.connect(lambda _: File(self.image_local_path).copy_to_clipboard())
        self.button_copy.hide()
        self.button_open = PrimaryToolButton(FIF.FOLDER)
        self.button_open.clicked.connect(lambda _: FileBase(self.image_local_path).open_use_explorer())
        self.button_open.hide()
        self.button_open.setFixedSize(30, 30)
        self.button_copy.setFixedSize(30, 30)
        self.button.setFixedSize(30, 30)
        self.layout_title.setSpacing(5)
        self.addWidget(self.button_open)
        self.addWidget(self.button_copy)
        self.addWidget(self.button)
        self.thumbStartSignal.connect(self.thumbStart)
        self.thumbFinishedSignal.connect(self.thumbFinished)
        # 设置图像信息
        self.setImageInfo(key_word, search_info)

    def setImageInfo(self, key_word, search_info: pd.Series):
        """
        设置图像信息
        :param key_word: 所属关键词
        :param search_info:图像搜索数据
        """
        self.key_word = key_word
        self.image_url = search_info['远程路径']
        self.thumb_url = search_info['略缩图_原']
        self.categories = search_info['类别']
        self.image_local_path = os.path.join(
            os.path.realpath(WH.Config.SAVE_DIR), search_info['分级'], search_info['类别'],
            search_info['id'] + search_info['文件扩展名'])
        if FileBase(self.image_local_path).exists:
            self.button_copy.show()
            self.button_open.show()
        else:
            self.button_copy.hide()
            self.button_open.hide()
        self.setText(search_info['id'])
        self.setColor(search_info['分级'])
        self.setState(self.image_id in self.parent.selected_image_id)

    def setText(self, text):
        """设置标题"""
        super().setText(text)
        self.image_id = text if text else None

    def setColor(self, purity) -> bool:
        color = WH.Config.COLOR_DICT.get(purity, None)
        if color is not None:
            super().setColor(color)
            self.purity = purity
            return True
        return False

    def thumbStart(self, task: WH.DownloadTask):
        self.setImageText('加载图片中...')
        self.image_loading = True

    def thumbFinished(self, task: WH.DownloadTask):
        """略缩图加载完成时"""
        result = task.result()
        if result is not None and self in self.parent.all_cells and self.image_id == task.image_id:
            self.setImage(result.get_thumb())
        else:
            self.image_loading = False

    def loadThumb(self):
        if self.thumb_url:
            self.work_flow = ThumbWorkFlow(
                self.thumb_url, self.key_word, self.thumbStartSignal, self.thumbFinishedSignal)
            self.work_flow.start()

    def stopThumb(self):
        if self.work_flow is not None:
            self.work_flow.stop()

    def viewImage(self):
        def sub_func(key_word):
            image_dialog.accept()
            AppCore().getSignal('search').emit(key_word)

        from SubWidget.Home.SlotFunc.DialogWidget import ImageDialog
        image_dialog = ImageDialog(self, self.parent, self.top_parent)
        image_dialog.tagClicked.connect(sub_func)
        image_dialog.exec()
        image_dialog.work_flow.stop()


class Table(GroupBoxTable):
    """表格数据展示"""
    startSignal = Signal(WH.SearchTask)  # 搜索开始
    progressSignal = Signal(WH.SearchTask)  # 搜索进度
    finishedSignal = Signal(WH.SearchTask)  # 搜索完成

    def __init__(self, parent=None):
        super().__init__(parent)
        self.enableRowVisibleCheck(True)
        # 实例属性
        self.all_cells: list[Cell] = []  # 全部单元格
        self.selected_image_id: set[str] = set()  # 被选中的图像id
        self.work_flow = None  # 任务流
        self.page = None  # 当前搜索的页码
        self.page_max = None  # 当前最大页码
        # 信号连接
        self.startSignal.connect(self.__start)
        self.finishedSignal.connect(self.__finished)

    def setTopParent(self, top_parent):
        self.top_parent = top_parent

    def searchKeyWord(self, key_word, purity, categories, page, search_all=False, use_network=True, use_tags=False):
        """搜索关键词"""
        params = WH.get_search_params()
        params.q = key_word
        params.purity = purity
        params.categories = categories
        params.page = page
        self.page = page
        self.work_flow = SearchWorkFlow(
            params, self.startSignal, self.progressSignal, self.finishedSignal,
            search_all, use_network, use_tags=use_tags)
        self.work_flow.start()

    def __start(self, task: WH.SearchTask):
        self.resetCell()  # 清理当前单元格内容

    def __finished(self, task: WH.SearchTask):
        """数据获取完成后"""
        result = task.result()
        if result is not None:
            if task.search_all:
                self.selected_image_id.update(result['id'].tolist())
            result = result[result['当前页码'] == self.page].reset_index(drop=True)
            if len(self.all_cells) > result.shape[0]:
                for cell in self.all_cells[result.shape[0]:]:
                    self.all_cells.remove(cell)
                    self.delWidget(cell)
                if len(self.all_cells) % self.columnCount() == 0:
                    row = len(self.all_cells) // self.columnCount()
                else:
                    row = len(self.all_cells) // self.columnCount() + 1
                self.setRowCount(row)
            self.page_max = result.loc[0, '总页数']
            for index, row in result.iterrows():
                # 获取单元格
                if index < len(self.all_cells):
                    cell = self.all_cells[index]
                    cell.setImageInfo(task.params.q, row)
                else:
                    self.addWidget(lambda key_word=task.params.q, value=row: self.createCell(key_word, value))
            self.verticalScrollBar().setValue(0)
            self.calculateRowHeight()  # 修正布局
            self.getShowRowSignal()  # 触发略缩图更新

    def selectImageID(self, image_id: str | list):
        """选择图片"""
        if isinstance(image_id, str):
            image_id = [image_id]
        self.selected_image_id.update(image_id)

    def cancelImageID(self, image_id: str | list):
        """取消选择图片"""
        if image_id:
            if isinstance(image_id, str):
                image_id = [image_id]
            self.selected_image_id = self.selected_image_id - set(image_id)

    def selectClear(self):
        """清空选择"""
        for cell in self.all_cells:
            cell.setState(False)
        self.selected_image_id.clear()

    def createCell(self, key_word, value: pd.Series) -> Cell:
        """创建单元格"""
        cell = Cell(key_word, value, self, self.top_parent)
        cell.StateChange.connect(
            lambda state, value=cell: self.selectImageID(cell.image_id)
            if state else self.cancelImageID(cell.image_id))
        self.all_cells.append(cell)
        return cell

    def resetCell(self):
        """重置全部单元格"""
        for cell in self.all_cells:
            cell.stopThumb()
            cell.setText('')
            cell.image_loading = False
            cell.clearImage()

    def clearCell(self):
        """清除全部单元格"""
        for cell in self.all_cells:
            self.delWidget(cell)
        self.all_cells.clear()
        self.selected_image_id.clear()
        self.setRowCount(0)

    def getShowRowSignal(self, emit=True):
        rows = super().getShowRowSignal(emit)
        column = self.columnCount()
        if rows:
            for cell in self.all_cells[rows[0] * column:rows[-1] * column + column]:
                if not cell.image_loading:
                    cell.loadThumb()
