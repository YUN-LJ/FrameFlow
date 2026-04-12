"""下载界面控制文件"""
from SubWidget.ImportPack import *
from SubWidget.Home.SlotFunc.WorkFlow import DownloadWorkFlow

ROW_HEIGHT = 60


class Row(QObject):
    """一行数据"""
    startSignal = Signal(WH.ImageInfoTask)
    progressSignal = Signal(TaskProgress)  # 进度条更新信号
    finishedSignal = Signal(bool)

    def __init__(self, key_word, url, parent: 'Table' = None):
        super().__init__(parent)
        self.parent = parent
        self.key_word = key_word
        self.url = url
        self.startSignal.connect(self.__start)
        self.progressSignal.connect(self.__progress)
        self.finishedSignal.connect(self.__finished)
        self.work_flow = DownloadWorkFlow(key_word, url, self.startSignal, self.progressSignal, self.finishedSignal)
        self.uiInit()
        self.row_data = [self.check_box, self.widget, self.button]

    def uiInit(self):
        self.check_box = CheckBox(self.work_flow.image_data.image_id)  # 图像ID

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

    def __button_slot(self):
        """操作按钮槽函数"""
        if self.button._icon == FIF.PLAY or self.button._icon == FIF.ROTATE:
            self.work_flow.start()
        elif self.button._icon == FIF.DELETE:
            self.work_flow.stop()
            self.parent.delRow(self)

    def __start(self, task: WH.ImageInfoTask):
        self.progress.setValue(0)
        self.label.setText('连接资源中')
        self.button.setIcon(FIF.DELETE)

    def __progress(self, value: TaskProgress):
        self.progress.setValue(value.get_progress())
        size_text = f'{value.finished / 1024 / 1024:0.2f}MB/{value.total / 1024 / 1024:0.2f}MB' if value.total / 1024 / 1024 > 1 else f'{value.finished / 1024:0.2f}KB/{value.total / 1024:0.2f}KB'
        rate_text = f'速度:{value.rate / 1024:0.2f}MB/S' if value.rate / 1024 > 1.2 else f'速度:{value.rate:0.2f}KB/S'
        self.label.setText(f'{size_text} {rate_text}')

    def __finished(self, value: bool):
        """任务完成"""
        icon = InfoBarIcon.ERROR
        title = self.work_flow.image_data.image_id
        content = '下载失败'
        if value:
            self.progress.setValue(100)
            self.label.setText('下载成功')
            self.button.setEnabled(False)
            QTimer.singleShot(2000, lambda: self.parent.delRow(self))
            icon = InfoBarIcon.SUCCESS
            content = '下载成功'
        else:
            self.label.setText('下载失败')
            self.button.setIcon(FIF.ROTATE)
        if self.parent.isVisible():
            InfoBar.new(
                icon=icon, title=title, content=content, orient=Qt.Horizontal,
                isClosable=True, position=InfoBarPosition.TOP,
                duration=1000, parent=self.parent)


class TableData(QThread):
    """表格数据层"""
    finished = Signal()  # 完成信号

    def __init__(self, parent: 'Table'):
        super().__init__(parent)
        self.all_work_flow = {}

    def getWorkFlow(self, key_word: str):
        if key_word in self.all_work_flow:
            return self.all_work_flow[key_word]

    def createWorkFlow(self, key_word, purity, categories):
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


class Table(GroupBoxTable):
    """表格数据展示"""
    __timer_start_signal = Signal()  # 定时器启动信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnHeader(['图像ID', '下载进度', '操作'])
        self.enable_adaptive_row_height = False
        self.verticalScrollBar().setSingleStep(int(ROW_HEIGHT / 3))
        # 设置列宽模式
        self.verticalHeader().setVisible(True)  # 显示左侧行头
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # 下载进度

        self.image_url_queue = Queue()  # 待提交的任务
        self.all_row: dict[str, Row] = {}  # 全部行{url,Row}
        self.selected_row: list[Row] = []  # 被选中的任务
        self.__app_core = AppCore()  # 全局信号控制器
        self.__timer_isRunning = False
        self.__timer_start_signal.connect(lambda: QTimer.singleShot(0, self.__submit_task))

    def selectAllRows(self, value=True):
        for row in self.all_row.copy().values():
            row.check_box.setChecked(value)

    def startDownload(self):
        for row in self.selected_row.copy():
            if not row.work_flow.isRunning:
                row.work_flow.start()
            row.check_box.setChecked(False)

    def delDownload(self):
        for row in self.selected_row:
            row.work_flow.stop()
            self.delRow(row)
        self.selected_row.clear()

    def addImageUrl(self, image_url: tuple | list):
        """
        添加图像下载
        :param image_url:[(key,url)]
        """
        if isinstance(image_url, tuple):
            image_url = [image_url]
        for args in image_url:
            self.image_url_queue.put(args)
        if not self.__timer_isRunning:
            self.__timer_start_signal.emit()

    def __submit_task(self):
        try:
            self.__timer_isRunning = True
            key, url = self.image_url_queue.get(timeout=1)
            if url not in self.all_row:
                self.addRow(key, url)
            QTimer.singleShot(50, self.__submit_task)
        except Empty:
            self.__timer_isRunning = False

    def addRow(self, key_word, url):
        """新增一行数据"""
        if url not in self.all_row:
            row = Row(key_word, url, self)
            row.check_box.stateChanged.connect(
                lambda state, value=row:
                self.selected_row.append(value) if state else
                self.selected_row.remove(value)
            )
            super().addRow(row.row_data, height=ROW_HEIGHT)
            # 防止自动布局显示不全
            row.check_box.setMinimumWidth(len(row.work_flow.image_data.image_id) * 15)
            self.all_row[url] = row

    def delRow(self, row):
        if row is not None:
            self.all_row.pop(row.url)
            super().delRow(row.check_box, 0)
