from pyside6_GUI.sub_ui.home.ImportPack import *


class SearchPage(QWidget, Ui_SearchPage):
    searchFinishedSignal = Signal(pd.DataFrame)  # 搜索完成的信号
    thumbFinisedSignal = Signal(Task)

    def __init__(self, wallhaven_api: WallHavenAPI, parent=None):
        super().__init__(parent)
        self.__parent = parent
        self.all_cells: list[GroupBoxCell] = []  # 表格中全部的单元格
        self.setupUi(self)
        # 初始化后端库
        self.wallhaven_api = wallhaven_api
        self.uiInit()
        # 所有子控件继承样式
        self.setStyleSheet("""
                                    SearchPage, SearchPage * {
                                        background-color: transparent;
                                    }
                                """)
        self.bind()

    def uiInit(self):
        self.pushButton_select_all.setIcon(FIF.CHECKBOX)
        self.pushButton_download.setIcon(FIF.DOWNLOAD)
        self.load_dialog = LoadDialog(parent=self.__parent)
        self.load_dialog.close()  # 只能在主线程中触发
        purity = self.wallhaven_api.get_search_params.purity
        self.checkBox_sfw.setChecked(int(purity[0]))
        self.checkBox_sketchy.setChecked(int(purity[1]))
        self.checkBox_nsfw.setChecked(int(purity[2]))
        categories = self.wallhaven_api.get_search_params.categories
        self.checkBox_general.setChecked(int(categories[0]))
        self.checkBox_anime.setChecked(int(categories[1]))
        self.checkBox_people.setChecked(int(categories[2]))

    def bind(self):
        self.lineEdit.searchSignal.connect(self.search)
        self.lineEdit.returnPressed.connect(self.search)
        self.lineEdit.clearSignal.connect(self.clearCell)
        self.spinBox.valueChanged.connect(lambda value: self.search(page=value))
        self.searchFinishedSignal.connect(self.searchFinished)
        self.thumbFinisedSignal.connect(self.thumbFinised)
        self.tableWidget_image.visibleRowsSignal.connect(self.loadThumbs)

    def search(self, text: str = None, page=None):
        def callback(task: Task):
            result = task.result()
            if result is not None:
                self.searchFinishedSignal.emit(result)
            else:
                self.searchFinishedSignal.emit(pd.DataFrame())

        text = self.lineEdit.text() if text is None else text
        if not text:
            TeachingTip.create(
                target=self.lineEdit,
                icon=InfoBarIcon.WARNING,
                title='温馨提示',
                content='请输入关键词',
                isClosable=True,
                tailPosition=TeachingTipTailPosition.BOTTOM,
                duration=1000,
                parent=self.__parent)
            return
        params = self.wallhaven_api.get_search_params
        params.q = text
        params.page = 1 if page is None else page
        # 关闭当前的略缩图下载任务
        self.wallhaven_api.close_thumb_pool()
        for cell in self.all_cells:
            cell.image_loading = False
        # 获取和提交任务
        task = self.wallhaven_api.get_search_task(params)
        task.add_done_callback(callback)
        self.wallhaven_api.add_task(task)
        # 修改UI元素
        self.load_dialog.setText(f'正在搜索:{text}的第{params.page}页')
        self.spinBox.setValue(params.page)
        if self.load_dialog.exec() == 0:
            task.cancel()

    def searchFinished(self, value: pd.DataFrame):
        text = '搜索失败' if value.empty else '搜索成功'
        self.load_dialog.setText(text)
        if not self.all_cells:
            for _ in range(value.shape[0]):
                self.tableWidget_image.addWidget(self.createCell)
            self.tableWidget_image.calculateRowHeight()
        if not value.empty:
            self.load_dialog.close()
            for cell, (index, row) in zip(self.all_cells, value.iterrows()):
                cell: GroupBoxCell
                cell.setText(row['id'])
                cell.setColor(WallHavenConfig.COLOR_DICT[row['分级']])
                cell.clearImage()
                cell.image_path = {'thumb': row['略缩图_原'], 'image': row['远程路径']}
            self.spinBox.setMaximum(row['总页数'])
            self.label_page_info.setText(f"当前{row['当前页码']},共{row['总页数']}页,共{row['总数']}张")
            self.loadThumbs()
        else:
            self.label_page_info.setText('')
            QTimer.singleShot(1500, self.load_dialog.close)
        self.tableWidget_image.verticalScrollBar().setValue(0)
        # self.load_dialog.cancelButton.click()  # 触发取消按钮的信号,防止在子线程中无法操作UI

    def thumbFinised(self, value: Task):
        """略缩图加载完成时"""
        # 确保单元格存在且单元格当前图像ID与任务描述里存储的图像ID一致
        if len(value.args) != 2:
            return
        cell, image_id = value.args
        if cell in self.all_cells and cell.getText() == image_id:
            image_data: ImageData = value.result()
            cell.setImage(image_data.get_thumb())

    def showImageView(self, cell: GroupBoxCell):
        """显示图片详细页"""
        image_dialog = dialogWidget.ImageDialog(
            wallhaven_api=self.wallhaven_api,
            cell=cell,
            all_cell=self.all_cells,
            parent=self.__parent
        )
        image_dialog.tagClicked.connect(
            lambda text: (
                image_dialog.accept(),
                self.lineEdit.setText(text),
                self.search(text),
            ))
        image_dialog.exec()
        image_dialog.tags_task.cancel()
        image_dialog.download_task.cancel()
        image_dialog.deleteLater()

    def createCell(self) -> GroupBoxCell:
        cell = GroupBoxCell()
        button = PrimaryToolButton(FIF.VIEW)
        button.clicked.connect(lambda _, value=cell: self.showImageView(value))
        cell.addWidget(button)
        self.all_cells.append(cell)
        return cell

    def clearCell(self):
        """清除全部缓存"""
        self.wallhaven_api.close_thumb_pool()
        for cell in self.all_cells:
            self.tableWidget_image.delWidget(cell)
        self.tableWidget_image.realign()
        self.label_page_info.setText('')
        self.all_cells.clear()

    def clearThumb(self, isShow=True):
        """
        清除略缩图
        :param isShow:
        """

    def loadThumbs(self, rows: list = None):
        """加载当前可见行的略缩图"""

        def loacl_thumb(task: Task):
            image = Image_PIL(task.result())
            image.resize((300, 200))
            task.set_result(image.get_BytesIO)
            del image
            self.thumbFinisedSignal.emit(task)

        def callback(task: Task):
            if task.result() is None:
                task.args[0].image_loading = False
            if isinstance(task.result(), str):
                loacl_thumb(task)
            else:
                self.thumbFinisedSignal.emit(task)

        rows = self.tableWidget_image.getShowRowSignal() if rows is None else rows
        if self.all_cells:
            for row in rows:
                for index in range(row * 4, row * 4 + 4):
                    cell = self.all_cells[index]
                    if cell.getText() != "" and cell.image is None and not cell.image_loading:
                        cell.setImageText('加载图片中...')
                        task = self.wallhaven_api.get_download_task(cell.image_path['thumb'])
                        task.add_done_callback(callback)
                        task.args = (cell, cell.getText())
                        self.wallhaven_api.add_task(task)  # 内部需要用到desc确定提交到哪一个线程池中
                        cell.image_loading = True
