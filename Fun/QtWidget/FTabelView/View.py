"""二维视图"""
from PySide6.QtCore import Signal, QPoint, Qt
from PySide6.QtGui import QCursor, QFontMetrics
from PySide6.QtWidgets import (
    QHeaderView, QAbstractItemView, QStyledItemDelegate, QWidget
)
from qfluentwidgets import TableView, SmoothMode

from Fun.BaseTools.Time import timer_decorator
from Fun.QtWidget import debouncer_timer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Model import DataFrameModelBase
TIMEOUT = 50


class DelegateBase(QStyledItemDelegate):
    """
    代理控件基类
    需要重写createEditor和setEditorData
    """
    GEOMETRY_FULL = 'full'  # 铺平
    GEOMETRY_CENTER = 'center'  # 居中
    GEOMETRY_ADJUSTED = 'adjusted'  # 固定内边距

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__geometry = self.GEOMETRY_FULL

    def setGeometry(self, geometry, adjusted: tuple = None, fixed_width=None, fixed_height=None):
        """
        设置代理控件的显示位置和尺寸
        :param geometry:布局枚举值
        :param adjusted:布局为adjusted时需要,内边距数值,例如(2,2,-2,-2)
        :param fixed_width:布局为center时需要,中心居中时,控件的固定宽度
        :param fixed_height:布局为center时需要,中心居中时,控件的固定高度
        """
        self.__geometry = geometry
        if adjusted:
            self.__geometry = self.GEOMETRY_ADJUSTED
            self.__adjusted = adjusted
        elif fixed_width:
            self.__geometry = self.GEOMETRY_CENTER
            self.__fixed_width = fixed_width
            self.__fixed_height = fixed_height

    @staticmethod
    def getEditorData(index):
        """从 UserRole 获取真实数据，而不是默认的 DisplayRole"""
        data = index.data(Qt.UserRole)  # 从模型拿真实数据
        if data is None:
            data = index.data(Qt.EditRole)  # 备用
        if data is None:
            data = index.data()  # 最后备用
        return data

    def createEditor(self, parent, option, index):
        """
        创建代理控件
        :param parent:父控件,一般是视图
        """
        raise NotImplementedError("请实现createEditor")

    def setEditorData(self, editor, index):
        """
        设置代理控件的数据
        """
        raise NotImplementedError("请实现setEditorData")

    def updateEditorGeometry(self, editor, option, index):
        """
        设置编辑器在表格中的位置和大小

        关键点：
        1. option.rect 是单元格的准确位置和尺寸
        2. 必须调用 setGeometry，否则编辑器会显示在错误位置
        3. 可以微调位置（比如添加偏移量）
        """
        # 1. 基础用法：完全填充单元格
        if self.__geometry == self.GEOMETRY_FULL:
            editor.setGeometry(option.rect)
        elif self.__geometry == self.GEOMETRY_CENTER:
            x = option.rect.center().x() - self.__fixed_width // 2
            y = option.rect.center().y() - self.__fixed_height // 2
            editor.setGeometry(x, y, self.__fixed_width, self.__fixed_height)
        elif self.__geometry == self.GEOMETRY_ADJUSTED:
            rect = option.rect.adjusted(*self.__adjusted)
            editor.setGeometry(rect)


class DataFrameViewBase(TableView):
    """
    用于显示DataFrame类型的视图基类
    几乎可以之间使用,
    使用需要设置模型和代理
        设置模型:setModel,模型必须是DataFrameModelBase或其子类
        设置代理:setDelegateColumn,如果不设置的话只单纯显示字符串
    视图只会加载可见范围内的数据
    setModel方法自动连接了模型数据变化的信号
    需要显示更新数据请使用updateUiLazy(延迟方法)或_updateUi(同步方法)
    """
    mouseRightClickedSignal = Signal(int, int, QPoint)  # 鼠标右击时发送row,col,以及点击时的坐标
    scrollChangedSignal = Signal(list)  # 滚动条滚动时发送当前可见行
    scrollToTopSignal = Signal(object)  # 滚动到顶部

    def __init__(self, model: 'DataFrameModelBase' = None, parent=None):
        """
        :param model: 数据模型，可选
        :param parent: 父控件，可选，默认为 None
        showGrid: 是否显示网格线，布尔值
        gridStyle: 网格线样式，如 Qt.SolidLine、Qt.DashLine 等
        sortingEnabled: 是否启用排序功能，布尔值
        wordWrap: 是否启用文本换行，布尔值
        cornerButtonEnabled: 是否显示左上角的角落按钮（全选按钮），布尔值
        """
        super().__init__(parent)
        if model is not None:
            self.setModel(model)
        self.__mode = model  # 模型
        self.__parent = self.parent()
        self.__cellRatio = 3 / 4  # 单元格宽高比
        self.__fixed_row_height = None
        self.__fixed_columns_width = None
        self.__columns_section_resize_mode = {}  # 列索引:列宽调整模式
        self.__display_delegate_row = set()  # 显示了代理的行
        self.__scroll_single_step = 6  # 滚动条单步大小除数,默认6
        # ui重绘定时器
        self.__update_ui_timer = debouncer_timer(self._updateUi)

        # 高度调整定时器
        self.__resizeRows_timer = debouncer_timer(self._resizeRowsToContents)

        # 列宽调整定时器
        self.__resizeColumns_timer = debouncer_timer(self._resizeColumnsToContents)

        # 加载代理控件定时器
        self.__load_delegate_timer = debouncer_timer(self._loadVisibleDelegate)

        self.__uiInit()
        self.__bind()

    def __uiInit(self):
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)  # 固定值,用户无法调整
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)  # 固定值,用户无法调整
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
        self.verticalHeader().setVisible(True)  # 隐藏垂直表头即左侧表头
        self.horizontalHeader().setVisible(True)  # 隐藏水平表头即顶侧表头
        self.setAlternatingRowColors(True)  # 交替行变色

    def __bind(self):
        self.enableResizeRowsToContents(True)
        # 启用自定义上下文菜单（必须设置）
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # 连接右键菜单信号
        self.customContextMenuRequested.connect(self.mouseRightClicked)
        # 滚动条值改变信号触发加载代理控件(非代理控件会自动加载)
        self.verticalScrollBar().valueChanged.connect(self.loadVisibleDelegateLazy)
        self.scrollToTopSignal.connect(self.scrollToTopSlot)

    def mouseRightClicked(self, position):
        """显示右键菜单"""
        # position 是相对 viewport() 的坐标
        # global_pos = self.viewport().mapToGlobal(position)# 直接使用 viewport() 转换到全局坐标
        global_pos = QCursor.pos()  # 直接获取鼠标当前全局坐标
        index = self.indexAt(position)  # 获取点击位置的行和列
        if index.isValid():
            self.mouseRightClickedSignal.emit(index.row(), index.column(), global_pos)

    # ---UI显示类方法---

    def _loadVisibleDelegate(self, buffer_rows: int = 2):
        """加载可见范围内的代理控件,删除不可见范围内的代理"""
        rows = self.getVisibleRow()  # 获取当前可见行
        if not rows:
            return None
        self.scrollChangedSignal.emit(rows)
        # 计算缓冲后的最小和最大行
        min_row = min(rows) - buffer_rows
        max_row = max(rows) + buffer_rows
        if min_row > 1:
            rows.append(min_row)
        if max_row < self.rowCount():
            rows.append(max_row)
        # 处理代理控件
        if self.__display_delegate_row:  # 清理已显示的代理
            for row in self.__display_delegate_row:
                for col in self.__mode.getDelegateColumn():
                    index = self.__mode.index(row, col)
                    self.closePersistentEditor(index)  # 删除代理,避免重复加载
            self.__display_delegate_row.clear()
        for row in rows:
            for col in self.__mode.getDelegateColumn():
                index = self.__mode.index(row, col)
                self.openPersistentEditor(index)  # 可见行,加载代理
        self.__display_delegate_row.update(rows)

    def loadVisibleDelegateLazy(self):
        """延迟加载可见行代理控件"""
        self.__load_delegate_timer.start(TIMEOUT)

    def _resizeRowsToContents(self):
        """实际执行高度调整函数"""
        if self.enable_resize_rows_to_contents:
            # 计算行高
            if self.__fixed_row_height is None:
                width = self.columnWidth(0)  # 获取当前列宽
                height = width / self.__cellRatio  # 计算高度
                height = height if height < self.height() else self.height()
            else:
                height = self.__fixed_row_height
            # 设置行高
            for index_row in range(self.rowCount()):
                self.setRowHeight(index_row, height)
            # 设置滚动条步进
            self.verticalScrollBar().setSingleStep(height // self.__scroll_single_step)

    def resizeRowsToContentsLazy(self):
        """延迟更新行高"""
        self.__resizeRows_timer.start(TIMEOUT)

    def _resizeColumnsToContents(self):
        """根据可见行内内容调整列宽"""
        stretch_columns = []  # 填充列
        all_columns = range(self.columnCount())
        for col in all_columns:
            mode = self.__columns_section_resize_mode.get(col, QHeaderView.Fixed)
            if mode == QHeaderView.Fixed or mode == QHeaderView.Interactive:
                self.setColumnWidth(col, self.__fixed_columns_width)
            elif mode == QHeaderView.ResizeToContents:
                max_width = self._get_visible_column_min_width(col)
                self.setColumnWidth(col, max_width)
            elif mode == QHeaderView.Stretch:
                stretch_columns.append(col)
        if stretch_columns:
            total_width = self.viewport().width()  # 总宽度
            use_width = sum(self.columnWidth(col) for col in set(all_columns) - set(stretch_columns))
            col_width = (total_width - use_width) // len(stretch_columns)
            for col in stretch_columns:
                max_width = self._get_visible_column_min_width(col)
                self.setColumnWidth(col, max(max_width, col_width))

    def resizeColumnsToContentsLazy(self):
        """延迟更新列宽"""
        self.__resizeColumns_timer.start(TIMEOUT)

    def _updateUi(self):
        # 触发布局更新
        self._resizeColumnsToContents()
        self._resizeRowsToContents()
        self.updateGeometry()
        self.updateGeometries()
        self.viewport().update()
        # 触发数据更新
        self._loadVisibleDelegate()

    def updateUiLazy(self):
        """延迟更新UI,数据刷新主要接口"""
        self.__update_ui_timer.start(TIMEOUT)

    def showEvent(self, event):
        self.updateUiLazy()
        super().showEvent(event)

    def resizeEvent(self, event):
        self.updateUiLazy()
        super().resizeEvent(event)

    # ---设置类方法---
    def setColumnCount(self, column_count: int):
        """设置列数"""
        self.__mode.setColumnCount(column_count)

    def setRowCount(self, row_count: int):
        """设置行数"""
        self.__mode.setRowCount(row_count)

    def enableResizeRowsToContents(self, enabled: bool):
        """启用行高自适应调整"""
        self.enable_resize_rows_to_contents = enabled

    def enableColumnResizeInteractive(self, col=None):
        """启用列宽可调整"""
        if col is None:
            self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        else:
            self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Interactive)

    def setScrollSmoothMode(self, mode=SmoothMode.LINEAR):
        """
        设置表格视图的滚动平滑模式

        :param mode: 滚动模式枚举值
            可选值（SmoothMode 枚举）：
            - 0: NO_SMOOTH     无平滑滚动，直接跳转，性能最好，最跟手
            - 1: CONSTANT      匀速滚动，速度恒定，感觉较机械
            - 2: LINEAR        线性滚动，与 CONSTANT 类似，速度均匀
            - 3: QUADRATI      二次方缓动，有加速/减速冲击感
            - 4: COSINE        余弦缓动，平滑自然，视觉体验最佳（默认推荐）
        """
        self.scrollDelagate.verticalSmoothScroll.setSmoothMode(mode)
        if mode == SmoothMode.NO_SMOOTH:
            self.verticalScrollBar().setSingleStep(self.rowHeight(0) // 3)

    def setScrollSingleStep(self, step: int):
        """设置单步滚动除数,内部会自动计算每次滚动高度,使用行高除以当前值"""
        self.__scroll_single_step = step

    def setFixedRowHeight(self, height: int):
        """
        设置固定行高,设置了固定行高后,自动调整行高函数将设置固定行高
        :param height:行高
        """
        self.__fixed_row_height = height

    def setDelegateColumn(self, column_index: int, delegate: QStyledItemDelegate):
        """
        设置指定列的代理控件
        :param column_index:列序号
        :param delegate:代理类
        """
        self.__mode.setDelegateColumn(column_index)
        self.setItemDelegateForColumn(column_index, delegate)

    def setColumnSectionResizeMode(self, col=None, mode=QHeaderView.Fixed, fixed_width: int = None):
        """
        设置列宽调整模式
        :param col:列索引,默认设置全部
        :param mode:模式,可选值QHeaderView.Stretch:填充剩余空间,
                             QHeaderView.ResizeToContents:根据内容调整,默认
                             QHeaderView.Fixed:固定值,用户无法调整
                             QHeaderView.Interactive:固定值,用户允许调整
        :param fixed_width:固定列宽值
        """
        if mode == QHeaderView.Fixed or mode == QHeaderView.Interactive:
            if fixed_width is None:
                raise ValueError("请设置固定列宽值")
            self.__fixed_columns_width = fixed_width
        if col is None:
            if mode == QHeaderView.Fixed or mode == QHeaderView.Interactive:
                self.horizontalHeader().setSectionResizeMode(mode)
            for col in range(self.columnCount()):
                self.__columns_section_resize_mode[col] = mode
        else:
            if col < 0 or col > self.columnCount() - 1:
                raise ValueError("列索引超出范围")
            if mode == QHeaderView.Fixed or mode == QHeaderView.Interactive:
                self.horizontalHeader().setSectionResizeMode(col, mode)
            self.__columns_section_resize_mode[col] = mode
        self.resizeColumnsToContentsLazy()

    def setModel(self, model):
        """设置模型并连接信号"""
        self.__mode = model
        super().setModel(model)
        if model is not None:
            # 连接模型的数据变化信号到视图刷新
            model.dataChanged.connect(self.updateUiLazy)
            model.modelReset.connect(self.updateUiLazy)
            model.layoutChanged.connect(self.updateUiLazy)

    # ---获取类方法---
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

    def getVisibleRow(self) -> list:
        """获取当前可见的行"""
        scroll_pos = self.verticalScrollBar().value()
        viewport_height = self.viewport().height()
        total_rows = self.rowCount()
        if total_rows == 0:
            return []
        row_height = self.rowHeight(0)
        # 直接计算并返回可见行范围
        start_row = max(0, scroll_pos // row_height)
        end_row = min(total_rows - 1, (scroll_pos + viewport_height) // row_height)
        visible_rows = list(range(start_row, end_row + 1))
        return visible_rows

    def rowCount(self) -> int:
        return self.__mode.rowCount()

    def columnCount(self) -> int:
        return self.__mode.columnCount()

    # ---辅助方法---
    def _calculate_text_width(self, text: str) -> int:
        """计算文本宽度"""
        # 考虑单元格内边距
        font = self.font()
        metrics = QFontMetrics(font)
        return metrics.horizontalAdvance(text) + 10

    def _get_visible_column_min_width(self, col, buffer_width=30) -> int:
        """计算可见范围内某列的最小宽度"""
        visible_rows = self.getVisibleRow()
        # 获取列宽内容需要的大小
        header_data = self.__mode.headerData(col, Qt.Horizontal).split("\n")
        max_width = max([self._calculate_text_width(text) for text in header_data])
        for row in visible_rows:
            index = self.__mode.index(row, col)
            text = self.__mode.data(index, Qt.DisplayRole)
            if text:  # 获取可见范围内最大列宽
                width = self._calculate_text_width(text) + buffer_width
                if width > max_width:
                    max_width = width
        return max_width

    def scrollToTopSlot(self, value):
        raise NotImplementedError("请实现scrollToTopSlot方法")


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    from Model import DataFrameModelBase
    from SubAPI.DataManage import KEY_WORD
    from Fun.QtWidget import MainWidget

    KEY_WORD.is_loaded(0)
    app = QApplication([])
    table_view = DataFrameViewBase()
    table_view.setFixedRowHeight(80)
    with KEY_WORD as df:
        data = df.copy(deep=True)
    table_view.setModel(DataFrameModelBase(data))
    table_view.setColumnSectionResizeMode(mode=QHeaderView.ResizeToContents)
    table_view.setColumnSectionResizeMode(0, mode=QHeaderView.Stretch)
    table_view.show()
    MainWidget.change_theme()
    app.exec()
