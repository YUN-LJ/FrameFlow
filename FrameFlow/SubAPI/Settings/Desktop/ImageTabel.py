"""图像显示单元格-表格"""
from PySide6.QtWidgets import QAbstractItemView

from Fun.QtWidget.FTabelWidget import DataFrameListBase, ListWidgetBase


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
        index = row * self.columnCount() + col
        menu = self.__round_menu_class(index, pos, self)
        menu.deleteLater()

    def scrollToTopSlot(self, row_index: int):
        index = self.model().index(row_index, 0)
        self.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtTop)
