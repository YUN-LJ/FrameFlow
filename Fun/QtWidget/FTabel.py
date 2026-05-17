# PySide6原生组件
from PySide6.QtCore import Signal, Qt, QPoint
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (QTableWidgetItem,
                               QHeaderView, QAbstractItemView, QWidget)
# 风格化组件
from qfluentwidgets.components.widgets import (
    TableWidget
)
from Fun.QtWidget import debouncer_timer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Fun.QtWidget import ImageCellBase

TIMEOUT = 200  # 防抖超时时间


class TableBase(TableWidget):
    """
    表格基类
    使用self.loadVisibleLazy可防抖
    列宽默认自适应列宽
    """
    mouseRightClickedSignal = Signal(int, int, QPoint)  # 鼠标右击时发送row,col,以及点击时的坐标
    scrollChangedSignal = Signal(list)  # 滚动条滚动时发送当前可见行

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.__parent = parent
        self.cellRatio = 3 / 4  # 单元格宽高比
        self.fixed_row_height = None  # 固定行高
        # ui重绘定时器
        self.__update_ui_timer = debouncer_timer(self.updateUi)

        # 可见内容加载延迟器
        self.loadVisible_timer = debouncer_timer(self.loadVisible)

        # 高度调整定时器
        self.resizeRows_timer = debouncer_timer(self._resizeRowsToContents)

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
        self.scrollChangedSignal.connect(self.loadVisibleLazy)

    def mouseRightClicked(self, position):
        """显示右键菜单"""
        # position 是相对 viewport() 的坐标
        # global_pos = self.viewport().mapToGlobal(position)# 直接使用 viewport() 转换到全局坐标
        global_pos = QCursor.pos()  # 直接获取鼠标当前全局坐标
        index = self.indexAt(position)  # 获取点击位置的行和列
        if index.isValid():
            self.mouseRightClickedSignal.emit(index.row(), index.column(), global_pos)

    def loadVisible(self, rows: list = None):
        """
        加载当前可见区域数据
        子类重写此方法来完成数据显示
        实现数据层和视图层分离
        :param rows:当且可见行
        """
        raise NotImplementedError('请实现loadVisible方法')

    def loadVisibleLazy(self):
        """延迟加载可见行数据"""
        self.loadVisible_timer.start(TIMEOUT)

    def enableResizeRowsToContents(self, enabled: bool):
        """启用行高自适应调整"""
        self.enable_resize_rows_to_contents = enabled

    def enableRowVisibleCheck(self, enabled: bool = True):
        """启用可见行检查定时器"""

        def sub_func():
            self.scroll_check_timer.start(TIMEOUT)

        if enabled:
            # 使用定时器实现防止滚动条快速滚动而频繁触发信号
            self.scroll_check_timer = debouncer_timer(self.visibleRow)
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

    def _resizeRowsToContents(self):
        """实际执行高度调整函数"""
        if self.enable_resize_rows_to_contents:
            # 计算行高
            if self.fixed_row_height is None:
                width = self.columnWidth(0)  # 获取当前列宽
                height = width / self.cellRatio  # 计算高度
                height = height if height < self.height() else self.height()
            else:
                height = self.fixed_row_height
            # 设置行高
            for index_row in range(self.rowCount()):
                self.setRowHeight(index_row, height)
            # 设置滚动条步进
            self.verticalScrollBar().setSingleStep(int(height / 6))
            # 触发布局更新
            self.__update_ui_timer.start(100)

    def resizeRowsToContentsLazy(self):
        self.resizeRows_timer.start(TIMEOUT)

    def setFixedRowHeight(self, height: int):
        """
        设置固定行高,设置了固定行高后,自动调整行高函数将设置固定行高
        :param height:行高
        """
        self.fixed_row_height = height

    def updateUi(self):
        # 触发布局更新
        self.updateGeometry()
        self.updateGeometries()
        self.viewport().update()

    def resizeEvent(self, e):
        self.resizeRowsToContentsLazy()
        self.loadVisibleLazy()
        super().resizeEvent(e)

    def showMaximized(self):
        self.loadVisibleLazy()
        super().showMaximized()

    def showNormal(self):
        self.loadVisibleLazy()
        super().showNormal()


class TableDataBase:
    """表格数据基类"""

    def __init__(self):
        self.data = None  # 数据实例

    def get_data(self, *args, **kwargs):
        """获取某一行或某个单元格数据"""
        raise NotImplementedError('请实现get_data方法')

    def set_data(self, data):
        """设置数据"""
        self.data = data

    def clear_data(self):
        """清空数据"""
        self.data = None

    def __len__(self):
        raise NotImplementedError('请实现__len__方法')


class TableDataCell(TableDataBase):
    """
    表格单元格数据
    需要实现get_data和__len__方法
    并自行调用set_data方法设置内部数据属性data
    """

    def __init__(self, parent: 'TableCell'):
        super().__init__()
        self.parent = parent
        self._enable_page_view = False  # 分页显示

    def get_data(self, virtual_index: int, virtual_page: int, original_index: int) -> object | None:
        """
        获取数据
        :param virtual_index:表格内虚拟索引
        :param virtual_page:所在页码
        :param original_index:原始数据索引
        return :单元格数据,没有数据时请返回None
        """
        raise NotImplementedError('请实现get_data方法')

    def columnCount(self) -> int:
        """获取表格列数"""
        return self.parent.columnCount()

    def rowCount(self) -> int:
        """获取表格行数"""
        return self.parent.rowCount()

    def enablePagedView(self, enable: bool, page_size: int = 24):
        """启用分页显示"""
        self._enable_page_view = enable
        self.page_size = page_size

    # ---计算数据索引的方法---
    def getIndexInPage(self, virtual_index: int) -> int:
        """
        计算当前虚拟索引所在第几页
        :return 不启用分页显示时始终返回1
        """
        # 向上取整,计算每页需要的行数和格子数
        if self._enable_page_view:
            page_rows = -(-self.page_size // self.columnCount())  # 一页数据需要的行数
            cells_per_page = page_rows * self.columnCount()  # 每页实际占用的格子数（含空缺）
            # 计算当前虚拟索引在第几页
            page = virtual_index // cells_per_page
            return page + 1
        else:
            return 1

    def getTotalTableIndex(self, total_data: int) -> int:
        """
        计算填满当前表格需要的总数据量
        如果一页为24条数据,当前一行显示5条数据则每一页的最后一行会缺少数据
        会将这些空缺的单元格也算上,方便后续分页显示
        不启用分页显示时一页数据即为当前总数据量
        """
        page_size = self.page_size if self._enable_page_view else len(self)
        # 向上取整,由于负数使用地板除后由-2.33->-3,所以使用-(-24//5)
        page_rows = -(-page_size // self.columnCount())  # 一页数据需要的行数
        # 每页实际需要的格子数（包含空缺）
        cells_per_page = page_rows * self.columnCount()
        # 总页数
        total_pages = -(-total_data // page_size)  # 向上取整
        finally_count = total_data - (total_pages - 1) * page_size
        total_data = (total_pages - 1) * cells_per_page + finally_count
        return total_data

    def tableIndexToIndex(self, virtual_index: int) -> int:
        """
        将表格中的虚拟索引（包含空缺单元格）转换为原始数据索引

        Args:
            virtual_index: 表格中的虚拟索引（0-based），包含空缺单元格

        Returns:
            原始数据中的索引（0-based）

        Example:
            如果 columnCount=5, PAGE_SIZE=24
            虚拟索引 0-24 应该映射到原始数据 0-23（第1页）
            虚拟索引 25 对应新页的原始索引 24
            虚拟索引中的空缺位置（24）应该返回 -1
        """
        page_size = self.page_size if self._enable_page_view else len(self)
        # 向上取整,计算每页需要的行数和格子数
        page_rows = -(-page_size // self.columnCount())  # 一页数据需要的行数
        cells_per_page = page_rows * self.columnCount()  # 每页实际占用的格子数（含空缺）

        # 计算当前虚拟索引在第几页
        page = virtual_index // cells_per_page

        # 在当前页内的虚拟位置
        pos_in_page_virtual = virtual_index % cells_per_page

        # 计算在当前页内的行和列
        table_row = pos_in_page_virtual // self.columnCount()
        table_col = pos_in_page_virtual % self.columnCount()

        # 计算在当前页内的原始数据位置
        pos_in_page_real = table_row * self.columnCount() + table_col

        # 检查这个位置是否在有效数据范围内（最后一行的空缺单元格）
        if pos_in_page_real >= page_size:
            return -1  # 返回-1表示这是空缺单元格，无有效数据

        # 转换为全局原始索引
        original_index = page * page_size + pos_in_page_real

        return original_index


class TableCell(TableBase):
    """
    单元格表格类
    一个单元格显示一个完整的数据
    需要实现loadCell方法和必须设置setTableData
    否则页面将加载不了数据
    内部数据实例table_data,自行完成数据的添加删除等操作
    表格只负责显示数据
    """
    currentPageSignal = Signal(int)  # 发送当前处于哪一页
    loadNextPageSignal = Signal(int)  # 发送加载哪一页的信号

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._enable_columns_to_contents = False
        self.table_data: 'TableDataCell' = None  # 表格数据

    def loadCell(self, row, column, cell_data):
        """
        加载单元格方法,子类必须实现
        :param row:行号
        :param column:列号
        :param cell_data:该单元格数据
        """
        raise NotImplementedError('请实现loadCell方法')

    def setTableData(self, data: 'TableDataCell'):
        """设置表格数据"""
        self.table_data = data

    def loadVisible(self, rows: list = None):
        """
        加载可见区域
        返回可见行
        """
        if self.table_data is None or len(self.table_data) == 0:
            return None
        # ---准备阶段---
        need_resize_rows = self.rowCount() == 0
        # 设置行数
        self.setRowCount(len(self.table_data))
        if need_resize_rows:
            self._resizeRowsToContents()
        self.resizeColumnsCountToContents()
        rows = self.visibleRow(False) if rows is None else rows
        if rows:
            # 发送当前处于哪一页的信号
            column_count = self.columnCount()
            current_page = self.table_data.getIndexInPage(max(rows) * column_count)
            self.currentPageSignal.emit(current_page)
            # ---添加阶段---
            for row in rows:
                for column in range(column_count):
                    # 判断是否为空数据
                    virtual_index = row * column_count + column
                    virtual_page = self.table_data.getIndexInPage(virtual_index)  # 获取虚拟数据页码
                    original_index = self.table_data.tableIndexToIndex(virtual_index)  # 原始数据索引
                    if original_index == -1:  # 意味着这里是空数据
                        self.clearCell(row, column)
                        continue
                    # 获取数据
                    cell_data = self.table_data.get_data(virtual_index, virtual_page, original_index)  # 获取该单元格数据
                    if cell_data is None:
                        # 清除该行无内容单元格
                        for i in range(column, column_count):
                            self.clearCell(row, i)
                        # 发送搜索下一页信号,只有当数据总页数大于等于当前页码,且位于第一列时发送
                        if virtual_page <= len(self.table_data) and column == 0:
                            self.loadNextPageSignal.emit(virtual_page)
                        return None
                    # 加载单元格
                    self.loadCell(row, column, cell_data)
        self.resizeRowsToContentsLazy()
        return rows

    def getLenToRow(self, index: int) -> int:
        """将一维索引换算成行号（从0开始），如果是数据数量需要-1"""
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
        if data_len <= 0:
            return super().setRowCount(0)
        max_rows = self.getLenToRow(data_len - 1) + 1
        if max_rows != self.rowCount():
            super().setRowCount(max_rows)
            self.resizeRowsToContentsLazy()

    def clearInvisibleCells(self, visible_rows: list, buffer_rows: int = 2):
        """
        清理不可见区域的单元格以释放内存
        :param visible_rows: 当前可见的行列表
        :param buffer_rows: 缓冲区行数，保留可见区域上下几行的数据，避免频繁加载
        """
        if not visible_rows or self.rowCount() == 0:
            return

        # 计算可见行的范围
        min_visible_row = min(visible_rows)
        max_visible_row = max(visible_rows)

        # 设置缓冲区：保留可见区域上下各几行的数据，避免滚动时频繁重新加载
        keep_start = max(0, min_visible_row - buffer_rows)
        keep_end = min(self.rowCount() - 1, max_visible_row + buffer_rows)

        # 清理不在保留范围内的行
        column_count = self.columnCount()
        for row in range(self.rowCount()):
            if row < keep_start or row > keep_end:
                # 清理该行的所有单元格
                for column in range(column_count):
                    # 清理 QWidget 类型的 cell
                    cell = self.cellWidget(row, column)
                    if cell is not None:
                        self.removeCellWidget(row, column)
                        cell.deleteLater()
                    # 清理 QTableWidgetItem 类型的 item
                    item = self.item(row, column)
                    if item is not None:
                        self.takeItem(row, column)

    def enableColumnsCountToContents(self, enable: bool, min_width: int = 200, max_width: int = 300):
        """启用根据表格大小调整列数"""
        self._enable_columns_to_contents = enable
        self.min_columns_width = min_width
        self.max_columns_width = max_width

    def resizeColumnsCountToContents(self):
        """调整列数"""
        if self._enable_columns_to_contents:
            viewport_width = self.viewport().width()
            # 计算理想列数
            target_column_count = max(1, viewport_width // self.min_columns_width)
            # 验证列宽是否在合理范围内
            if target_column_count > 0:
                resulting_width = viewport_width / target_column_count
                # 如果结果列宽超过最大值，减少列数
                while resulting_width > self.max_columns_width and target_column_count > 1:
                    target_column_count -= 1
                    resulting_width = viewport_width / target_column_count
            # 只有当列数真正需要改变时才更新
            if target_column_count != self.columnCount():
                self.setColumnCount(target_column_count)

    def clearCell(self, row, column) -> bool:
        """清理单元格"""
        cell = self.cellWidget(row, column)
        self.removeCellWidget(row, column)
        if cell is not None:
            cell.deleteLater()
            return True
        return False


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
        改变某行的item值
        :param row_data:一行数据,会忽略QWidget类型
        """
        for col, widget in enumerate(row_data):
            if isinstance(widget, (str, int, float)):
                item = QTableWidgetItem(widget)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row_index, col, item)
