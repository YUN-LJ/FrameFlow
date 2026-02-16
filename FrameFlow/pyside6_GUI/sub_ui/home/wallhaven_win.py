"""wallhaven壁纸下载"""
# 导入后台线程
from pyside6_GUI.sub_ui.home.ThreadTask import *
# 导入左右布局
from pyside6_GUI.sub_ui.home.widgetUI.leftWidget import LeftWidget
from pyside6_GUI.sub_ui.home.widgetUI.rightWidget import RigetWidget
# 导入对话框
from pyside6_GUI.sub_ui.home.widgetUI.dialogWidget import LoadDialog, ImageDialog, SetDialog


class WallHavenWin(Ui_wallhaven, QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        if parent is None:
            parent = self
        self.__parent = parent
        self.setupUi(self)
        self.uiInit()  # 初始化界面
        self.threadInit()  # 初始化后台线程
        self.bind()  # 绑定槽函数
        self.search_key_word = None  # 当前的搜索关键词
        self.choice_image_id = None  # 用于切换页面时备份当前页面的选中图片
        self.url_list = None  # 当前页面的略缩图地址

    def uiInit(self):
        """界面初始化"""
        # 设置按钮图标
        self.pushButton_set.setIcon(FIF.SETTING)
        self.pushButton_keep.setIcon(FIF.DICTIONARY)
        self.pushButton_download_choice.setIcon(FIF.DOWNLOAD)
        # 实例化左右布局
        self.left_widget = LeftWidget(self.__parent)
        self.right_widget = RigetWidget(self.__parent)
        # 实例化进度对话框
        self.load_dialog: LoadDialog = None
        # 创建QSplitter对象，指定为水平方向（左右分栏）
        self.splitter = QSplitter(Qt.Horizontal)
        # 关闭实时更新
        # self.splitter.setOpaqueResize(False)
        # 将左右部件添加到splitter
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        # 设置初始比例,数字代表宽度像素
        self.splitter.setSizes([500, 0])
        # 设置分界线样式
        self.splitter.setStyleSheet(
            """QSplitter::handle { 
                            background-color: rgb(220,220,220); 
                            border: 1px solid rgb(220,220,220); 
                            margin: 1px;}""")
        # 将splitter添加到主布局
        self.horizontalLayout_5.addWidget(self.splitter)

    def threadInit(self):
        """后台线程初始化"""
        # 启动后台进程
        self.wallhaven_api = WallHavenAPI()
        self.wallhaven_api.start()
        # 后台线程
        self.thread_task = ThreadTask(self.wallhaven_api, self)
        self.thread_task.start.connect(self.taskStart)
        self.thread_task.done.connect(self.taskDone)
        self.thread_task.finished.connect(self.taskFinished)
        # 添加后台加载收藏夹资源
        self.thread_task.add_task(ThreadTask.LOADUI, ThreadTask.LOADUI, None)
        # 设置分级和类别
        self.setPurity(self.wallhaven_api.get_purity())
        self.setCategories(self.wallhaven_api.get_categories())

    def bind(self):
        """控件绑定"""

        def choiceAll():
            """全选按钮"""
            if self.search_key_word is not None:
                [image_id[1].setChecked(True) for image_id in self.left_widget.cell_items]
                self.search(self.search_key_word, None)
                self.pushButton_choice_all.setText('取消全选')
                self.pushButton_choice_all.clicked.disconnect()
                self.pushButton_choice_all.clicked.connect(choiceNone)
                TeachingTip.create(
                    target=self.pushButton_choice_all,
                    icon=InfoBarIcon.SUCCESS,
                    title='全选成功',
                    content=f'当前选择{len(self.left_widget.choice_image_id)}张',
                    isClosable=True,
                    tailPosition=TeachingTipTailPosition.BOTTOM,
                    duration=2000,
                    parent=self.__parent)
            else:
                TeachingTip.create(
                    target=self.pushButton_choice_all,
                    icon=InfoBarIcon.WARNING,
                    title='温馨提示',
                    content='请先搜索关键词',
                    isClosable=True,
                    tailPosition=TeachingTipTailPosition.BOTTOM,
                    duration=1000,
                    parent=self.__parent)

        def choiceNone():
            """取消全选"""
            self.left_widget.choice_image_id.clear()
            for item in self.left_widget.cell_items:
                if item[1].text() != '':
                    item[1].setChecked(False)
            self.pushButton_choice_all.setText('全选')
            self.pushButton_choice_all.clicked.disconnect()
            self.pushButton_choice_all.clicked.connect(choiceAll)
            TeachingTip.create(
                target=self.pushButton_choice_all,
                icon=InfoBarIcon.SUCCESS,
                title='已全取消',
                content=f'当前选择{len(self.left_widget.choice_image_id)}张',
                isClosable=True,
                tailPosition=TeachingTipTailPosition.BOTTOM,
                duration=2000,
                parent=self.__parent)

        def pageChanged(page):
            """当页面发送改变时"""
            if self.search_key_word:
                self.choice_image_id = self.left_widget.choice_image_id.copy()
                self.search(self.search_key_word, page)
                self.left_widget.choice_image_id = self.choice_image_id
                self.choice_image_id = None
            else:
                TeachingTip.create(
                    target=self.left_widget.spinBox,
                    icon=InfoBarIcon.WARNING,
                    title='温馨提示',
                    content='请输入关键词',
                    isClosable=True,
                    tailPosition=TeachingTipTailPosition.BOTTOM,
                    duration=1000,
                    parent=self.__parent)

        def download_clicked(value: tuple):
            """右侧表格按钮事件处理函数"""
            if value[1] == 0:  # 取消任务
                self.thread_task.cancel_task(value[0])
                self.right_widget.delDownload(value[0])
            elif value[1] == 1:  # 重试
                self.thread_task.add_task(value[0][0], ThreadTask.DOWNLOAD, (value[0][0], value[0][1]))
            elif value[1] == 2:  # 任务完成
                self.right_widget.delDownload(value[0])

        def pushButton_set():
            """设置"""
            set_dialog = SetDialog(self.wallhaven_api, self.__parent)
            if set_dialog.exec() == 1:
                print('成功')

        def pushButton_add_like():
            """添加收藏"""
            if self.search_key_word is not None:
                key_data = self.wallhaven_api.add_key_like(self.search_key_word).iloc[0]
                if self.right_widget.addLike(
                        key_data['关键词'],
                        key_data['总页数'],
                        key_data['总数'],
                        key_data['最新日期'],
                        key_data['上次更新']):
                    TeachingTip.create(
                        target=self.pushButton_add_like,
                        icon=InfoBarIcon.SUCCESS,
                        title='温馨提示',
                        content=f'已成功添加{self.search_key_word}',
                        isClosable=True,
                        tailPosition=TeachingTipTailPosition.BOTTOM,
                        duration=1000,
                        parent=self.__parent)
                else:
                    TeachingTip.create(
                        target=self.pushButton_add_like,
                        icon=InfoBarIcon.ERROR,
                        title='温馨提示',
                        content=f'关键词{self.search_key_word}已存在',
                        isClosable=True,
                        tailPosition=TeachingTipTailPosition.BOTTOM,
                        duration=1000,
                        parent=self.__parent)
            else:
                TeachingTip.create(
                    target=self.pushButton_add_like,
                    icon=InfoBarIcon.WARNING,
                    title='温馨提示',
                    content='请输入关键词',
                    isClosable=True,
                    tailPosition=TeachingTipTailPosition.BOTTOM,
                    duration=1000,
                    parent=self.__parent)

        def showThumbs(index):
            """显示略缩图,懒加载"""
            if self.url_list:
                start, end = index
                columnCount = self.left_widget.tableWidget_image.columnCount()
                start_index = start * columnCount
                end_index = (end + 1) * columnCount
                for url, item in zip(self.url_list[start_index:end_index],
                                     self.left_widget.cell_items[start_index:end_index]):
                    self.thread_task.add_task(
                        os.path.basename(url),
                        ThreadTask.THUMB, (url, item[2]))

        def del_like(key_word):
            ask = MessageBox("删除确认", f"是否删除{key_word}", self.__parent)
            if ask.exec():
                self.wallhaven_api.del_key_like(key_word)
                self.right_widget.delLike(key_word)

        self.lineEdit.searchSignal.connect(self.search)
        self.left_widget.spinBox.valueChanged.connect(pageChanged)
        self.left_widget.pushButton_previous_page.clicked.connect(
            lambda: self.left_widget.spinBox.setValue(self.left_widget.spinBox.value() - 1))
        self.left_widget.pushButton_next_page.clicked.connect(
            lambda: self.left_widget.spinBox.setValue(self.left_widget.spinBox.value() + 1))
        # 绑定类别
        for obj in self.widget_categories.findChildren(QCheckBox):
            obj.stateChanged.connect(lambda _: self.setCategories())
        for obj in self.widget_purity.findChildren(QCheckBox):
            obj.stateChanged.connect(lambda _: self.setPurity())
        # 绑定按钮
        self.pushButton_set.clicked.connect(pushButton_set)
        self.pushButton_add_like.clicked.connect(pushButton_add_like)
        self.pushButton_download_choice.clicked.connect(
            lambda: (self.right_widget.stackedWidget.setCurrentIndex(0),
                     self.downloadImage(self.left_widget.choice_image_id, self.search_key_word),
                     self.splitter.setSizes([100, 500]))
        )
        self.pushButton_keep.clicked.connect(
            lambda: (self.right_widget.stackedWidget.setCurrentIndex(1),
                     self.splitter.setSizes([100, 500]))
        )
        self.pushButton_choice_all.clicked.connect(choiceAll)
        # 绑定表格内信号
        self.left_widget.download_clicked.connect(lambda image_id: self.downloadImage(image_id, self.search_key_word))
        self.left_widget.view_cliced.connect(lambda image_id: self.viewImage(image_id))
        self.left_widget.visible_row.connect(showThumbs)
        self.right_widget.download_clicked.connect(download_clicked)
        self.right_widget.update_clicked.connect(
            lambda key_list: [self.thread_task.add_task(key, ThreadTask.UPDATEKEY, key) for key in key_list]
        )
        self.right_widget.like_button_clicked.connect(del_like)

    def taskStart(self, args):
        """任务开始时"""
        task_name, task_enum = args
        if task_enum == ThreadTask.UPDATEKEY:
            self.right_widget.displayLikeStart(task_name)
        elif task_enum == ThreadTask.DOWNLOAD:
            self.right_widget.displayStart(task_name)

    def taskDone(self, args):
        """任务进行"""
        task_name, task_enum, task_args = args
        if task_enum == ThreadTask.SEARCH:
            self.searchFinished(task_name, task_args)
        elif task_enum == ThreadTask.THUMB:
            task_args[1].set_image(task_args[0])
            # QTimer.singleShot(
            #     random.randrange(10, 100, 10),
            #     lambda image_widget=task_args[1], image=task_args[0]: image_widget.set_image(image)
            # )
        elif task_enum == ThreadTask.DOWNLOAD:
            self.right_widget.displayDownloading(task_args)
        elif task_enum == ThreadTask.VIEW:
            task_args[1].display(task_args[0])
        elif task_enum == ThreadTask.LOADUI:
            self.right_widget.addLike(*task_args)
        elif task_enum == ThreadTask.UPDATEKEY:
            if len(task_args) == 3:  # 更新进度
                self.right_widget.displayLikeUpdating(*task_args)
            elif len(task_args) == 4:  # 添加下载
                last_page, total, date, image_ids = task_args
                self.right_widget.displayLikeUpdating(
                    task_name, last_page, total, date, get.now_time('%Y-%m-%d %H:%M:%S')
                )
                self.wallhaven_api.add_key_like(task_name)
                if image_ids:
                    self.downloadImage(image_ids, task_name)

    def taskFinished(self, args):
        """任务完成"""
        task_name, task_enum, task_state = args
        if task_enum == ThreadTask.SEARCH:
            self.searchFinished(task_name, task_state)
        elif task_enum == ThreadTask.THUMB:
            if not task_state:
                self.left_widget.label_state.setText(f'当前状态:{task_name}略缩图加载失败')
        elif task_enum == ThreadTask.DOWNLOAD:
            if task_state[0]:
                self.right_widget.displayFinished(task_name)
            else:
                self.right_widget.displayError(task_name, task_state[1])
        elif task_enum == ThreadTask.VIEW:
            task_state[1].finished(task_state[0])
        elif task_enum == ThreadTask.LOADUI:
            self.left_widget.label_state.setText('当前状态:后台UI资源加载完毕')
        elif task_enum == ThreadTask.UPDATEKEY:
            if task_state[0]:
                self.right_widget.displayLikeFinished(task_name, task_state[1])
                if task_state[1] == 2:  # 任务完成后确保处于收藏页面
                    self.right_widget.stackedWidget.setCurrentIndex(1)
            else:
                self.right_widget.displayLikeError(task_name)

    def search(self, key_word: str, page: int = 1):
        """
        搜索函数
        :param key_word:搜索关键词
        :param page:指定搜索页码,为None时搜索全部页码
        """
        # self.left_widget.spinBox.blockSignals(True)  # 关闭信号
        # self.left_widget.spinBox.setValue(page)
        # self.left_widget.spinBox.blockSignals(False)  # 开启信号
        # 删除当前略缩图加载任务
        self.thread_task.cancel_task(ThreadTask.THUMB)
        if page is not None:
            # 重新初始化图像显示
            self.left_widget.defaultCell()
        purity = self.wallhaven_api.get_purity
        categories = self.wallhaven_api.get_categories
        name = f'{key_word}.{page}.{purity}.{categories}'
        self.thread_task.add_task(
            name, ThreadTask.SEARCH,
            (key_word, page))
        # 显示加载对话框
        if self.load_dialog is None:
            text = f'正在搜索:{key_word}的第{page}页' if page is not None else f'正在搜索:{key_word}'
            self.load_dialog = LoadDialog(text, parent=self.__parent)
            if self.load_dialog.exec() == 1:
                self.search_key_word = key_word
                self.load_dialog = None
                self.splitter.setSizes([500, 0])
            else:
                self.thread_task.cancel_task(name)
                self.load_dialog = None

    def searchFinished(self, task_name: str, data: pd.DataFrame | tuple):
        """搜索完成后"""
        if isinstance(data, pd.DataFrame) and not data.empty:
            page = task_name.split('.')[1]
            if page != 'None':
                # 数据提取
                image_ids = data['id'].tolist()
                self.url_list = data['略缩图_原'].tolist()  # 用于后续的略缩图加载
                last_page = data.iloc[0]['总页数']
                total = data.iloc[0]['总数']
                self.left_widget.label_total.setText(f"共{last_page}页,总计:{total}张")
                # 更改标签ID
                for item, image_id in zip(self.left_widget.cell_items, image_ids):
                    item[1].setText(image_id)
                    # 先设置图像ID,才能判断图像是否被选中
                    if image_id in self.left_widget.choice_image_id:
                        item[1].setChecked(True)
                # 触发表格的检测可见行信号,会自动触发加载略缩图
                self.left_widget.checkShowRowSignal()
                # 设置最大页码数
                self.left_widget.spinBox.setMaximum(last_page)
            else:
                self.left_widget.choice_image_id.update(data['id'])
        else:
            state, page = data
            text = f'当前状态:搜索成功 第{page}页' if state else f'当前状态:搜索失败 第{page}页'
            self.left_widget.label_state.setText(text)
            if self.load_dialog is not None:
                self.load_dialog.accept()

    def viewImage(self, image_id: str):
        """显示照片"""

        def tag_clicked(key_word: str):
            nonlocal image_dialog
            image_dialog.accept()
            self.search(key_word, 1)
            self.lineEdit.setText(key_word)

        image_dialog = ImageDialog(self.__parent)
        image_dialog.tag_clicked.connect(tag_clicked)
        self.thread_task.add_task(
            f'{image_id}_view', ThreadTask.VIEW,
            (image_id, self.search_key_word, image_dialog))
        image_dialog.exec()  # 进入事件循环
        self.thread_task.cancel_task(image_id)

    def downloadImage(self, image_ids: str | list, key_word: str):
        """下载图片"""

        def add_one(image_id):
            if self.right_widget.addDownload(image_id):
                self.thread_task.add_task(image_id, ThreadTask.DOWNLOAD, (image_id, key_word))
            else:
                TeachingTip.create(
                    target=self.pushButton_download_choice,
                    icon=InfoBarIcon.WARNING,
                    title='温馨提示',
                    content=f'{image_id}已在下载列表中',
                    isClosable=True,
                    tailPosition=TeachingTipTailPosition.BOTTOM,
                    duration=1000,
                    parent=self.__parent)

        if isinstance(image_ids, str):
            image_ids = [image_ids]
        for image_id in image_ids:
            QTimer.singleShot(
                random.randrange(10, 500, 50),
                lambda value=image_id: add_one(value))

    def setCategories(self, categories: str = None):
        """设置类别"""
        obj_categories = self.widget_categories.findChildren(QCheckBox)
        if categories is None:
            categories = []
            for obj in obj_categories:
                categories.append(str(int(obj.isChecked())))
                obj.setEnabled(True)
            categories = ''.join(categories)
            if categories.count('1') == 1:
                obj_categories[categories.find('1')].setEnabled(False)
        else:
            for i, obj in zip(categories, obj_categories):
                obj.setChecked(bool(int(i)))
        self.wallhaven_api.set_categories(categories)

    def setPurity(self, purity: str = None):
        """设置分级"""
        obj_purity = self.widget_purity.findChildren(QCheckBox)
        if purity is None:
            purity = []
            for obj in obj_purity:
                purity.append(str(int(obj.isChecked())))
                obj.setEnabled(True)
            purity = ''.join(purity)
            if purity.count('1') == 1:
                obj_purity[purity.find('1')].setEnabled(False)
        else:
            for i, obj in zip(purity, obj_purity):
                obj.setChecked(bool(int(i)))
        self.wallhaven_api.set_purity(purity)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.hide()  # 先隐藏前台窗口,等待线程安全结束
        # 关闭后端
        self.wallhaven_api.stop()
        # 关闭后台线程
        self.thread_task.stop()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    w = WallHavenWin()
    w.show()
    app.exec()


if __name__ == '__main__':
    main()
