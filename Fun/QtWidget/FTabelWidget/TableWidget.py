"""二维视图"""
from PySide6.QtCore import Signal, QPoint, Qt, QTimer
from PySide6.QtGui import QCursor, QFontMetrics
from PySide6.QtWidgets import QHeaderView, QAbstractItemView, QWidget, QTableWidgetItem
from qfluentwidgets import SmoothMode, TableWidget
from Fun.QtWidget import debouncer_timer
from Fun.QtWidget.FTabelWidget.TableData import DataFrameModelBase, DataFrameListBase
from Fun.BaseTools.Time import timer_decorator

TIMEOUT = 200


class DelegateBase:
    """
    代理控件基类
    需要重写createWidget、deleteWidget、setWidgetData
    内部有私有方法用于管理创建的控件
    """

    def __init__(self, parent=None):
        self.__parent = parent
        # 代理控件字典{row,col:代理控件}
        self.__all_widget: dict[tuple[int, int], QWidget] = {}

    def _createWidget(self, parent, row, col) -> QWidget:
        widget = self.__all_widget.get((row, col), None)
        # 检查widget是否有效且未被删除
        if widget is not None:
            try:
                # 尝试访问一个属性来验证对象是否有效
                _ = widget.objectName()
                return widget
            except RuntimeError:
                # 对象已被删除，从缓存中移除
                self.__all_widget.pop((row, col), None)
        # 创建新控件
        widget = self.createWidget(parent, row, col)
        self.__all_widget[(row, col)] = widget
        return widget

    def _deleteWidget(self, parent, row, col):
        widget = self.__all_widget.pop((row, col), None)
        if widget is not None:
            try:
                self.deleteWidget(parent, widget)
                widget.deleteLater()
            except Exception:
                pass

    # 必须实现
    def createWidget(self, parent, row: int, col: int):
        """
        创建代理控件
        :param parent:父控件,一般是视图
        """
        raise NotImplementedError("请实现createWidget")

    def deleteWidget(self, parent, widget):
        """
        删除代理控件
        :param parent: 父控件,一般是视图
        """

    def setWidgetData(self, parent, widget, value):
        """
        设置代理控件的数据
        """
        raise NotImplementedError("请实现setEditorData")


class ListDelegateBase:
    """
    代理控件基类
    需要重写createWidget、deleteWidget、setWidgetData
    内部有私有方法用于管理创建的控件
    """

    def __init__(self, parent=None):
        self.__parent = parent
        self.__all_widget: list[QWidget] = []

    def _createWidget(self, parent, index) -> QWidget:
        widget = self.createWidget(parent, index)
        self.__all_widget.append(widget)
        return widget

    def _deleteWidget(self, parent, widget):
        try:
            self.deleteWidget(parent, widget)
            if widget in self.__all_widget:
                self.__all_widget.remove(widget)
            widget.deleteLater()
        except Exception as e:
            print(f'{self.__class__.__name__}.deleteWidget 错误:{e}')

    # 必须实现
    def createWidget(self, parent, index: int):
        """
        创建代理控件
        :param parent:父控件,一般是视图
        """
        raise NotImplementedError("请实现createWidget")

    def deleteWidget(self, parent, widget):
        """
        删除代理控件
        :param parent: 父控件,一般是视图
        """

    def deleteWidgetAll(self):
        """删除全部代理控件"""
        for widget in self.__all_widget.copy():
            try:
                widget.deleteLater()
            except RuntimeError:
                pass
        self.__all_widget.clear()

    def setWidgetData(self, parent, widget, value):
        """
        设置代理控件的数据
        """
        raise NotImplementedError("请实现setEditorData")


class TableWidgetBase(TableWidget):
    """
    二维视图基类不支持列数变化,列数反复变化可能出现意料之外的情况
    使用需要设置模型和代理
        设置模型:setTableData,模型必须是DataFrameModelBase或其子类
        设置代理:setDelegateColumn,如果不设置的话只单纯显示字符串
    视图只会加载可见范围内的数据
    setModel方法自动连接了模型数据变化的信号
    需要显示更新数据请使用updateUiLazy(延迟方法)或_updateUi(同步方法)
    """
    mouseRightClickedSignal = Signal(int, int, QPoint)  # 鼠标右击时发送row,col,以及点击时的坐标
    # scrollChangedSignal = Signal(list)  # 滚动条滚动时发送当前可见行
    scrollToTopSignal = Signal(object)  # 滚动到顶部

    def __init__(self, model: 'DataFrameModelBase' = None, parent=None):
        """
        :param model: 数据模型
        :param parent: 父控件
        """
        super().__init__(parent)
        self._model = model  # 模型
        self._parent = parent
        self._cellRatio = 32 / 40  # 单元格宽高比
        self._buffer_rows = 5  # 默认缓冲行,当前可见行上下5行
        self._fixed_row_height = None  # 固定行高
        self._fixed_columns_width: dict[int, int] = {}  # 列索引:列宽
        self._columns_min_width: dict[int, int] = {}  # 列索引:列宽
        self._columns_section_resize_mode = {}  # 列索引:列宽调整模式,默认为根据内容调整
        self._delegate_col: dict[int, DelegateBase] = {}  # 代理列
        self._display_row = set()  # 已显示的行
        self._scroll_single_step = 6  # 滚动条单步大小除数,默认6
        self.__enable_resize_rows_to_contents = False  # 是否自动调整行高
        self.__enable_resize_columns_to_contents = False  # 是否自动调整列宽
        # ui重绘定时器
        self.__update_ui_timer = debouncer_timer(self._updateUi)
        # 高度调整定时器
        self.__resizeRows_timer = debouncer_timer(self._resizeRowsToContents)
        # 列宽调整定时器
        self.__resizeColumns_timer = debouncer_timer(self._resizeColumnsToContents)
        # 加载代理控件定时器
        self.__load_delegate_timer = debouncer_timer(self._loadVisible)
        # 加载UI
        if model:
            self.setTableData(model)
        self.__uiInit()
        self.__bind()

    def __uiInit(self):
        self._enableResizeRowsToContents(True)
        self.enableResizeColumnsToContents(True)
        # self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)  # 固定值,用户无法调整
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)  # 固定值,用户无法调整
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # 禁止编辑
        self.verticalHeader().setVisible(True)  # 隐藏垂直表头即左侧表头
        self.horizontalHeader().setVisible(True)  # 隐藏水平表头即顶侧表头
        self.setAlternatingRowColors(True)  # 交替行变色

    def __bind(self):
        # 启用自定义上下文菜单（必须设置）
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # 连接右键菜单信号
        self.customContextMenuRequested.connect(self.mouseRightClicked)
        # 滚动条值改变信号触发加载代理控件(非代理控件会自动加载)
        self.verticalScrollBar().valueChanged.connect(self.loadVisibleLazy)
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
    def _loadVisible(self):
        """加载可见范围内的代理控件,删除不可见范围内的代理"""
        self._resizeColumnsToContents()
        self._resizeRowsToContents()
        rows = self.getVisibleRow()  # 获取当前可见行
        if not rows:
            return None
        # 计算缓冲后的最小和最大行
        if self._buffer_rows:
            min_row = max(0, min(rows) - self._buffer_rows)
            max_row = min(self.rowCount(), max(rows) + self._buffer_rows)
            rows = list(range(min_row, max_row))
        # 清理代理控件
        wait_del_row = self._display_row - set(rows)
        if wait_del_row:  # 清理不在可见范围的内容
            for row in wait_del_row:
                for col in range(self.columnCount()):
                    delegate = self._delegate_col.get(col, None)
                    if delegate:  # 是代理列
                        delegate._deleteWidget(self, row, col)
                        self.removeCellWidget(row, col)
                    else:  # 不是代理列
                        self.setItem(row, col, None)
                self._display_row.discard(row)
        # 加载控件
        if self._model is not None:
            for row in rows:
                for col in range(self.columnCount()):
                    delegate = self._delegate_col.get(col, None)
                    value = self._model.data(row, col, not bool(delegate))  # 代理列需要原始数据
                    if value is None:
                        continue
                    if delegate:  # 是代理列
                        self._useDelegateCreateWidget(row, col, value)
                    else:  # 不是代理列
                        self._useItemCreateWidget(row, col, value)
            self._display_row.update(rows)
        # 延迟更新UI,防止布局错位
        QTimer.singleShot(0, self._layoutChange)

    def loadVisibleLazy(self):
        """延迟加载可见行代理控件"""
        self.__load_delegate_timer.start(TIMEOUT)

    def _resizeColumnsToContents(self):
        """根据可见行内内容调整列宽"""
        if not self.__enable_resize_columns_to_contents:
            return None
        # 将未配置的列设置为Stretch
        for col in set(range(self.columnCount())) - set(self._columns_section_resize_mode.keys()):
            self.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
        # 列宽模式
        for col, mode in self._columns_section_resize_mode.items():
            # 根据内容调整
            if mode == QHeaderView.ResizeMode.ResizeToContents:
                self.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
                width = self._get_visible_column_min_width(col)
                self.setColumnWidth(col, width)
            # 固定值
            elif mode == QHeaderView.ResizeMode.Fixed:
                self.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
                width = self._fixed_columns_width[col]  # 获取固定值
                self.setColumnWidth(col, width)
            elif mode == QHeaderView.ResizeMode.Interactive:
                self.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
            else:
                self.horizontalHeader().setSectionResizeMode(col, mode)
            min_width = self._columns_min_width.get(col, 0)
            min_width = self._get_visible_column_min_width(col) if min_width is None else min_width
            if self.columnWidth(col) < min_width:  # 确保不小于最小尺寸
                self.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
                self.setColumnWidth(col, min_width)

    def resizeColumnsToContentsLazy(self):
        """延迟更新列宽"""
        self.__resizeColumns_timer.start(TIMEOUT)

    def _resizeRowsToContents(self):
        """实际执行高度调整函数"""
        if self.__enable_resize_rows_to_contents:
            # 计算行高
            if self._fixed_row_height is None:
                width = self.columnWidth(0)  # 获取当前列宽
                height = width / self._cellRatio  # 计算高度
                height = height if height < self.height() else self.height()
            else:
                height = self._fixed_row_height
            # 设置行高
            for index_row in range(self.rowCount()):
                self.setRowHeight(index_row, height)
            # 设置滚动条步进
            self.verticalScrollBar().setSingleStep(height // self._scroll_single_step)

    def resizeRowsToContentsLazy(self):
        """延迟更新行高"""
        self.__resizeRows_timer.start(TIMEOUT)

    def _layoutChange(self):
        self._resizeRowsToContents()
        self._resizeColumnsToContents()
        self.updateGeometry()
        self.updateGeometries()

    def _updateUi(self):
        # 触发数据更新
        self._loadVisible()
        # 触发布局更新
        self.updateGeometry()
        self.updateGeometries()
        self.viewport().update()

    def updateUiLazy(self):
        """延迟更新UI,数据刷新主要接口"""
        self.__update_ui_timer.start(TIMEOUT)

    def _modelLayoutChange(self, row_count=None, column_count=None):
        """模型行列数量改变"""
        row_count = row_count if row_count else self._model.rowCount()
        column_count = column_count if column_count else self._model.columnCount()
        self.setRowCount(row_count)
        self.setColumnCount(column_count)
        self.setColumnHeader(self._model.headerData())
        self._layoutChange()

    def _modelDataChange(self, row, col, value):
        """模型数据改变"""
        if row < 0 or row >= self.rowCount() or col < 0 or col >= self.columnCount():
            return
        visible_rows = self.getVisibleRow()
        if row in visible_rows:
            if col in self._delegate_col:
                delegate = self._delegate_col.get(col, None)
                if delegate:
                    self._useDelegateCreateWidget(row, col, value)
            else:
                self._useItemCreateWidget(row, col, value)

    def _modelDataRefresh(self):
        """模型数据刷新"""
        self._modelLayoutChange()
        self.updateUiLazy()

    def _useDelegateCreateWidget(self, row, col, value):
        """使用代理创建控件"""
        delegate = self._delegate_col.get(col, None)
        if delegate:
            widget = self.cellWidget(row, col)
            if widget is None:
                widget = delegate._createWidget(self, row, col)
                self.setCellWidget(row, col, widget)
            delegate.setWidgetData(self, widget, value)

    def _useItemCreateWidget(self, row, col, value):
        """使用item创建控件"""
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, col, item)

    def showEvent(self, event):
        self.updateUiLazy()
        super().showEvent(event)

    def resizeEvent(self, event):
        self.updateUiLazy()
        super().resizeEvent(event)

    # ---设置类方法---
    def _enableResizeRowsToContents(self, enabled: bool):
        self.__enable_resize_rows_to_contents = enabled

    def enableResizeColumnsToContents(self, enabled: bool):
        """
        设置列宽是否自动调整
        :param enabled: 是否自动调整列宽
        """
        self.__enable_resize_columns_to_contents = enabled

    def setScrollSmoothMode(self, mode=SmoothMode.LINEAR):
        """
        设置表格视图的滚动平滑模式

        :param mode: 滚动模式枚举值
            可选值（SmoothMode 枚举）：
            - NO_SMOOTH     无平滑滚动，直接跳转，性能最好，最跟手
            - CONSTANT      匀速滚动，速度恒定，感觉较机械
            - LINEAR        线性滚动，与 CONSTANT 类似，速度均匀
            - QUADRATI      二次方缓动，有加速/减速冲击感
            - COSINE        余弦缓动，平滑自然，视觉体验最佳（默认推荐）
        """
        self.scrollDelagate.verticalSmoothScroll.setSmoothMode(mode)
        if mode == SmoothMode.NO_SMOOTH:
            self.verticalScrollBar().setSingleStep(self.rowHeight(0) // 3)

    def setScrollSingleStep(self, step: int):
        """设置单步滚动除数,内部会自动计算每次滚动高度,使用行高除以当前值"""
        self._scroll_single_step = step

    def setFixedRowHeight(self, height: int):
        """
        设置固定行高,设置了固定行高后,自动调整行高函数将设置固定行高
        :param height:行高
        """
        self._fixed_row_height = height

    def setColumnSectionResizeMode(self, col=None, mode=QHeaderView.ResizeMode.Stretch, fixed_width: int = None):
        """
        设置列宽调整模式
        :param col:列索引,默认设置全部
        :param mode:模式,可选值QHeaderView.Stretch:填充剩余空间,默认
                             QHeaderView.ResizeToContents:根据内容调整
                             QHeaderView.Fixed:固定值,用户无法调整
                             QHeaderView.Interactive:固定值,用户允许调整
        :param fixed_width:固定列宽值
        """
        # 处理固定列宽
        if mode == QHeaderView.Fixed or mode == QHeaderView.Interactive:
            if mode == QHeaderView.Fixed and fixed_width is None:
                raise ValueError("请设置固定列宽值")
            if col is None:
                for col in range(self.columnCount()):
                    self._columns_section_resize_mode[col] = mode
                    if fixed_width is not None:
                        self._fixed_columns_width[col] = fixed_width
            else:
                if col < 0 or col > self.columnCount() - 1:
                    raise ValueError("列索引超出范围")
                self._columns_section_resize_mode[col] = mode
                if fixed_width is not None:
                    self._fixed_columns_width[col] = fixed_width
        # 处理其它模式
        if col is None:
            for col in range(self.columnCount()):
                self._columns_section_resize_mode[col] = mode
        else:
            if col < 0 or col > self.columnCount() - 1:
                raise ValueError("列索引超出范围")
            self._columns_section_resize_mode[col] = mode
        self.resizeColumnsToContentsLazy()

    def setColumnMinimumWidth(self, col, min_width=None):
        """
        设置某些列的最小宽度,不受缩放模式影响
        :param min_width: 为None时最终调整宽度时将实时计算当前可见范围内的最小列宽
        """
        self._columns_min_width[col] = min_width

    def setDelegateColumn(self, column_index: int, delegate: DelegateBase):
        """
        设置指定列的代理控件
        :param column_index:列序号
        :param delegate:代理类
        """
        if isinstance(delegate, DelegateBase):
            self._delegate_col[column_index] = delegate

    def setColumnHeader(self, header: list):
        """设置列头"""
        self.setColumnCount(len(header))
        self.setHorizontalHeaderLabels(header)

    def setTableData(self, model: DataFrameModelBase):
        if isinstance(model, DataFrameModelBase):
            self._model = model
            self.setColumnHeader(model.headerData())
            model.layoutChanged.connect(self._modelLayoutChange)
            model.dataChange.connect(self._modelDataChange)
            model.dataRefresh.connect(self._modelDataRefresh)
            # 首次显示数据
            self._modelLayoutChange()
            self.updateUiLazy()

    def setBufferRows(self, buffer_rows):
        """设置缓冲行数量"""
        self._buffer_rows = buffer_rows

    # ---获取类方法---
    def rowCount(self):
        return self._model.rowCount()

    def columnCount(self):
        return self._model.columnCount()

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
        start_row = max(0, scroll_pos // row_height if row_height != 0 else 0)
        end_row = min(total_rows - 1, (scroll_pos + viewport_height) // row_height if row_height != 0 else 0)
        visible_rows = list(range(start_row, end_row + 1))
        return visible_rows

    def getModel(self) -> DataFrameModelBase:
        return self._model

    # ---辅助方法---
    def _calculate_text_width(self, text: str) -> int:
        """计算文本宽度"""
        # 考虑单元格内边距
        font = self.font()
        metrics = QFontMetrics(font)
        return metrics.horizontalAdvance(str(text)) + 10

    def _get_visible_column_min_width(self, col, buffer_width=30) -> int:
        """计算可见范围内某列的最小宽度"""
        visible_rows = self.getVisibleRow()
        # 获取列宽内容需要的大小
        try:
            header_data = self._model.headerData()[col].split("\n")
        except IndexError:
            return 0
        max_width = max([self._calculate_text_width(text) for text in header_data])
        for row in visible_rows:
            text = self._model.data(row, col)
            if text:  # 获取可见范围内最大列宽
                width = self._calculate_text_width(text) + buffer_width
                if width > max_width:
                    max_width = width
        return max_width

    def scrollToTopSlot(self, value):
        raise NotImplementedError("请实现scrollToTopSlot方法")


class ListWidgetBase(TableWidgetBase):
    """
    用于将一行pandas数据展示为一个单元格数据,
    支持启用自适应列数,无论几列,数据永远算是一维数据,即每次返回一行数据
    """

    def __init__(self, model: 'DataFrameListBase' = None, parent=None):
        self._enable_columns_to_contents = False
        self._delegate: ListDelegateBase = None
        self._model: DataFrameListBase = None
        super().__init__(model, parent)

    def enableColumnsCountToContents(self, enable: bool, min_width: int = 200, max_width: int = 300):
        """启用根据表格大小调整列数"""
        self._enable_columns_to_contents = enable
        self.min_columns_width = min_width
        self.max_columns_width = max_width

    def _resizeColumnsCountToContents(self):
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
                self.setRowCount(self.rowCount())
                self._layoutChange()  # 刷新布局

    def _loadVisible(self):
        # 计算布局
        self._resizeColumnsCountToContents()
        self._resizeRowsToContents()

        rows = self.getVisibleRow()  # 获取当前可见行
        if not rows:
            return None
        # 计算缓冲后的最小和最大行
        if self._buffer_rows:
            min_row = max(0, min(rows) - self._buffer_rows)
            max_row = min(self.rowCount(), max(rows) + self._buffer_rows)
            rows = list(range(min_row, max_row))
        # 清理代理控件
        wait_del_row = self._display_row - set(rows)
        if wait_del_row:  # 清理不在可见范围的内容
            for row in wait_del_row:
                for col in range(self.columnCount()):
                    if self._delegate is not None:  # 是代理列
                        widget = self.cellWidget(row, col)
                        if widget is not None:
                            self._delegate._deleteWidget(self, widget)
                            self.removeCellWidget(row, col)
                    else:  # 不是代理列
                        self.setItem(row, col, None)
                self._display_row.discard(row)
        # 加载控件
        column_count = self.columnCount()
        if self._model is not None:
            for row in rows:
                for col in range(column_count):
                    index = row * column_count + col
                    value = self._model.data(index)  # 代理列需要原始数据
                    if value is None:
                        continue
                    if self._delegate:  # 是代理列
                        self._useDelegateCreateWidget(row, col, value)
                    else:  # 不是代理列
                        self._useItemCreateWidget(row, col, value)
            self._display_row.update(rows)
        # 延迟更新UI,防止布局错位
        QTimer.singleShot(0, self._layoutChange)

    def _modelDataChange(self, row, col, value):
        """模型数据改变"""
        if row < 0 or row >= self.rowCount() or col < 0 or col >= self.columnCount():
            return
        visible_rows = self.getVisibleRow()
        if row in visible_rows:
            if self._delegate is not None:
                self._useDelegateCreateWidget(row, col, value)
            else:
                self._useItemCreateWidget(row, col, value)

    def _useDelegateCreateWidget(self, row, col, value):
        """使用代理创建控件"""
        if self._delegate is not None:
            widget = self.cellWidget(row, col)
            if widget is None:
                widget = self._delegate._createWidget(self, row * self.columnCount() + col)
                self.setCellWidget(row, col, widget)
            self._delegate.setWidgetData(self, widget, value)

    def setDelegateColumn(self, delegate: ListDelegateBase):
        self._delegate = delegate

    def rowCount(self):
        row_count = self._model.rowCount()
        return int(-(-row_count // self.columnCount()))  # 向上取整

    def columnCount(self):
        return super(TableWidgetBase, self).columnCount()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    from TableData import DataFrameModelBase
    from SubAPI.DataManage import KEY_WORD
    from Fun.QtWidget import MainWidget

    KEY_WORD.is_loaded(0)
    app = QApplication([])
    table_view = TableWidgetBase()
    table_view.setFixedRowHeight(80)
    with KEY_WORD as df:
        data = df.copy(deep=True)
    table_view.setTableData(DataFrameModelBase(data))
    table_view.show()
    MainWidget.change_theme()
    app.exec()
