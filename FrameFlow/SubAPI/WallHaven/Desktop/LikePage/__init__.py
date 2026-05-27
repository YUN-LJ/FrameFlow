"""收藏夹窗口"""
from SubAPI.WallHaven.ImportPack import *
from SubAPI.WallHaven import api
from SubAPI.WallHaven.Desktop.LikePage.DesignFile.LikePage import Ui_like_widget


class LikePage(FluentWidgetFromUI, Ui_like_widget):
    addKeyWordFinished = Signal(api.KeyWordTask)  # 添加关键词完成

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__parent = parent
        self.slot = LikePageSlot(self, self.__parent)
        self.uiInit()
        self.bind()

    def uiInit(self):
        self.pushButton_update.setIcon(FIF.UPDATE)
        self.pushButton_add.setIcon(FIF.ADD)
        self.pushButton_delete.setIcon(FIF.DELETE)
        self.progressBar.hide()
        self.progress_label.hide()
        # 所有子控件继承样式
        self.setStyleSheet("LikePage, LikePage * {background-color: transparent;}")

    def bind(self):
        self.pushButton_update.clicked.connect(self.slot.pushButton_update)
        self.pushButton_add.clicked.connect(self.slot.pushButton_add)
        self.pushButton_delete.clicked.connect(self.slot.pushButton_delete)
        self.lineEdit.searchSignal.connect(self.slot.lineEdit)
        self.lineEdit.returnPressed.connect(self.slot.lineEdit)

    def __startUpdate(self):
        self.progressBar.show()
        self.progress_label.show()

    def __progressUpdate(self, value: TaskProgress):
        self.progress_label.setText(f'更新中:{value.finished}/{value.total}')
        self.progressBar.setValue(value.get_progress())

    def __finishUpdate(self):
        self.progressBar.hide()
        self.progress_label.hide()


class LikePageSlot:
    def __init__(self, parent: LikePage, top_parent):
        self.parent = parent
        self.top_parent = top_parent
        self.signal_connect()

    def signal_connect(self):
        self.parent.addKeyWordFinished.connect(self.__addKeyWordFinishedSlot)
        signal = SignalConfig.WallHavenSignal.like_signal
        signal.startSignal.connect(self.__start)
        signal.progressSignal.connect(self.__progress)
        signal.finishSignal.connect(self.__finish)
        signal.stopSignal.connect(self.__stop)

    @info_bar_decorator
    def __addKeyWordFinishedSlot(self, task: api.KeyWordTask):
        self.parent.pushButton_add.setEnabled(True)
        if task.result() is not None:
            return True, f'{task.params.q}添加成功', self.parent
        return False, f'{task.params.q}添加失败', self.parent

    @info_bar_decorator
    def __start(self, _):
        self.parent.pushButton_update.setIcon(FIF.CLOSE)
        self.parent.pushButton_update.setText('取消')
        self.parent.progressBar.setValue(0)
        self.parent.progress_label.setText('更新中:')
        self.parent.progressBar.show()
        self.parent.progress_label.show()
        return True, '更新开始', self.parent

    def __progress(self, value: TaskProgress):
        self.parent.progressBar.setValue(value.get_progress())
        self.parent.progress_label.setText(f'更新中:{value.finished}/{value.total}')

    @info_bar_decorator
    def __finish(self, value: api.Task):
        text = '更新成功' if value.result() else '更新失败'
        self.parent.pushButton_update.setIcon(FIF.UPDATE)
        self.parent.pushButton_update.setText('更新')
        self.parent.progressBar.hide()
        self.parent.progress_label.hide()
        return value.result(), text, self.parent

    @info_bar_decorator
    def __stop(self, _):
        self.parent.pushButton_update.setIcon(FIF.UPDATE)
        self.parent.pushButton_update.setText('更新')
        self.parent.progressBar.hide()
        self.parent.progress_label.hide()
        return True, '已取消', self.parent

    @info_bar_decorator
    def lineEdit(self, key_word=None):
        key_word = self.parent.lineEdit.text() if key_word is None else key_word
        if self.parent.tableWidget.searchKeyWord(key_word):
            return True, f'已将{key_word}定位到首行', self.parent
        return False, f'未找到{key_word}', self.parent

    def pushButton_update(self):
        if self.parent.pushButton_update._icon == FIF.UPDATE:
            self.parent.tableWidget.startSerialWorkFlow()
        elif self.parent.pushButton_update._icon == FIF.CLOSE:
            self.parent.tableWidget.stopSerialWorkFlow()

    @info_bar_decorator
    def pushButton_add(self):
        key_word = self.parent.lineEdit.text()
        if key_word:
            task = self.parent.tableWidget.addKeyWord(key_word)
            if task:
                self.parent.pushButton_add.setEnabled(False)
                task.finish_signal.connect(self.parent.addKeyWordFinished.emit)
                return True, '正在获取数据', self.parent
        return False, '数据已存在', self.parent

    @info_bar_decorator
    def pushButton_delete(self):
        select_len = len(self.parent.tableWidget.selected_rows)
        message = MessageBox('确认删除', f'是否删除{select_len}个？', GlobalValue.TOP_WINDOWS)
        if message.exec() and self.parent.tableWidget.delKeyWord():
            return True, '删除成功', self.parent
        return False, '已取消', self.parent


def start():
    from SubAPI.WallHaven.Desktop import DownloadPage
    global download
    download = DownloadPage()
    win = LikePage()
    win.show()
    download.move(20, 20)
    download.show()
    return win


if __name__ == '__main__':
    from SubAPI import StartAPI

    start_api = StartAPI(func=start, console_level='INFO')
    start_api.start_thread()
