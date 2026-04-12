from threading import Lock
from typing import Optional
# PySide6原生组件
from PySide6.QtCore import Signal, Qt, QTimer, QObject, QPoint
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QTableWidgetItem,
                               QGroupBox, QHeaderView, QStackedWidget, QTableWidget,
                               QAbstractItemView, QWidget, QSizePolicy, QApplication)
# 风格化组件
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets.components.widgets import (
    TableWidget, CheckBox, TitleLabel, IndeterminateProgressRing,
    ProgressRing, PrimaryToolButton
)

TIMEOUT = 200  # 防抖超时时间


class TableBase(TableWidget):
    """表格基类"""
    mouseRightClickedSignal = Signal(int, int, QPoint)  # 鼠标右击时发送row,col,以及点击时的坐标
    scrollChangedSignal = Signal(list)  # 滚动条滚动时发送当前可见行

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.__parent = parent
        self.cellRatio = 3 / 4  # 单元格宽高比
        self.__uiInit()
        self.__bind()

    def __uiInit(self):
        self.resize(400, 300)
        self.setColumnCount(4)  # 设置列数
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应列宽
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
        self.verticalHeader().setVisible(False)  # 隐藏垂直表头即左侧表头
        self.horizontalHeader().setVisible(False)  # 隐藏水平表头即顶侧表头
        self.setAlternatingRowColors(True)  # 交替行变色

    def __bind(self):
        self.enableResizeRowsToContents(True)
        self.enableRowVisibleCheck(True)
        # 启用自定义上下文菜单（必须设置）
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # 连接右键菜单信号
        self.customContextMenuRequested.connect(self.mouseRightClicked)
        self.scrollChangedSignal.connect(self.loadVisible)

    def mouseRightClicked(self, position):
        """显示右键菜单"""
        # 获取点击的坐标
        pos = self.viewport().mapFromGlobal(self.mapToGlobal(position))
        # 方法1：获取点击位置的行和列
        index = self.indexAt(pos)
        if index.isValid():
            self.mouseRightClickedSignal.emit(index.row(), index.column(), self.mapToGlobal(position))

    def loadVisible(self, rows: list = None):
        """
        加载当前可见区域数据
        子类重写此方法来完成数据显示
        实现数据层和视图层分离
        """

    def enableResizeRowsToContents(self, enabled: bool):
        """启用行高自适应调整"""
        self.enable_resize_rows_to_contents = enabled

    def enableRowVisibleCheck(self, enabled: bool = True):
        """启用可见行检查定时器"""

        def sub_func():
            self.scroll_check_timer.start(TIMEOUT)

        if enabled:
            # 使用定时器实现防止滚动条快速滚动而频繁触发信号
            self.scroll_check_timer = QTimer()
            self.scroll_check_timer.setSingleShot(True)  # 单次触发
            self.scroll_check_timer.timeout.connect(self.visibleRow)
            self.verticalScrollBar().valueChanged.connect(sub_func)
        else:
            self.verticalScrollBar().valueChanged.disconnect(sub_func)

    def visibleRow(self, emit=True) -> list:
        """获取当前显示的行"""
        scroll_pos = self.verticalScrollBar().value()
        viewport_height = self.viewport().height()
        total_rows = self.rowCount()
        if total_rows == 0:
            if emit:
                self.scrollChangedSignal.emit([])
            return []
        row_height = self.rowHeight(0)
        # 直接计算并返回可见行范围
        start_row = max(0, scroll_pos // row_height)
        end_row = min(total_rows - 1, (scroll_pos + viewport_height) // row_height)
        visible_rows = list(range(start_row, end_row + 1))
        if emit:
            self.scrollChangedSignal.emit(visible_rows)
        return visible_rows

    def getWidgetCoord(self, widget: QWidget, column_index: int | list = None) -> tuple[int, int]:
        """
        获取目标容器坐标
        :param column_index:指定搜索哪一列
        """
        column = range(self.columnCount()) if column_index is None else column_index
        if isinstance(column, int):
            column = [column]
        for target_row in range(self.rowCount()):
            for target_col in column:
                if self.cellWidget(target_row, target_col) == widget:
                    return target_row, target_col
        return -1, -1

    def resizeRowsToContents(self):
        super().resizeRowsToContents()
        if self.enable_resize_rows_to_contents:
            width = self.columnWidth(0)  # 获取当前列宽
            height = width / self.cellRatio  # 计算高度
            height = height if height < self.height() else self.height()
            for index_row in range(self.rowCount()):
                self.setRowHeight(index_row, height)
            self.verticalScrollBar().setSingleStep(int(height / 4))
            # 触发布局更新
            # self.updateGeometry()
            # self.updateGeometries()
            # self.viewport().update()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.resizeRowsToContents()


class TableCell(TableBase):
    """单元格表格"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def getLenToRow(self, index: int) -> int:
        """将一维索引换算成行号（从0开始）"""
        if index < 0:
            return -1
        column_count = self.columnCount()
        if column_count <= 0:
            return -1
        # 行号 = 索引 // 列数
        row = index // column_count
        return row

    def setRowCount(self, data_len: int):
        """
        设置表格行数,内部根据输入的数据长度自动换算成行数
        :param data_len:数据长度
        """
        max_rows = self.getLenToRow(data_len) + 1
        if max_rows != self.rowCount():
            super().setRowCount(max_rows)
            self.resizeRowsToContents()


class TableRow(TableBase):
    """行数据表格"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def setColumnHeader(self, header: list):
        """设置列头"""
        self.setColumnCount(len(header))
        self.horizontalHeader().setVisible(True)
        self.setHorizontalHeaderLabels(header)

    def addRow(self, row_index, row_data: list[QWidget | str | int | float]):
        """新增一行数据"""
        if row_index > self.rowCount():
            self.insertRow(row_index)
        for col, widget in enumerate(row_data):
            if isinstance(widget, (str, int, float)):
                item = QTableWidgetItem(widget)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row_index, col, item)
            elif isinstance(widget, QWidget):
                self.setCellWidget(row_index, col, widget)
            else:
                raise TypeError(f'{widget}是不支持的类型{type(widget)}')

    def delRow(self, row_index):
        """删除一行数据"""
        self.removeRow(row_index)

    def changeRowItem(self, row_index, row_data: list[QWidget | str | int | float]):
        """
        改变一行的item值
        :param row_data:一行数据,会忽略QWidget类型
        """
        for col, widget in enumerate(row_data):
            if isinstance(widget, (str, int, float)):
                item = QTableWidgetItem(widget)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row_index, col, item)


if __name__ == '__main__':
    from BaseClass import KeyWord
    from FCell import ImageCell


    def scrollchanged(rows: list):
        column = table.columnCount()
        for row in rows:
            for col in range(column):
                index = row * column + col
                if index < KeyWord.data().shape[0]:
                    cell_data = KeyWord.data().iloc[index]
                    cell = ImageCell(table)
                    cell.setTitle(cell_data['关键词'])
                    table.setCellWidget(row, col, cell)
                    table.resizeRowsToContents()


    app = QApplication([])
    KeyWord.is_loaded(1)
    table = TableBase()
    table.setRowCount(KeyWord.data().shape[0])
    table.scrollChangedSignal.connect(scrollchanged)
    table.show()
    app.exec()
