"""模板化部件"""
# PySide6原生组件
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout,
                               QGroupBox, QHeaderView, QStackedWidget,
                               QAbstractItemView, QWidget)
# 风格化组件
from qfluentwidgets.components.widgets import (TableWidget, CheckBox,
                                               TitleLabel, IndeterminateProgressRing)
from qfluentwidgets.components.dialog_box import MessageBoxBase
from qfluentwidgets.components.navigation import Pivot, SegmentedWidget
# 自定义组件
from Fun.GUI_Qt.PySide6Mod import ImageWidget

from typing import Callable


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


class GroupBoxCell(QGroupBox):
    """带选择控件和图片显示的单元格组件"""
    StateChange = Signal(bool)  # 内部的checkBox状态改变时

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, parent=parent, **kwargs)
        self.__parent = parent  # 父对象
        # 主要用于反馈当前图像加载状况
        self.image = None  # 当前显示的图像
        self.image_path = None  # 设置图像路径
        self.image_loading = False  # 图像是否正在加载

        self.layout = QVBoxLayout(self)
        self.layout_title = QHBoxLayout(self)
        self.image_widget = ImageWidget()
        self.checkBox = CheckBox()
        self.uiInit()
        self.bind()

    def uiInit(self):
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout_title.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout_title.setSpacing(0)
        self.layout.addLayout(self.layout_title)
        self.layout_title.addWidget(self.checkBox)
        self.layout.addWidget(self.image_widget)

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

    def setImage(self, image):
        self.image_widget.set_image(image)
        self.image = image

    def setImageText(self, text: str):
        self.image_widget.set_text(text)

    def clearImage(self):
        self.image = None
        self.image_path = None
        self.image_loading = False
        self.image_widget.set_image(self.image_widget.defaultImage)

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
                """
                           )


class GroupBoxTable(TableWidget):
    """用于容纳GroupBoxCell的表格"""
    delWidgetSignal = Signal(QWidget)  # 有部件被删除时的信号
    addWidgetSignal = Signal(QWidget)  # 有部件新增时的信号
    realignSignal = Signal(bool)  # 单元格重新排布时的信号
    visibleRowsSignal = Signal(list)  # 滚动条滚动时发送当前可见行

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, parent=parent, **kwargs)
        self.__parent = parent
        self.__widget_dict = {}  # 存储了每个QWidget类的创建函数
        self.cellRatio = 3 / 4  # 单元格宽高比
        # 使用定时器实现防止滚动条快速滚动而频繁触发信号
        self.scroll_check_timer = QTimer()
        self.scroll_check_timer.setSingleShot(True)  # 单次触发
        self.scroll_check_timer.timeout.connect(self.getShowRowSignal)
        self.verticalScrollBar().valueChanged.connect(lambda: self.scroll_check_timer.start(300))
        self.uiInit()

    def uiInit(self):
        self.setColumnCount(4)  # 设置列数
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应列宽
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
        self.verticalHeader().setVisible(False)  # 隐藏垂直表头即左侧表头
        self.horizontalHeader().setVisible(False)  # 隐藏水平表头即顶侧表头
        self.setAlternatingRowColors(True)  # 交替行变色

    def getEmptyCoord(self, start_row: int = None, start_col: int = None, create=True) -> tuple[int, int]:
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
        self.setRowHeight(max_row, 100)
        return max_row, 0

    def getWidgetCoord(self, widget: QWidget):
        """获取目标容器坐标"""
        for target_row in range(self.rowCount()):
            for target_col in range(self.columnCount()):
                if self.cellWidget(target_row, target_col) == widget:
                    return target_row, target_col

    def getShowRowSignal(self) -> list:
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

        # 发射信号（可以根据需要选择发射哪种格式）
        self.visibleRowsSignal.emit(all_visible_rows)  # 只发射行号列表
        # self.visibleRowsSignal.emit(visible_info)  # 或者发射详细信息

        return all_visible_rows

    def addWidget(self, create_func: Callable, emit=True) -> QWidget:
        """
        添加一个QWidget子类
        :param create_func:创建这个部件的函数,用于表格内位置调整,返回值必须为QWidget子类
        :param emit:是否发射信号
        """
        # 获取当前非空单元格位置,如果当前没有非空单元格则创建新的行
        target_row, target_col = self.getEmptyCoord()
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
        """
        target_row, target_col = self.getWidgetCoord(widget)  # 获取坐标
        widget = self.cellWidget(target_row, target_col)
        self.removeCellWidget(target_row, target_col)
        if deleteLater:
            widget.deleteLater()
        if emit:
            self.delWidgetSignal.emit(widget)
        return target_row, target_col

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
                self.addWidget(create_func(), create_func, emit=False)
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
        self.calculateRowHeight()


class LoadDialog(MessageBoxBase):
    """加载对话框"""

    def __init__(self, text='', parent=None):
        """
        :param text: 要显示的文本内容
        """
        self.__parent = parent
        self.text = text
        super().__init__(self.__parent)
        self.uiInit()

    def uiInit(self):
        """添加基本控件"""
        # 添加环形进度条
        self.progress = IndeterminateProgressRing()
        self.progress.setFixedSize(50, 50)
        self.progress.setStrokeWidth(4)
        self.viewLayout.addWidget(self.progress)
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


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    w = GroupBoxTable()
    w.addWidget(GroupBoxCell)
    w.show()
    app.exec()
