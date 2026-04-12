"""模板化部件"""
import threading
# PySide6原生组件
from PySide6.QtCore import Signal, Qt, QTimer, QObject, QPoint
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QTableWidgetItem,
                               QGroupBox, QHeaderView, QStackedWidget, QTableWidget,
                               QAbstractItemView, QWidget, QSizePolicy)
# 风格化组件
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets.components.widgets import (
    TableWidget, CheckBox, TitleLabel, IndeterminateProgressRing,
    ProgressRing, PrimaryToolButton
)
from qfluentwidgets.components.dialog_box import MessageBoxBase
from qfluentwidgets.components.navigation import Pivot, SegmentedWidget
# 自定义组件
from Fun.QtWidget.FWidget import ImageWidget
from Fun.BaseTools.Image import ImageLoad
from typing import Callable
from BaseClass.TaskManage import TaskManage
from SubAPI import WallHaven as WH


class TopWidget(QWidget):
    """顶端标签导航"""
    isSegmented = True

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__parent = parent
        # 可选Pivot/SegmentedWidget
        self.topWidget = SegmentedWidget(self) if self.__class__.isSegmented else Pivot(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)
        # 连接信号
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)

        self.vBoxLayout.setContentsMargins(30, 0, 30, 30)
        self.vBoxLayout.addWidget(self.topWidget, 0, Qt.AlignHCenter)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.resize(400, 400)

    def addSubInterface(self, widget: QWidget, objectName: str, text: str):
        """添加子界面"""
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        # 使用全局唯一的 objectName 作为路由键
        self.topWidget.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def onCurrentIndexChanged(self, index):
        """界面切换时触发"""
        widget = self.stackedWidget.widget(index)
        self.topWidget.setCurrentItem(widget.objectName())


class GroupBoxCellBase(QGroupBox):
    """带选择控件的单元格组件"""
    StateChange = Signal(bool)  # 内部的checkBox状态改变时

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, parent=parent, **kwargs)
        self.__parent = parent  # 父对象
        self.layout = QVBoxLayout(self)
        self.layout_title = QHBoxLayout(self)
        self.checkBox = CheckBox(self)
        self.args = args  # 外部使用时可用来存一些变量
        self.kwargs = kwargs
        self.uiInit()
        self.bind()

    def uiInit(self):
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout_title.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout_title.setSpacing(0)
        self.layout.addLayout(self.layout_title)
        self.layout_title.addWidget(self.checkBox)

    def bind(self):
        self.checkBox.stateChanged.connect(self.StateChange.emit)

    def getState(self) -> bool:
        return self.checkBox.isChecked()

    def getText(self) -> str:
        return self.checkBox.text()

    def setText(self, text: str):
        self.checkBox.setText(text)

    def setState(self, state: bool):
        self.checkBox.setChecked(state)

    def addWidget(self, widget):
        self.layout_title.addWidget(widget)

    def setColor(self, color: str):
        self.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {color};
                border-radius: 5px;
                margin-top: 3px;
                font-size: 12px;
                }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: {color};
                }}
                """)


class GroupBoxCell(GroupBoxCellBase):
    """带图片显示的单元格组件"""

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent=None, *args, **kwargs)
        self.__parent = parent  # 父对象
        # 主要用于反馈当前图像加载状况
        self.image = None  # 当前显示的图像
        self.thumb_url = None  # 略缩图网址
        self.image_url = None  # 图像图网址
        self.image_loading = False  # 图像是否正在加载
        self.image_widget = ImageWidget(parent=self)
        self.layout.addWidget(self.image_widget)

    def setImage(self, image):
        self.image_widget.set_image(ImageLoad(image))
        self.image = image

    def setImageText(self, text: str):
        self.image_widget.set_text(text)

    def clearImage(self):
        self.image = None  # 当前显示的图像
        self.thumb_url = None  # 略缩图网址
        self.image_url = None  # 图像图网址
        self.image_widget.set_image(self.image_widget.default_image_load)


class ProgressRingButton(PrimaryToolButton):
    """带进度显示的按钮"""

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, parent=parent, **kwargs)
        self.__progressRing = ProgressRing(parent=self)
        self.uiInit()

    def uiInit(self):
        self.__progressRing.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.__progressRing.setStrokeWidth(2)

        # 让进度环覆盖在按钮上
        self.__progressRing.raise_()

    def setMinimum(self, value):
        self.__progressRing.setMinimum(value)

    def setMaximum(self, value):
        self.__progressRing.setMaximum(value)

    def setValue(self, value):
        self.__progressRing.setValue(value)

    def value(self):
        return self.__progressRing.value()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # 进度环居中，大小为按钮的0.8
        btn_size = self.size()
        radius = min(int(btn_size.width() * 0.8), int(btn_size.height() * 0.8))
        self.__progressRing.setFixedSize(radius, radius)

        # 居中
        x = (btn_size.width() - radius) // 2
        y = (btn_size.height() - radius) // 2
        self.__progressRing.move(x, y)


class GroupBoxTable(TableWidget):
    """用于容纳GroupBoxCell的表格"""
    mouseRightClickedSignal = Signal(int, int, QPoint)  # 鼠标右击时发送row,col,以及点击时的坐标
    delWidgetSignal = Signal(QWidget)  # 有部件被删除时的信号
    addWidgetSignal = Signal(QWidget)  # 有部件新增时的信号
    realignSignal = Signal(bool)  # 单元格重新排布时的信号
    visibleRowsSignal = Signal(list)  # 滚动条滚动时发送当前可见行

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, parent=parent, **kwargs)
        self.__parent = parent
        self.__widget_dict = {}  # 存储了每个QWidget类的创建函数
        self.enable_adaptive_row_height = True
        self.cellRatio = 3 / 4  # 单元格宽高比
        # 启用自定义上下文菜单（必须设置）
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # 连接右键菜单信号
        self.customContextMenuRequested.connect(self.mouseRightClicked)
        self.uiInit()

    def uiInit(self):
        self.setColumnCount(4)  # 设置列数
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应列宽
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
        self.verticalHeader().setVisible(False)  # 隐藏垂直表头即左侧表头
        self.horizontalHeader().setVisible(False)  # 隐藏水平表头即顶侧表头
        self.setAlternatingRowColors(True)  # 交替行变色

    def mouseRightClicked(self, position):
        """显示右键菜单"""
        # 获取点击的坐标
        pos = self.viewport().mapFromGlobal(self.mapToGlobal(position))
        # 方法1：获取点击位置的行和列
        index = self.indexAt(pos)
        if index.isValid():
            self.mouseRightClickedSignal.emit(index.row(), index.column(), self.mapToGlobal(position))

    def enableRowVisibleCheck(self, value: bool = True):
        """启用可见行检查定时器"""

        def sub_func():
            self.scroll_check_timer.start(300)

        if value:
            # 使用定时器实现防止滚动条快速滚动而频繁触发信号
            self.scroll_check_timer = QTimer()
            self.scroll_check_timer.setSingleShot(True)  # 单次触发
            self.scroll_check_timer.timeout.connect(self.getShowRowSignal)
            self.verticalScrollBar().valueChanged.connect(sub_func)
        else:
            self.verticalScrollBar().valueChanged.disconnect(sub_func)

    def getEmptyCoord(self, start_row: int = None, start_col: int = None, height=100, create=True) -> tuple[int, int]:
        """
        获取首个非空单元格的坐标
        :param start_row: 从哪一行开始,默认从首行
        :param start_col: 从那一列开始,默认从首列
        :param create: 如果当前表格内无非空单元格是否允许创建新的行,默认允许
        """
        start_row = 0 if start_row is None else start_row
        start_col = 0 if start_col is None else start_col
        max_row = self.rowCount()
        max_col = self.columnCount()
        for cur_row in range(start_row, max_row):
            for cur_col in range(start_col, max_col):
                if self.cellWidget(cur_row, cur_col) is None:
                    return cur_row, cur_col
        self.insertRow(max_row)
        self.setRowHeight(max_row, height)
        return max_row, 0

    def getWidgetCoord(self, widget: QWidget, column_index: int | list = None):
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

    def getShowRowSignal(self, emit=True) -> list:
        """
        获取当前显示的行（精确版本，考虑部分可见的行）

        Returns:
            dict: 包含可见行信息的字典
        """
        # 获取基本信息
        scroll_pos = self.verticalScrollBar().value()  # 滚动条位置（像素）
        viewport_height = self.viewport().height()  # 视口高度
        total_rows = self.rowCount()  # 总行数
        if total_rows == 0:
            self.visibleRowsSignal.emit([])
            return []
        row_height = self.rowHeight(0)  # 行高
        # 计算完全可见和部分可见的行
        fully_visible_rows = []
        partially_visible_rows = []
        for row in range(total_rows):
            # 获取该行的垂直位置（相对于表格顶部）
            row_top = row * row_height
            row_bottom = row_top + row_height
            # 检查是否在视口内
            if row_bottom > scroll_pos and row_top < scroll_pos + viewport_height:
                # 判断是否完全可见
                if row_top >= scroll_pos and row_bottom <= scroll_pos + viewport_height:
                    fully_visible_rows.append(row)
                else:
                    partially_visible_rows.append(row)
        # 所有可见的行
        all_visible_rows = fully_visible_rows + partially_visible_rows
        all_visible_rows.sort()
        # 计算可见比例（可选）
        visible_info = {
            'fully_visible': fully_visible_rows,
            'partially_visible': partially_visible_rows,
            'all_visible': all_visible_rows,
            'first_visible': all_visible_rows[0] if all_visible_rows else -1,
            'last_visible': all_visible_rows[-1] if all_visible_rows else -1,
            'count': len(all_visible_rows),
            'fully_count': len(fully_visible_rows),
            'scroll_pos': scroll_pos,
            'viewport_height': viewport_height
        }
        if emit:
            # 发射信号（可以根据需要选择发射哪种格式）
            self.visibleRowsSignal.emit(all_visible_rows)  # 只发射行号列表
            # self.visibleRowsSignal.emit(visible_info)  # 或者发射详细信息

        return all_visible_rows

    def setColumnHeader(self, header: list):
        """设置列头"""
        self.setColumnCount(len(header))
        self.horizontalHeader().setVisible(True)
        self.setHorizontalHeaderLabels(header)

    def addWidget(self, create_func: Callable, height=100, emit=True) -> QWidget:
        """
        添加一个QWidget子类
        :param create_func:创建这个部件的函数,用于表格内位置调整,返回值必须为QWidget子类
        :param height:行高
        :param emit:是否发射信号
        """
        # 获取当前非空单元格位置,如果当前没有非空单元格则创建新的行
        target_row, target_col = self.getEmptyCoord(height=height)
        widget = create_func()
        self.setCellWidget(target_row, target_col, widget)
        self.__widget_dict[widget] = create_func
        if emit:
            self.addWidgetSignal.emit(widget)
        return widget

    def delWidget(self, widget: QWidget, deleteLater=True, emit=True) -> tuple[int, int]:
        """
        删除一个QWidget子类
        :param widget :需要删除的Qwidget类
        :param deleteLater:彻底清除
        :param emit:是否发射信号
        :return 返回该元素所在的坐标(行，列)
        """
        target_row, target_col = self.getWidgetCoord(widget)  # 获取坐标
        widget = self.cellWidget(target_row, target_col)
        self.removeCellWidget(target_row, target_col)
        if deleteLater:
            widget.deleteLater()
        if emit:
            self.delWidgetSignal.emit(widget)
        return target_row, target_col

    def addRow(self, row_data: list[QWidget | str | int | float], height=100):
        """新增一行数据"""
        row_index = self.rowCount()
        self.insertRow(row_index)
        self.setRowHeight(row_index, height)
        for col, widget in enumerate(row_data):
            if isinstance(widget, (str, int, float)):
                item = QTableWidgetItem(widget)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row_index, col, item)
            elif isinstance(widget, QWidget):
                self.setCellWidget(row_index, col, widget)
            else:
                raise TypeError(f'{widget}是不支持的类型{type(widget)}')

    def delRow(self, widget: QWidget, column_index: int | list = None):
        """
        删除一行数据
        :param column_index:指定搜索哪一列
        """
        target_row, target_col = self.getWidgetCoord(widget, column_index)  # 获取坐标
        self.removeRow(target_row)

    def realign(self, start_row: int = None, start_col: int = None):
        """
        重新调整当前表格单元格位置
        :param start_row: 从哪一行开始,默认从首行
        :param start_col: 从那一列开始,默认从首列
        """
        start_row = 0 if start_row is None else start_row
        start_col = 0 if start_col is None else start_col
        # 记录全部需要重新调整位置的QWidget
        widgets = []
        for cur_row in range(start_row, self.rowCount()):
            for cur_col in range(start_col, self.columnCount()):
                widget = self.cellWidget(cur_row, cur_col)
                if widget is not None:
                    widgets.append(widget)
        # 重新创建QWidget类
        for widget in widgets:
            create_func = self.__widget_dict.get(widget, None)
            if create_func is not None:
                self.delWidget(widget, emit=False)
                self.addWidget(create_func, emit=False)
        # 清除多余行
        row, col = self.getEmptyCoord(create=False)
        if col == 0:
            self.setRowCount(row)
        self.realignSignal.emit(True)

    def calculateRowHeight(self):
        width = self.columnWidth(0)  # 获取当前列宽
        height = width / self.cellRatio  # 计算高度
        height = height if height < self.height() else self.height()
        for index_row in range(self.rowCount()):
            self.setRowHeight(index_row, height)
        self.verticalScrollBar().setSingleStep(int(height / 6))
        # 触发布局更新
        self.updateGeometry()
        self.updateGeometries()
        self.viewport().update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.enable_adaptive_row_height:
            self.calculateRowHeight()


class LoadDialog(MessageBoxBase):
    """加载对话框"""

    def __init__(self, text='', parent=None, show_progress=False):
        """
        :param text: 要显示的文本内容
        :param show_progress:显示有进度 进度环,默认显示无进度
        """
        self.__parent = parent
        self.text = text
        self.show_progress = show_progress
        super().__init__(self.__parent)
        self.uiInit()

    def uiInit(self):
        """添加基本控件"""
        self.progress_layout = QHBoxLayout(self)
        # 添加环形进度条
        self.progress = ProgressRing()
        self.progress.setTextVisible(True)
        self.progress.setFixedSize(50, 50)
        self.progress.setStrokeWidth(4)
        # 进度环形无进度进度条
        self.progress_indeter = IndeterminateProgressRing()
        self.progress_indeter.setFixedSize(50, 50)
        self.progress_indeter.setStrokeWidth(4)
        # self.progress_layout.addStretch()
        self.progress_layout.addWidget(self.progress)
        self.progress_layout.addWidget(self.progress_indeter)
        # self.progress_layout.addStretch()
        self.viewLayout.addLayout(self.progress_layout)
        self.progress_indeter.hide() if self.show_progress else self.progress.hide()
        # 添加文本
        self.label = TitleLabel(text=self.text)
        self.viewLayout.addWidget(self.label)
        # 隐藏确定和取消按钮
        self.hideYesButton()
        # self.hideCancelButton()
        # 设置最小宽度
        self.widget.setMinimumWidth(300)
        self.widget.setMinimumHeight(200)

    def setText(self, text):
        self.label.setText(text)


class AppCore(QObject):
    """全局控制信号"""
    broadcastSignal = Signal(str, object)  # 广播信号，标识符,数据
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        super().__init__()
        self._all_signals = {}  # 提交的信号
        self._work_flow_pool_nowait = TaskManage(WH.Config.THREAD_NUM)  # UI任务流任务管理类,不阻塞任务
        self._work_flow_pool = TaskManage(WH.Config.THREAD_NUM)  # UI任务流任务管理类,可阻塞任务

    @property
    def getWorkFlowPool(self) -> TaskManage:
        return self._work_flow_pool

    @property
    def getWorkFlowPoolNowait(self) -> TaskManage:
        return self._work_flow_pool_nowait

    def addSignal(self, name, signal):
        """添加信号,name一般采用信号变量名除signal部分"""
        with self._lock:
            self._all_signals[name] = signal

    def getSignal(self, name) -> Signal | None:
        with self._lock:
            return self._all_signals.get(name, None)

    def broadcast(self, id, data):
        """发射广播信号"""
        self.broadcastSignal.emit(id, data)

    def stopWorkFlow(self):
        self._work_flow_pool.stop()
        self._work_flow_pool_nowait.stop()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    w = QWidget()
    b = ProgressRingButton()
    l = QHBoxLayout(w)
    l.addWidget(b)
    w.show()
    app.exec()
