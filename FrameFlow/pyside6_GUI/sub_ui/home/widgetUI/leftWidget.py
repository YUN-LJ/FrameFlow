"""主布局的左半表格"""
from pyside6_GUI.sub_ui.home.widgetUI.Config import *


class LeftWidget(Ui_ImageTable, QWidget):
    view_cliced = Signal(str)  # 查看详细按钮触发
    download_clicked = Signal(str)
    visible_row = Signal(tuple)  # 滚动条改变时触发,发送当前可见的(起始行索引,终止行索引),调用checkShowRowSignal主动触发

    def __init__(self, parent=None):
        self.__parent = parent
        self.__curruent_col = -1  # 数据添加了几次
        self.cell_items = []  # 存储了表格中全部的单元格(QWidget,QCheckBox,image_widget,button_download,button_view)
        self.choice_image_id = set()  # 存储了全部被选中的image_id
        super().__init__()
        self.setupUi(self)
        self.uiInit()
        self.bind()
        # 使用定时器实现防止滚动条快速滚动而频繁触发信号
        self.scroll_check_timer = QTimer()
        self.scroll_check_timer.setSingleShot(True)  # 单次触发
        self.scroll_check_timer.timeout.connect(self.checkShowRowSignal)
        QTimer.singleShot(0, self.updateHight)

    def uiInit(self):
        # 设置列数
        self.tableWidget_image.setColumnCount(4)
        # 自适应列宽
        self.tableWidget_image.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 禁止编辑
        self.tableWidget_image.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 隐藏垂直表头即左侧表头
        self.tableWidget_image.verticalHeader().setVisible(False)
        # 隐藏水平表头即顶侧表头
        self.tableWidget_image.horizontalHeader().setVisible(False)
        # 交替行变色
        self.tableWidget_image.setAlternatingRowColors(True)
        # 创建24个网格(由于每页的搜索结果是24张)
        for index in range(24):
            # 计算当前元素所在的坐标
            row = index // self.tableWidget_image.columnCount()
            col = index % self.tableWidget_image.columnCount()
            # 创建元素
            item = self.createItem()
            self.cell_items.append(item)
            self.addItem(item[0])
            item[1].stateChanged.connect(lambda state, row=row, col=col: self.checkSignal(state, row, col))
            item[3].clicked.connect(lambda _, row=row, col=col: self.downloadSignal(row, col))
            item[4].clicked.connect(lambda _, row=row, col=col: self.viewSignal(row, col))

    def bind(self):
        self.tableWidget_image.verticalScrollBar().valueChanged.connect(lambda: self.scroll_check_timer.start(300))

    def createItem(self) -> tuple[QWidget, QCheckBox, ImageWidget, PrimaryToolButton, PrimaryToolButton]:
        """
        创建一个表格单元格内容
        :return :tuple(QWidget,QCheckBox,image_widget,button_download,button_view)
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 5, 0, 5)
        # 创建标签
        choose_id = QCheckBox(text='')
        layout.addWidget(choose_id)
        # 创建图片显示
        image_polt = ImageWidget(DEFAULT_IMAGE)
        layout.addWidget(image_polt)
        # 创建按钮
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_download = PrimaryToolButton(FIF.DOWNLOAD)
        button_view = PrimaryToolButton(FIF.VIEW)
        button_layout.addWidget(button_download)
        button_layout.addWidget(button_view)
        layout.addLayout(button_layout)
        return (widget, choose_id, image_polt, button_download, button_view)

    def addItem(self, item: QWidget, hight=300):
        """添加一个元素到表格中"""
        self.__curruent_col += 1
        col = self.__curruent_col % self.tableWidget_image.columnCount()  # 添加到哪一列
        # 获取当前行数
        current_row = self.tableWidget_image.rowCount()
        if current_row == 0:
            self.tableWidget_image.insertRow(current_row)
            self.tableWidget_image.setRowHeight(current_row, hight)
            self.tableWidget_image.setCellWidget(current_row, col, item)
            return True
        # 如果表格已满，添加新行
        if col == 0:
            self.tableWidget_image.insertRow(current_row)
            self.tableWidget_image.setRowHeight(current_row, hight)
            self.tableWidget_image.setCellWidget(current_row, col, item)
            return True
        else:
            self.tableWidget_image.setCellWidget(current_row - 1, col, item)
            return True

    def checkShowRowSignal(self):
        """检测当前显示的行"""
        # 获取当前所在行
        start_row = self.tableWidget_image.verticalScrollBar().value()
        cell_hight = self.tableWidget_image.rowHeight(0)  # 单元格高
        table_hight = self.tableWidget_image.height()  # 表格高度
        show_count = (table_hight // cell_hight) - 1
        if table_hight % cell_hight > 0.2 * cell_hight:
            show_count += 1
        end_row = start_row + show_count
        self.visible_row.emit((start_row, end_row))

    def viewSignal(self, row, col):
        """查看按钮时点击时发送所在单元格的image_id"""
        index = row * self.tableWidget_image.columnCount() + col
        image_id = self.cell_items[index][1].text()
        # image_id = '8ggm9o'
        if image_id != "":
            self.view_cliced.emit(image_id)
        else:
            TeachingTip.create(
                target=self.cell_items[index][4],
                icon=InfoBarIcon.WARNING,
                title='温馨提示',
                content='无图片',
                isClosable=True,
                tailPosition=TeachingTipTailPosition.BOTTOM,
                duration=1000,
                parent=self.__parent)

    def downloadSignal(self, row, col) -> str:
        """下载按钮被点击时发送所在单元格的image_id"""
        index = row * self.tableWidget_image.columnCount() + col
        image_id = self.cell_items[index][1].text()
        # image_id = '8g5d5o'
        if image_id != "":
            self.download_clicked.emit(image_id)
        else:
            TeachingTip.create(
                target=self.cell_items[index][3],
                icon=InfoBarIcon.WARNING,
                title='温馨提示',
                content='无图片',
                isClosable=True,
                tailPosition=TeachingTipTailPosition.BOTTOM,
                duration=1000,
                parent=self.__parent)

    def checkSignal(self, state, row, col):
        """状态改变时记录选中的image_id,选中是2,未选中是0"""
        index = row * self.tableWidget_image.columnCount() + col
        image_id = self.cell_items[index][1].text()
        if image_id != '':
            if state == 2:
                self.choice_image_id.add(image_id)
            elif state == 0 and image_id in self.choice_image_id:
                self.choice_image_id.remove(image_id)
        else:
            TeachingTip.create(
                target=self.cell_items[index][1],
                icon=InfoBarIcon.WARNING,
                title='温馨提示',
                content='无图片',
                isClosable=True,
                tailPosition=TeachingTipTailPosition.BOTTOM,
                duration=1000,
                parent=self.__parent)
            self.cell_items[index][1].setChecked(False)

    def defaultCell(self):
        """重置单元格状态"""
        for item in self.cell_items:
            item[1].setChecked(False)
            item[1].setText('')
            item[2].set_image(DEFAULT_IMAGE)

    def updateHight(self, ratio=4 / 3):
        """根据列宽调整表格的行高"""
        parent_width = self.width()
        self.tableWidget_image.setMinimumWidth(max(parent_width * 5 / 10, 500))
        # 根据当前列宽设置行高
        width = self.tableWidget_image.columnWidth(0)
        height = width * ratio
        for row in range(self.tableWidget_image.rowCount()):
            self.tableWidget_image.setRowHeight(row, height)

    def resizeEvent(self, event):
        """当窗口大小改变时自动调整单元格"""
        super().resizeEvent(event)
        self.updateHight()
        self.update()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    w = LeftWidget()
    w.show()
    app.exec()
