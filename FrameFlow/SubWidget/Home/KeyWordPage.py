"""收藏夹子窗口"""
from SubWidget.ImportPack import *
from SubWidget.Home.DesignFile.KeyWordPage import Ui_KeyWordWidget
from SubWidget.Home.SlotFunc.WorkFlow import SerialWorkFlow


class KeyWordPage(QWidget, Ui_KeyWordWidget):
    downloadSignal = Signal(list)  # 更新关键词触发下载[(关键词,url)]
    addKeyWordSignal = Signal(WH.KeyWordTask)  # 添加新的关键词信号
    startUpdateSignal = Signal(SerialWorkFlow)  # 更新任务开始
    progressSignal = Signal(TaskProgress)  # 更新进度
    finishUpdateSignal = Signal(bool)  # 更新任务结束/停止

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__parent = parent
        self.slot = KeyWordSlot(self, self.__parent)
        self.setupUi(self)
        # 所有子控件继承样式
        self.setStyleSheet("""
                            KeyWordPage, KeyWordPage * {
                                background-color: transparent;
                            }
                            """)
        self.uiInit()
        self.bind()

    def uiInit(self):
        self.pushButton_add.setIcon(FIF.ADD)
        self.pushButton_select_all.setIcon(FIF.CHECKBOX)
        self.pushButton_update.setIcon(FIF.UPDATE)
        self.pushButton_delete.setIcon(FIF.DELETE)
        self.progressBar.hide()
        self.progress_label.hide()

    def bind(self):
        self.startUpdateSignal.connect(self.__startUpdate)
        self.progressSignal.connect(self.__progressUpdate)
        self.finishUpdateSignal.connect(self.__finishUpdate)
        self.tableWidget.work_flow.start_signal.connect(self.startUpdateSignal.emit)
        self.tableWidget.work_flow.progress_signal.connect(self.progressSignal.emit)
        self.tableWidget.work_flow.finish_signal.connect(self.finishUpdateSignal.emit)
        self.tableWidget.work_flow.stop_signal.connect(self.finishUpdateSignal.emit)
        self.tableWidget.submit_download_task.connect(self.downloadSignal.emit)
        self.pushButton_update.clicked.connect(self.slot.pushButton_update)
        self.pushButton_select_all.clicked.connect(self.slot.pushButton_select_all)
        self.pushButton_add.clicked.connect(self.slot.pushButton_add)
        self.pushButton_delete.clicked.connect(self.slot.pushButton_delete)
        self.lineEdit.searchSignal.connect(self.slot.lineEdit)
        self.lineEdit.returnPressed.connect(self.slot.lineEdit)
        self.addKeyWordSignal.connect(self.slot.addKeyWordSignal)

    def __startUpdate(self):
        self.progressBar.show()
        self.progress_label.show()
        self.pushButton_update.setText('取消更新')

    def __progressUpdate(self, value: TaskProgress):
        self.progress_label.setText(f'更新中:{value.finished}/{value.total}')
        self.progressBar.setValue(value.get_progress())

    def __finishUpdate(self):
        self.progressBar.hide()
        self.progress_label.hide()
        self.pushButton_update.setText('更新')


class KeyWordSlot:
    def __init__(self, parent: KeyWordPage, top_parent):
        self.parent = parent
        self.top_parent = top_parent

    def lineEdit(self, key_word=None):
        key_word = self.parent.lineEdit.text() if key_word is None else key_word
        icon = InfoBarIcon.ERROR
        title = '失败'
        content = f'{key_word} 不存在'
        if self.parent.tableWidget.searchKey(key_word):
            icon = InfoBarIcon.SUCCESS
            title = '成功'
            content = f'已将{key_word}定位到首行'
        if self.parent.isVisible():
            TeachingTip.create(
                target=self.parent.lineEdit, icon=icon, title=title, content=content,
                isClosable=True, duration=2000, parent=self.top_parent,
                tailPosition=TeachingTipTailPosition.BOTTOM)

    def pushButton_update(self):
        if self.parent.tableWidget.selected_rows:
            state = True if self.parent.pushButton_update.text() == '更新' else False
            self.parent.tableWidget.updateKeyWord(state)
        else:
            TeachingTip.create(
                target=self.parent.pushButton_update, icon=InfoBarIcon.ERROR,
                title='错误', content='请勾选需要更新的关键词',
                isClosable=True, duration=1500, parent=self.top_parent,
                tailPosition=TeachingTipTailPosition.BOTTOM)

    def pushButton_select_all(self):
        if self.parent.pushButton_select_all.text() == '全选':
            self.parent.pushButton_select_all.setText('取消全选')
            self.parent.tableWidget.selectAllRows(True)
        else:
            self.parent.pushButton_select_all.setText('全选')
            self.parent.tableWidget.selectAllRows(False)

    def pushButton_add(self):
        key_word = self.parent.lineEdit.text()
        if key_word:
            self.parent.pushButton_add.setEnabled(False)
            params = WH.get_search_params()
            params.q = key_word
            task = WHAPI.key_word_task(params, use_cache=False)
            task.finish_signal.connect(self.parent.addKeyWordSignal.emit)
            task.start()
        else:
            TeachingTip.create(
                target=self.parent.pushButton_add, icon=InfoBarIcon.ERROR, title='错误', content='请输入内容',
                isClosable=True, duration=2000, parent=self.top_parent,
                tailPosition=TeachingTipTailPosition.BOTTOM)

    def pushButton_delete(self):
        icon = InfoBarIcon.ERROR
        title = '删除失败'
        content = '未选择任何关键词'
        if self.parent.tableWidget.selected_rows:
            load_dialog = MessageBox(
                '确认删除',
                f'已选择{len(self.parent.tableWidget.selected_rows)}个',
                parent=self.top_parent)
            if load_dialog.exec():
                self.parent.tableWidget.delKeyWord()
                icon = InfoBarIcon.SUCCESS
                title = '删除成功'
                content = '已删除'
            else:
                content = '已取消'
        InfoBar.new(
            icon=icon, title=title, content=content, orient=Qt.Horizontal,
            isClosable=True, position=InfoBarPosition.TOP,
            duration=1000, parent=self.top_parent)

    def addKeyWordSignal(self, task: WH.KeyWordTask):
        icon = InfoBarIcon.ERROR
        title = '添加失败'
        content = f'{task.params.q} 搜索不到数据或已存在'
        result = task.result()
        self.parent.pushButton_add.setEnabled(True)
        if result is not None and task.params.q not in self.parent.tableWidget.all_rows:
            icon = InfoBarIcon.SUCCESS
            title = '添加成功'
            content = f'{task.params.q} 已添加,并定位到改行'
            self.parent.tableWidget.addKeyWord(result)
        InfoBar.new(
            icon=icon, title=title, content=content, orient=Qt.Horizontal,
            isClosable=True, position=InfoBarPosition.TOP,
            duration=2000, parent=self.top_parent)
