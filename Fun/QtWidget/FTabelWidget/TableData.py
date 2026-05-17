"""二维模型"""
import pandas as pd
from threading import RLock
from PySide6.QtCore import Qt, Signal, QObject


class TableModelBase(QObject):
    """二维模型基类"""
    dataRefresh = Signal()  # 数据刷新信号
    dataChange = Signal(int, int, object)  # 数据改变信号, 参数为行索引，列索引，数据
    layoutChanged = Signal(int, int)  # 布局改变信号, 参数为行数,列数
    dataIndexError = Signal(int, int)  # 数据索引错误信号 参数为行索引，列索引

    def __init__(self, parent=None):
        super().__init__(parent)
        self._lock = RLock()
        self._row_count = None
        self._column_count = None
        self._dataframe = None

    # ---必须实现的方法---
    def rowCount(self):
        if self._row_count is not None:
            return self._row_count
        return 0

    def columnCount(self):
        if self._column_count is not None:
            return self._column_count
        return 0

    def data(self, row, col) -> str | None:
        """
        获取单元格数据
        :param row:行索引
        :param col:列索引
        """
        raise NotImplementedError('请实现data方法')

    # 可选实现

    def setCellData(self, row, col, value) -> bool:
        """
        设置单元格数据
        :param row:行索引
        :param col:列索引
        :param value:值
        """
        raise NotImplementedError('请实现setCellData方法')

    def headerData(self, orientation=Qt.Orientation.Horizontal) -> list[str]:
        """
        获取表头数据
        :param orientation:列头Qt.Orientation.Horizontal/行头Qt.Orientation.Vertical
        :return 无数据时返回空列表
        """
        raise NotImplementedError('请实现headerData方法')

    # ---功能性方法---
    def refreshData(self):
        """刷新数据"""

    def setDataFrame(self, dataframe, emit=True):
        """设置数据源"""
        with self._lock:
            self._dataframe = dataframe
        if emit:
            self.dataRefresh.emit()

    def setColumnCount(self, column_count: int, emit=True):
        """设置虚拟列数（不改变实际数据）"""
        self._column_count = column_count
        if emit:
            self.layoutChanged.emit(self.rowCount(), self.columnCount())

    def setRowCount(self, row_count: int, emit=True):
        """设置虚拟行数（不改变实际数据）"""
        self._row_count = row_count
        if emit:
            self.layoutChanged.emit(self.rowCount(), self.columnCount())

    @property
    def Lock(self) -> RLock:
        return self._lock

    def __enter__(self):
        """进入上下文管理器，自动加锁并返回数据"""
        self._lock.acquire()
        return self._dataframe

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器，自动释放锁"""
        self._lock.release()
        return False  # 不抑制异常


class DataFrameModelBase(TableModelBase):
    """
    Pandas DataFrame 数据模型基类
    需要插入某列用于记录代理状态继承重写
    data.insert(0, '选择', False) or data.insert(0, '选择', self._dataframe['选择'].copy(deep=True))
    """

    def __init__(self, dataframe: pd.DataFrame = None, display_dtype=False, parent=None):
        super().__init__(parent)
        self.display_dtype = display_dtype  # 列头是否显示数据类型
        self._dataframe = dataframe if dataframe is not None else pd.DataFrame()

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

    # ---必须实现的方法---
    def rowCount(self):
        if self._row_count is not None:
            return self._row_count
        with self._lock:
            return len(self._dataframe)

    def columnCount(self):
        if self._column_count is not None:
            return self._column_count
        with self._lock:
            return len(self._dataframe.columns)

    def data(self, row, col, dtype_format=True) -> str | None:
        """
        获取单元格数据
        :param row:行索引
        :param col:列索引
        :param dtype_format:将不同格式转为str类型,默认启用,否则返回原始数据
        """
        with self._lock:
            if row < 0 or row >= self.rowCount() or col < 0 or col >= self.columnCount():
                self.dataIndexError.emit(row, col)
                return None
            try:
                value = self._dataframe.iloc[row, col]
            except IndexError:
                self.dataIndexError.emit(row, col)
                return None
            # 处理NaN值
            if pd.isna(value):
                return ""
            # 有效数据处理
            col_name = self._dataframe.columns[col]
            dtype = str(self._dataframe[col_name].dtype)
            if dtype_format and dtype in self._formatters:
                return self._formatters[dtype](value)
            else:
                return value

    # 可选实现
    def setCellData(self, row, col, value, emit=True) -> bool:
        """
        设置单元格数据
        :param row:行索引
        :param col:列索引
        :param value:值
        :param emit:是否发送信号
        """
        with self._lock:
            if row < 0 or row >= len(self._dataframe) or col < 0 or col >= len(self._dataframe.columns):
                return False
            try:
                # 更新DataFrame中的数据
                self._dataframe.iloc[row, col] = value
                # 发射信号通知视图刷新
                if emit:
                    self.dataChange.emit(row, col, value)
                return True
            except Exception as e:
                print(f"{self.__class__.__name__}.setData 错误: {e}")
                return False

    def headerData(self, orientation=Qt.Orientation.Horizontal) -> list[str]:
        """
        获取表头数据
        :param orientation:列头Qt.Orientation.Horizontal/行头Qt.Orientation.Vertical
        :return 无数据时返回空列表
        """
        header_data = []
        if orientation == Qt.Orientation.Horizontal:
            with self._lock:
                columns = self._dataframe.columns.copy()
            for col, col_name in enumerate(columns):
                if col_name:
                    if self.display_dtype:
                        dtype = self._dataframe[col_name].dtype
                        header_data.append(f"{col_name}\n({dtype})")
                    else:
                        header_data.append(col_name)
                else:
                    header_data.append(f"列{col_name + col}")
        elif orientation == Qt.Orientation.Vertical:
            pass
        return header_data

    def getRowData(self, row_index) -> pd.Series | None:
        """获取一整行数据"""
        with self._lock:
            try:
                return self._dataframe.iloc[row_index]
            except IndexError:
                return None

    def getDataFrame(self) -> pd.DataFrame:
        """获取数据源"""
        with self._lock:
            return self._dataframe.copy(deep=True)

    def clearData(self):
        with self._lock:
            self.setDataFrame(pd.DataFrame())


class DataFrameListBase(DataFrameModelBase):
    """
    将二维模型转为一维模型使用,
    必须设置列数,否则默认为一列,
    行数会自动计算
    """

    def __init__(self, dataframe: pd.DataFrame = None, display_dtype=False, parent=None):
        super().__init__(dataframe, display_dtype, parent)
        self.setColumnCount(1)

    def data(self, index) -> str | None:
        """
        获取单元格数据
        :param index:一维索引
        :return 返回原始数据
        """
        with self._lock:
            try:
                value = self._dataframe.iloc[index]
                return value
            except IndexError:
                self.dataIndexError.emit(index, 1)
                return None

    def setRowData(self, index, value: pd.Series, emit=True) -> bool:
        """
        设置一整行数据
        :param index:索引
        :param value:值
        :param emit:是否发送信号
        """
        with self._lock:
            try:
                # 更新DataFrame中的数据
                self._dataframe.iloc[index] = value
                # 发射信号通知视图刷新
                if emit:
                    self.dataRefresh.emit()
                return True
            except Exception as e:
                print(f"{self.__class__.__name__}.setRowData 错误: {e}")
                return False

    def headerData(self, orientation=Qt.Orientation.Horizontal) -> list[str]:
        """
        获取表头数据
        :param orientation:列头Qt.Orientation.Horizontal/行头Qt.Orientation.Vertical
        :return 无数据时返回空列表
        """
        header_data = []
        if orientation == Qt.Orientation.Horizontal:
            for col in range(self.columnCount()):
                header_data.append(f"列{col}")
        elif orientation == Qt.Orientation.Vertical:
            pass
        return header_data
