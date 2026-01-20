"""主布局的右半表格"""
from .Config import *


class RigetWidget(Ui_RightWidget, QWidget):
    download_clicked = Signal(tuple)  # 发送(image_id,状态信息0:删除,1:重试,2:已完成)
    update_clicked = Signal(list)  # 发送待更新的key_wrod

    def __init__(self, parent=None):
        self.__parent = parent
        # 存储了全部单元格元素
        # image_id:{choice,progress,label,button}
        self.cell_items = {}
        # 存储了全部单元格元素
        # key_word:(checkBox,probar,lable,
        # QTableWidgetItem,QTableWidgetItem,QTableWidgetItem,QTableWidgetItem)
        self.cell_items_like = {}
        super().__init__()
        self.setupUi(self)
        self.uiInit()
        self.bind()

    def uiInit(self):
        # 设置下载表格
        # 设置列数
        # self.tableWidget_download.setColumnCount(1)
        # 自适应列宽
        self.tableWidget_download.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # 填充剩余空间
        self.tableWidget_download.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        # 禁止编辑
        self.tableWidget_download.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 禁止用户通过拖动调整行高
        self.tableWidget_download.verticalHeader().setSectionsMovable(False)  # 禁止移动行
        self.tableWidget_download.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)  # 关键：固定行高
        # 隐藏水平表头即顶侧表头
        # self.tableWidget_download.horizontalHeader().setVisible(False)
        # 交替行变色
        self.tableWidget_download.setAlternatingRowColors(True)

        # 设置收藏表格
        # 自适应列宽
        self.tableWidget_like.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # 填充剩余空间
        self.tableWidget_like.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        # 禁止编辑
        self.tableWidget_like.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget_like.verticalHeader().setSectionsMovable(False)  # 禁止移动行
        self.tableWidget_like.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)  # 关键：固定行高

        # 隐藏垂直表头即左侧表头
        # self.tableWidget_like.verticalHeader().setVisible(False)
        # 交替行变色
        self.tableWidget_like.setAlternatingRowColors(True)

    def bind(self):
        def choiceAll2():
            self.pushButton_choice_all_2.setText('取消全选')
            for item in self.cell_items_like.values():
                item[0].setChecked(True)
            self.pushButton_choice_all_2.clicked.disconnect()
            self.pushButton_choice_all_2.clicked.connect(choiceAll2_None)

        def choiceAll2_None():
            self.pushButton_choice_all_2.setText('全选')
            for item in self.cell_items_like.values():
                item[0].setChecked(False)
            self.pushButton_choice_all_2.clicked.disconnect()
            self.pushButton_choice_all_2.clicked.connect(choiceAll2)

        self.pushButton_updata.clicked.connect(self.updateSignal)
        self.pushButton_choice_all_2.clicked.connect(choiceAll2)

    def addLike(self, key_word, last_page, total, date, updata_date):
        row = self.tableWidget_like.rowCount()
        self.tableWidget_like.insertRow(row)
        self.tableWidget_like.setRowHeight(row, 50)
        # 添加选择按钮
        choice = QCheckBox(text=key_word)
        self.tableWidget_like.setCellWidget(row, 0, choice)
        # 添加进度条
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout_H = QHBoxLayout()
        layout.setContentsMargins(0, 5, 0, 0)
        layout_H.setContentsMargins(0, 0, 5, 5)
        progress = QProgressBar(minimum=0, maximum=100, value=0)
        label = QLabel(text='')
        layout_H.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout_H.addWidget(label)
        layout.addWidget(progress)
        layout.addLayout(layout_H)
        self.tableWidget_like.setCellWidget(row, 1, widget)
        items = [choice, progress, label]
        # 添加页数、总数、日期、上次更新日期
        for count, text in enumerate([last_page, total, date, updata_date]):
            # 转为QWitem对象
            item = QTableWidgetItem(str(text))
            item.setTextAlignment(Qt.AlignCenter)
            # 添加子元素
            self.tableWidget_like.setItem(row, count + 2, item)
            items.append(item)
        self.cell_items_like[key_word] = items

    def addDownload(self, image_id):
        """下载表格添加数据"""
        if image_id not in self.cell_items:
            row = self.tableWidget_download.rowCount()
            self.tableWidget_download.insertRow(row)
            self.tableWidget_download.setRowHeight(row, 40)
            # 添加选择按钮
            choice = QCheckBox(text=image_id)
            self.tableWidget_download.setCellWidget(row, 0, choice)
            # 添加进度条
            progress_widget = QWidget()
            layout = QVBoxLayout(progress_widget)
            layout.setContentsMargins(0, 0, 5, 5)
            progress = QProgressBar(minimum=0, maximum=100, value=0)
            layout.addWidget(progress)
            # 添加状态标签
            label = QLabel(text='未开始')
            layout.addWidget(label)
            self.tableWidget_download.setCellWidget(row, 1, progress_widget)
            # 添加操作按钮(默认状态为删除)
            button = PrimaryToolButton(FIF.CLOSE)
            layout.addWidget(button)
            self.tableWidget_download.setCellWidget(row, 2, button)
            # 保存元素信息
            self.cell_items[image_id] = {
                'choice': choice,
                'progress': progress,
                'label': label,
                'button': button
            }
            # 绑定信号
            button.clicked.connect(lambda _, value=image_id: self.download_clicked.emit((value, 0)))
            self.stackedWidget.setCurrentIndex(0)
            return True
        else:
            return False

    def delDownload(self, image_id):
        """下载表格删除数据"""
        item: dict = self.cell_items.get(image_id, None)
        if item is not None:
            # 找到widget所在的行
            row = -1
            for r in range(self.tableWidget_download.rowCount()):
                if self.tableWidget_download.cellWidget(r, 0).text() == image_id:
                    row = r
                    break
            if row >= 0:
                # 清理资源
                for widget in item.values():
                    widget.deleteLater()
                # 从字典中移除
                del self.cell_items[image_id]
                # 删除行
                self.tableWidget_download.removeRow(row)

    def displayStart(self, image_id):
        item = self.cell_items.get(image_id, None)
        if item is not None:
            item['label'].setText('获取图像信息中')

    def displayLikeStart(self, key_word):
        item = self.cell_items_like[key_word]
        item[2].setText('检查更新中')

    def displayLikeUpdating(self, key_word, *args):
        """更新中"""
        item = self.cell_items_like[key_word]
        if len(args) == 2:
            finised, total = args
            value = int(100 * finised / total)
            item[1].setValue(value)
            text = '搜索中' if item[2].text() != '下载中' else '下载中'
            item[2].setText(text)
        elif len(args) == 4:
            last_page, total, date, update_date = args
            item[3].setText(str(last_page))
            item[4].setText(str(total))
            item[5].setText(str(date))
            item[6].setText(str(update_date))

    def displayDownloading(self, result: dict):
        """显示下载中的状态"""
        value = int(100 * (result['progress'] / result['total'])) if result['total'] != 0 else 0
        if result['rate'] / 1024 < 1.2:
            rate = f'下载中:{result['rate']:4.2f}Kb/s'
        else:
            rate = f'下载中:{result['rate'] / 1024:4.2f}Mb/s'
        item = self.cell_items.get(result['name'], None)
        if item is not None:
            item['progress'].setValue(value)
            item['label'].setText(rate)

    def displayLikeFinished(self, key_word: str, state: int):
        """显示完成,state:0表示搜索完成,1表示下载完成,2表示更新完成"""
        item = self.cell_items_like[key_word]
        text_dict = {
            0: '搜索完成',
            1: '下载中',
            2: '更新完成'
        }
        item[2].setText(text_dict[state])
        if state == 2:
            item[0].setChecked(False)
        elif state == 1:
            item[1].setValue(0)
        # 将该行置顶
        self.tableWidget_like.scrollToItem(
            item[3],
            QAbstractItemView.ScrollHint.PositionAtTop  # 滚动到顶部
        )

    def displayFinished(self, image_id: str):
        """已完成下载的槽函数"""
        item = self.cell_items.get(image_id, None)
        if item is not None:
            item['progress'].setValue(100)
            item['label'].setText('已完成')
            item['button'].setIcon(FIF.DELETE)
            item['button'].clicked.disconnect()  # 断开全部点击连接信号
            item['button'].clicked.connect(
                lambda _, value=image_id: self.download_clicked.emit((value, 2))
            )
            # 三秒后自动删除已完成的下载记录
            QTimer.singleShot(3000, lambda value=image_id: self.delDownload(value))

    def displayError(self, image_id: str, key_word: str):
        def retry(image_id, key_word):
            self.download_clicked.emit(((image_id, key_word), 1))
            item = self.cell_items[image_id]
            item['label'].setText('未开始')
            item['button'].setIcon(FIF.CLOSE)
            item['button'].clicked.disconnect()  # 断开全部点击连接信号
            item['button'].clicked.connect(lambda _, value=image_id: self.download_clicked.emit((value, 0)))

        if image_id in self.cell_items.keys():
            self.delDownload(image_id)
        self.addDownload(image_id)
        item = self.cell_items[image_id]
        item['label'].setText('下载失败')
        item['button'].setIcon(FIF.ROTATE)
        item['button'].clicked.disconnect()  # 断开全部点击连接信号
        item['button'].clicked.connect(lambda _, value=(image_id, key_word): retry(*value))

    def displayLikeError(self, key_word):
        item = self.cell_items_like[key_word]
        item[2].setText('任务失败')
        # item[0].setChecked(False)

    def buttonRetry(self, image_id: str):
        item = self.cell_items.get(image_id, None)
        if item is not None:
            item['label'].setText('正在重试')
            item['button'].setIcon(FIF.CLOSE)
            item['button'].clicked.disconnect()  # 断开全部点击连接信号
            item['button'].clicked.connect(lambda _, value=image_id: self.download_clicked.emit((value, 0)))

    def updateSignal(self):
        """发送待更新的key_word"""
        key_words = [key_word for key_word, item in self.cell_items_like.items() if item[0].isChecked()]
        self.update_clicked.emit(key_words)

    def updateHight(self, ratio=1 / 5):
        """根据当前窗口大小调整表格最小宽度"""
        parent_width = self.width()
        self.tableWidget_download.setMinimumWidth(max(parent_width * 4 / 10, 300))

    def resizeEvent(self, event):
        """当窗口大小改变时自动调整单元格"""
        super().resizeEvent(event)
        self.updateHight()
        self.update()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication, QTableWidgetItem

    app = QApplication([])
    w = RigetWidget()
    w.show()
    app.exec()
