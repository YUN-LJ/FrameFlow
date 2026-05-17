"""二维模型"""
import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QColor


class DataFrameModelBase(QAbstractTableModel):
    """
    Pandas DataFrame 数据模型基类

    继承自 QAbstractTableModel，用于将 pandas.DataFrame 适配到 Qt 的 Model/View 架构。

    ========== 核心信号（继承自 QAbstractItemModel） ==========

    1. dataChanged(topLeft: QModelIndex, bottomRight: QModelIndex, roles: list = [])
        - 发射时机: 当现有单元格数据发生变化时，由 setData() 或自定义更新方法手动发射
        - 作用: 通知视图刷新指定范围内的单元格显示
        - 示例: self.dataChanged.emit(top_left, bottom_right)
        - 注意: 参数 roles 通常传空列表即可，表示所有角色都需刷新

    2. layoutChanged()
        - 发射时机: 当模型的数据结构发生重大变化（如排序、过滤、完全重置）时手动发射
        - 作用: 通知视图整个布局需要重新计算（开销较大，谨慎使用）
        - 示例: self.layoutChanged.emit()
        - 注意: 优先使用 dataChanged 进行细粒度更新，避免频繁调用此信号

    3. headerDataChanged(orientation: Qt.Orientation, first: int, last: int)
        - 发射时机: 当表头数据（列标题或行标题）发生变化时手动发射
        - 作用: 通知视图刷新表头显示
        - 示例: self.headerDataChanged.emit(Qt.Horizontal, 0, 2)
        - 参数: orientation 指定水平（列）或垂直（行）表头

    4. rowsInserted(parent: QModelIndex, first: int, last: int)
        - 发射时机: 在调用 beginInsertRows() / endInsertRows() 后自动发射
        - 作用: 通知视图有新行插入
        - 注意: 不需要手动发射，由 beginInsertRows/endInsertRows 自动处理

    5. rowsAboutToBeRemoved(parent: QModelIndex, first: int, last: int)
        - 发射时机: 在调用 beginRemoveRows() / endRemoveRows() 后自动发射
        - 作用: 通知视图行即将被删除
        - 注意: 不需要手动发射，由 beginRemoveRows/endRemoveRows 自动处理

    6. columnsInserted() / columnsAboutToBeRemoved()
        - 同理 row 相关信号，用于处理列的增加和删除
        - 由 beginInsertColumns/endInsertColumns 等函数自动处理

    7. modelAboutToBeReset()
        - 发射时机: 调用 beginResetModel() 时自动发射
        - 作用: 通知视图模型即将全部重置

    8. modelReset()
        - 发射时机: 调用 endResetModel() 时自动发射
        - 作用: 通知视图模型已全部重置，需要完全重新加载

    ========== 典型使用场景 ==========

    场景1 - 更新单个单元格数据:
        def setData(self, index, value, role=Qt.EditRole):
            if role == Qt.EditRole:
                self._dataframe.iloc[index.row(), index.column()] = value
                # 发射信号通知视图刷新
                self.dataChanged.emit(index, index)
                return True
            return False

    场景2 - 更新整行数据:
        def updateRow(self, row, new_row_data):
            self._dataframe.iloc[row] = new_row_data
            left = self.index(row, 0)
            right = self.index(row, self.columnCount() - 1)
            self.dataChanged.emit(left, right)

    场景3 - 插入新行:
        def insertRow(self, row, data):
            self.beginInsertRows(QModelIndex(), row, row)
            self._dataframe = pd.concat([
                self._dataframe.iloc[:row],
                pd.DataFrame([data], columns=self._dataframe.columns),
                self._dataframe.iloc[row:]
            ]).reset_index(drop=True)
            self.endInsertRows()  # 自动发射 rowsInserted 信号

    场景4 - 删除行:
        def removeRow(self, row):
            self.beginRemoveRows(QModelIndex(), row, row)
            self._dataframe = self._dataframe.drop(row).reset_index(drop=True)
            self.endRemoveRows()  # 自动发射 rowsAboutToBeRemoved 信号

    场景5 - 排序（触发布局变化）:
        def sort(self, column, order=Qt.AscendingOrder):
            self.layoutAboutToBeChanged.emit()  # 可选，在排序前发射
            col_name = self._dataframe.columns[column]
            self._dataframe = self._dataframe.sort_values(
                by=col_name,
                ascending=(order == Qt.AscendingOrder)
            )
            self.layoutChanged.emit()  # 通知视图布局已变

    场景6 - 完全重置数据:
        def resetDataframe(self, new_dataframe):
            self.beginResetModel()
            self._dataframe = new_dataframe
            self.endResetModel()  # 自动发射 modelReset 信号

    ========== 最佳实践 ==========

    1. 优先使用 dataChanged 进行细粒度更新，避免频繁调用 layoutChanged
    2. 插入/删除行/列时必须使用 begin/end 函数，确保信号正确发射
    3. 批量更新数据时，可以使用 beginResetModel/endResetModel 一次性更新
    4. 更新表头后记得调用 headerDataChanged

    ========== 继承关系 ==========

    QObject → QAbstractItemModel → QAbstractTableModel → DataFrameModelBase
    """

    def __init__(self, dataframe: pd.DataFrame = None, display_dtype=False, parent=None):
        super().__init__(parent)
        self._row_count = None
        self._column_count = None
        self.display_dtype = display_dtype  # 列头是否显示数据类型
        self._dataframe = dataframe if dataframe is not None else pd.DataFrame()
        self._delegate_columns: set[int] = set()  # 记录委托列

        # 数据类型格式化器
        self._formatters = {
            'float64': lambda x: f'{x:.2f}' if pd.notna(x) else '',
            'float32': lambda x: f'{x:.2f}' if pd.notna(x) else '',
            'int64': lambda x: f'{x:,}' if pd.notna(x) else '',
            'int32': lambda x: f'{x:,}' if pd.notna(x) else '',
            'uint64': lambda x: f'{x:,}' if pd.notna(x) else '',
            'uint32': lambda x: f'{x:,}' if pd.notna(x) else '',
            'datetime64[ns]': lambda x: x.strftime('%Y-%m-%d %H:%M') if pd.notna(x) else '',
            'object': lambda x: str(x)[:50] if pd.notna(x) else '',
            'bool': lambda x: '✓' if x else '✗'
        }

        self._color_mapping = None

    # ---必须实现的方法---
    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        if self._row_count is not None:
            return self._row_count
        return len(self._dataframe)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        if self._column_count is not None:
            return self._column_count
        return len(self._dataframe.columns)

    def data(self, index, role=Qt.DisplayRole):
        """
        获取单元格数据
        :param index:索引,包含了行列信息
        :param role:角色
        """
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if row < 0 or row >= len(self._dataframe):
            return None

        try:
            value = self._dataframe.iloc[row, col]
        except IndexError:
            return None

        is_delegate_column = col in self._delegate_columns
        # 委托列的所有显示相关角色都返回空
        if is_delegate_column:
            if role == Qt.UserRole:  # 委托列通过 UserRole 传递真实数据给委托
                return value
            elif role in (Qt.DisplayRole, Qt.EditRole):
                return ""  # 不显示文本
            elif role == Qt.ToolTipRole:
                return None  # 不需要工具提示

        # 处理NaN值
        if pd.isna(value):
            if role == Qt.DisplayRole:
                return ""
            return None

        # 非委托列的正常处理
        if role == Qt.DisplayRole:
            col_name = self._dataframe.columns[col]
            dtype = str(self._dataframe[col_name].dtype)

            if dtype in self._formatters:
                return self._formatters[dtype](value)
            else:
                return str(value)
        elif role == Qt.TextAlignmentRole:
            col_name = self._dataframe.columns[col]
            dtype = str(self._dataframe[col_name].dtype)
            return Qt.AlignmentFlag.AlignCenter
        elif role == Qt.ToolTipRole:
            col_name = self._dataframe.columns[col]
            dtype = str(self._dataframe[col_name].dtype)
            if dtype == 'object' and len(str(value)) > 50:
                return f"完整内容:\n{value}"
            return f"{col_name}: {value}"
        elif role == Qt.BackgroundRole:
            if self._color_mapping:
                col_name = self._dataframe.columns[col]
                if col_name in self._color_mapping:
                    color_func = self._color_mapping[col_name]
                    color = color_func(value)
                    if color:
                        return QColor(color)

        return None

    def setCellData(self, index, value, role=Qt.EditRole):
        """
        设置单元格数据
        :param index:索引,包含了行列信息
        :param value:值
        :param role:角色
        """
        if not index.isValid():
            return False

        row = index.row()
        col = index.column()

        if row < 0 or row >= len(self._dataframe) or col < 0 or col >= len(self._dataframe.columns):
            return False

        if role == Qt.EditRole:
            try:
                # 更新DataFrame中的数据
                self._dataframe.iloc[row, col] = value
                # 发射信号通知视图刷新
                self.dataChanged.emit(index, index, [role])
                return True
            except Exception as e:
                print(f"{self.__class__.__name__}.setData 错误: {e}")
                return False
        return False

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            if section < len(self._dataframe.columns):
                col_name = self._dataframe.columns[section]
                if self.display_dtype:
                    dtype = self._dataframe[col_name].dtype
                    return f"{col_name}\n({dtype})"
                return str(col_name)
            return f"列{section + 1}"
        else:
            if section < len(self._dataframe):
                index_val = self._dataframe.index[section]
                return str(index_val)
            return f"{section + 1}"

    def flags(self, index):
        """重写 flags 方法"""
        if index.column() in self._delegate_columns:
            # 委托列：只启用，不可编辑（委托接管显示）
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return super().flags(index)

    # ---功能性方法---
    def refreshData(self):
        """刷新数据"""
        self.beginResetModel()
        self.endResetModel()

    def setDelegateColumn(self, col):
        """设置使用委托的列"""
        self._delegate_columns.add(col)

    def getDelegateColumn(self) -> set:
        """获取使用委托的列"""
        return self._delegate_columns.copy()

    def setDataFrame(self, dataframe: pd.DataFrame):
        self.beginResetModel()
        self._dataframe = dataframe
        self.endResetModel()

    def setColumnCount(self, column_count: int):
        """设置虚拟列数（不改变实际数据）"""
        self._column_count = column_count
        self.layoutChanged.emit()

    def setRowCount(self, row_count: int):
        """设置虚拟行数（不改变实际数据）"""
        self._row_count = row_count
        self.layoutChanged.emit()

    def updateHeader(self, orientation=Qt.Horizontal, first=0, last=None):
        """更新表头，发射headerDataChanged信号"""
        if last is None:
            if orientation == Qt.Horizontal:
                last = self.columnCount() - 1
            else:
                last = self.rowCount() - 1
        self.headerDataChanged.emit(orientation, first, last)
