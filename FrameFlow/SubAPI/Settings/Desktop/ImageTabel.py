"""图像显示单元格-表格"""
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from SubAPI.WallHaven.api import ImageData

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QAbstractItemView

from SubAPI.WallHaven.api.WorkFlow import ThumbWorkFlow

from Fun.BaseTools import LogClass
from Fun.QtWidget import ImageCell
from Fun.QtWidget.FTabelWidget import DataFrameListBase, ListWidgetBase

logger = LogClass.get_logger(__name__, console_level='WARNING')

TIMEOUT = 200  # 定时器超时时间ms


class ImageTableCell(ImageCell):
    """图像单元格"""
    thumbStartSignal = Signal(ThumbWorkFlow)  # 略缩图加载开始
    thumbFinishedSignal = Signal(ThumbWorkFlow)  # 略缩图加载完成
    thumbStopSignal = Signal(ThumbWorkFlow)  # 略缩图停止
    thumbClearSignal = Signal(ThumbWorkFlow, object)  # 略缩图清除

    def __init__(self, parent: 'ImageTable' = None):
        super().__init__(parent, main_widget_type=ImageCell.GROUPBOX_AND_CARDWIDGET)
        self.__thumb_url: Optional[str] = None  # 略缩图
        self.__thumb_work: Optional[ThumbWorkFlow] = None  # 任务流
        self.__uiInit()
        self.__bind()

    def __uiInit(self):
        # 添加控件
        self._layout_title.setSpacing(5)

    def __bind(self):
        self.thumbStartSignal.connect(self._thumbStart)
        self.thumbFinishedSignal.connect(self._thumbFinished)

    def _thumbStart(self):
        self.setImageText('加载图片中...')

    def _thumbFinished(self, task: ThumbWorkFlow):
        """略缩图加载完成时"""
        if isinstance(task, ThumbWorkFlow):
            result: Optional[ImageData] = task.result()
            try:
                if result is not None:
                    self.setImage(result.generate_thumb())
            except Exception as e:
                logger.exception(f"{self.__class__.__name__} 略缩图加载错误: {e}")
                self.setImageText('加载图片失败')
        else:
            self.setImageText('停止加载图片')

    def _create_thumb_work(self):
        """创建略缩图加载任务"""
        # 清理旧任务
        if self.__thumb_work is not None:
            self.__thumb_work.clear()

        if self.__thumb_url is not None:
            self.__thumb_work = ThumbWorkFlow(self.__thumb_url)
            self.__thumb_work.start_signal.bridge_signal(self.thumbStartSignal)
            self.__thumb_work.finish_signal.bridge_signal(self.thumbFinishedSignal)
            self.__thumb_work.stop_signal.bridge_signal(self.thumbStopSignal)
            self.__thumb_work.clear_signal.bridge_signal(self.thumbClearSignal)

    def isShowImage(self):
        """当前是否显示了图片"""
        return self.image_widget.isShowImage()

    def setThumbUrl(self, url: str):
        """设置略缩图"""
        self.__thumb_url = url
        self._create_thumb_work()

    def startThumb(self, parent_task=None):
        if self.isShowImage():
            logger.warning(f'{self.__class__.__name__}.startThumb: 略缩图已显示,但任务被再次启动')

        if self.__thumb_work is not None:
            if not self.__thumb_work.state.isRunning:
                self.__thumb_work.start(priority=2, parent_task=parent_task)
            else:
                logger.warning(f'{self.__class__.__name__}.startThumb: 略缩图任务正在运行')
        else:
            raise RuntimeError('略缩图任务未创建')

    def stopThumb(self):
        """停止略缩图加载任务"""
        if self.__thumb_work is not None:
            self.__thumb_work.stop()
        else:
            logger.warning(f'{self.__class__.__name__}.stopThumb: 略缩图任务未创建')

    def clearThumb(self):
        """清理略缩图"""
        self.image_widget.set_image(None)
        if self.__thumb_work is not None:
            self.__thumb_work.clear()
        else:
            logger.warning(f'{self.__class__.__name__}.clearThumb: 略缩图任务未创建')

    def deleteLater(self):
        """确保资源删除干净"""
        # 由于表格会在刷新视图时删除掉不可见区域单元格
        self.clearThumb()
        super().deleteLater()


class ImageTableData(DataFrameListBase):
    """表格数据"""
    column_choose_name = '选择'

    def getRowIndex(self, item, column_name) -> int:
        """获取某行的索引"""
        with self._lock:
            data = self._dataframe[self._dataframe[column_name] == item]
            if data.empty:
                return -1
            return data.index[0]

    def clearSelect(self) -> bool:
        """清空选择"""
        with self._lock:
            if self.column_choose_name in self._dataframe.columns:
                self._dataframe['选择'] = False
                self.dataRefresh.emit()
                return True
        return False

    def selectAll(self) -> bool:
        """全选"""
        with self._lock:
            if self.column_choose_name in self._dataframe.columns:
                self._dataframe['选择'] = True
                self.dataRefresh.emit()
                return True
        return False

    def disSelect(self):
        """取消全选"""
        with self._lock:
            if self.column_choose_name in self._dataframe.columns:
                self._dataframe['选择'] = False
                self.dataRefresh.emit()
                return True
        return False


class ImageTable(ListWidgetBase):
    """表格数据展示"""

    def __init__(self, parent=None, round_menu_class=None):
        super().__init__(parent=parent)
        self.__round_menu_class = round_menu_class
        # 设置表格参数
        self.horizontalHeader().setVisible(False)  # 关闭水平表头
        self.enableResizeColumnsToContents(True)
        # 信号连接
        self.mouseRightClickedSignal.connect(self.showRoundMenu)

    def showRoundMenu(self, row, col, pos):
        """显示右键菜单"""
        if self.__round_menu_class is not None:
            index = row * self.columnCount() + col
            menu = self.__round_menu_class(index, pos, self)
            menu.deleteLater()

    def scrollToTopSlot(self, row_index: int):
        index = self.model().index(row_index, 0)
        self.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtTop)


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    test_cell = ImageTableCell()
    test_cell.show()
    app.exec()
