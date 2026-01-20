"""壁纸播放窗口"""
import os, sys, numpy as np

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.realpath(__file__))
# 计算父级目录的路径(wallpaper路径)
parent_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
# 将父级目录添加到模块搜索路径
sys.path.append(parent_dir)

# UI界面-PySide6模块及其美化库
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout,
                               QAbstractItemView, QHeaderView,
                               QSplitter, QLabel)
from PySide6.QtCore import Signal, Qt
from qfluentwidgets.components.widgets.button import PrimaryToolButton
from qfluentwidgets import FluentIcon as FIF

# 壁纸播放的功能实现
from play_wallpaper import play

# 本项目公用库
from Fun.GUI_Qt import PySide6Mod, PlotCv2Mod, qfdialog
from Fun.Norm import get, file

# 导入UI界面
from .ui.wallpaper_ui import Ui_wallpaper
from .ui.set import Ui_set
from .ui.table import Ui_widget_table


class Dialog(qfdialog.DialogBase):

    def __init__(self, wallpaper, parent=None):
        super().__init__(Ui_set, parent)
        self.wallpaper = wallpaper
        self.data_init()

    def data_init(self):
        self.ui.spinBox_paly_time.setValue(self.wallpaper.get_play_time)  # 播放间隔
        self.ui.lineEdit_white.setText(';'.join(self.wallpaper.get_filter_list[0]))  # 白名单
        self.ui.lineEdit_black.setText(';'.join(self.wallpaper.get_filter_list[1]))  # 黑名单

    def get_all_data(self):
        play_time = self.ui.spinBox_paly_time.value()
        white_text = self.ui.lineEdit_white.text()
        if white_text != '':
            white_list = white_text.split(';')
        else:
            white_list = []
        black_text = self.ui.lineEdit_black.text()
        if black_text != '':
            black_list = black_text.split(';')
        else:
            black_list = []

        if play_time == self.wallpaper.get_play_time:
            play_time = -1.0
        if white_list == self.wallpaper.get_filter_list[0]:
            white_list = None
        if black_list == self.wallpaper.get_filter_list[1]:
            black_list = None
        return {'play_time': play_time,
                'white_list': white_list,
                'black_list': black_list}


class WallPaperWin(Ui_wallpaper, QWidget):
    # 初始化信号
    update_signal = Signal(tuple)

    def __init__(self, parent=None):
        self.__parent = parent
        super().__init__(parent)
        Ui_wallpaper.setupUi(self, self)
        # 初始化左右布局
        self.__init_splitter()

        # 添加左布局中的table
        self.table = Ui_widget_table()
        self.table.setupUi(self.left_widget)

        # 连接槽函数
        self.update_signal.connect(self.updata_ui)
        # 初始化图像显示
        self.__show_image = PlotCv2Mod.PlotChart(self.right_layout)
        self.__show_image.set_alpha(0)
        self.__image_path = str  # 当前播放的图像路径
        # 初始化壁纸播放
        self.__wallpaper = play.WallPaper()
        self.__wallpaper.load_data()
        self.__wallpaper.set_play_func(lambda image_path, image: self.update_signal.emit((image_path, image)))

        # 设置界面元素
        self.__init_ui()
        # 绑定控件
        self.__bind()

    def updata_ui(self, value: tuple):
        self.__image_path, image = value
        image = np.array(image)
        self.__show_image.clear_plot()
        self.__show_image.open_image(image, is_show=True)

    def __init_splitter(self):
        # 创建左右布局
        self.left_widget = QWidget()
        self.left_layout = QHBoxLayout(self.left_widget)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(0)

        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)

        # 创建QSplitter对象，指定为水平方向（左右分栏）
        self.splitter = QSplitter(Qt.Horizontal)
        # 关闭实时更新
        self.splitter.setOpaqueResize(False)
        # 将左右部件添加到splitter
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)

        # 设置初始比例,数字代表宽度像素
        self.splitter.setSizes([400, 500])

        # 设置分界线样式
        self.splitter.setStyleSheet(
            """QSplitter::handle { 
                            background-color: rgb(220,220,220); 
                            border: 1px solid rgb(220,220,220); 
                            margin: 1px;}""")

        # 将splitter添加到主布局
        self.verticalLayout_2.addWidget(self.splitter)

    def __init_ui(self):
        """界面元素初始化"""
        # 禁止编辑
        self.table.tableWidget_dirs_path.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 隐藏垂直表头即右侧表头
        self.table.tableWidget_dirs_path.verticalHeader().setVisible(False)
        # 交替行变色
        self.table.tableWidget_dirs_path.setAlternatingRowColors(True)
        # 设置列宽模式
        # 设置填充剩余空间,第一个参数不填时默认全部生效
        self.table.tableWidget_dirs_path.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # 设置列自适应列宽,第一个参数不填时默认全部生效
        self.table.tableWidget_dirs_path.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.tableWidget_dirs_path.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

        # 添加按钮图标
        self.pushButton_start.setIcon(FIF.SEND)
        self.pushButton_add.setIcon(FIF.FOLDER_ADD)
        self.pushButton_del.setIcon(FIF.DELETE)
        self.pushButton_set.setIcon(FIF.SETTING)
        self.pushButton_open_image.setIcon(FIF.CHEVRON_RIGHT)

        # 添加数据
        self.__pushButton_add(self.__wallpaper.get_dirs_path, init=True)

    def update_theme_color(self, change='light'):
        change = change.lower()
        # 设置所有QWidget类背景色为浅色
        LIGHT = 'QWidget {background-color: rgb(250,248,252);color: black;}'
        DACK = 'QWidget {background-color: rgb(45,45,45);color: black;}'
        if change == 'light':
            self.setStyleSheet(LIGHT)
        elif change == 'dark':
            self.setStyleSheet(DACK)
        LIGHT_table = """QTableWidget {
                            gridline-color: #eee;
                            selection-background-color: #e3f2fd;
                            selection-color: #333; /* 选中单元格的字体颜色 */
                            color: #555; /* 默认字体颜色（未选中状态） */
                            font-family: "Microsoft YaHei", sans-serif; /* 可选：设置字体 */
                            font-size: 12px; /* 可选：设置字体大小 */
                            }
                            QHeaderView::section {
                                background-color: rgb(250,248,252);
                                color: black;
                                font-weight:bold;
                                border: none;
                                padding: 5px;
                            }"""
        DACK_table = """QTableWidget {
                            gridline-color: #eee;
                            selection-background-color: #e3f2fd;
                            selection-color: #333; /* 选中单元格的字体颜色 */
                            color: #555; /* 默认字体颜色（未选中状态） */
                            font-family: "Microsoft YaHei", sans-serif; /* 可选：设置字体 */
                            font-size: 12px; /* 可选：设置字体大小 */
                            }
                            /* 单元格默认样式 */
                            QTableWidget::item {
                                color: #faf8fc; /* 默认字体颜色 */
                            }
                            /* 选中单元格样式 */
                            QTableWidget::item:selected {
                                color: rgb(45,45,45);
                            }
                            QHeaderView::section {
                                background-color: rgb(45,45,45);
                                color: #faf8fc;
                                font-weight:bold;
                                border: none;
                                padding: 5px;
                            }"""
        if change == 'light':
            self.table.tableWidget_dirs_path.setStyleSheet(LIGHT_table)
        elif change == 'dark':
            self.table.tableWidget_dirs_path.setStyleSheet(DACK_table)

    def __pushButton_add(self, dirs_path: list | set = None, init=False):
        if dirs_path is None:
            max_row = self.table.tableWidget_dirs_path.rowCount()
            item = self.table.tableWidget_dirs_path.item(max_row - 1, 0)
            if item is not None:
                item = f'{item.text()}/..'
                path = PySide6Mod.get_exist_dir(dir_path=item)
            else:
                path = PySide6Mod.get_exist_dir()
            if path == '':
                return
            else:
                dirs_path = [path]
        if isinstance(dirs_path, set):
            dirs_path = list(dirs_path)
        if dirs_path != []:
            for dir_path in dirs_path:
                if init or dir_path not in self.__wallpaper.get_dirs_path:
                    # 创建一个按钮
                    widget = QWidget()
                    btn = PrimaryToolButton(FIF.VIEW)
                    btn_layout = QHBoxLayout(widget)
                    btn_layout.setContentsMargins(5, 5, 5, 5)
                    btn_layout.setSpacing(10)
                    btn_layout.addWidget(btn)
                    btn.clicked.connect(lambda: file.open_file_use_explorer(dir_path))
                    # 获取当前时间
                    now_time = get.now_time('%Y-%m-%d')
                    PySide6Mod.add_table_widget_row(self.table.tableWidget_dirs_path, [dir_path, now_time, widget])
            # 保存当前配置
            self.__wallpaper.add_user_dir(dirs_path, update=not init)
            self.__wallpaper.save_set()

    def __pushButton_start(self):
        if self.pushButton_start.text() == '开始':
            self.pushButton_start.setText('停止')
            self.__wallpaper.run()
        elif self.pushButton_start.text() == '停止':
            self.pushButton_start.setText('开始')
            self.__wallpaper.stop()

    def __pushButton_del(self):
        # 获取所有选中的项目
        selected_items = self.table.tableWidget_dirs_path.selectedItems()
        all_selectcell = []
        del_row = []
        if selected_items:
            # 输出依次输出选中单元格的信息
            for item in selected_items:
                col = item.column()
                if col == 0:
                    value = item.text()
                    row = item.row()
                    all_selectcell.append(value)
                    del_row.append(row)
        if all_selectcell != []:
            del_row = sorted(del_row, reverse=True)
            for index in del_row:
                self.table.tableWidget_dirs_path.removeRow(index)
            self.__wallpaper.del_user_dir(all_selectcell)
            self.__wallpaper.save_set()

    def __pushButton_set(self):
        """壁纸播放设置"""
        dialog = Dialog(self.__wallpaper, self.__parent)
        if dialog.exec() == 1:
            data = dialog.get_all_data()
            if data['play_time'] != -1:
                self.__wallpaper.set_play_time(data['play_time'])
            self.__wallpaper.set_filre_list(data['white_list'], data['black_list'])
            # 保存当前设置
            self.__wallpaper.save_set()

    def __bind(self):
        """控件绑定"""
        self.pushButton_del.clicked.connect(self.__pushButton_del)
        self.pushButton_add.clicked.connect(lambda: self.__pushButton_add())
        self.pushButton_start.clicked.connect(self.__pushButton_start)
        self.pushButton_set.clicked.connect(self.__pushButton_set)
        self.pushButton_open_image.clicked.connect(lambda: file.open_file_use_explorer(self.__image_path))


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    w = WallPaperWin()
    w.update_theme_color('LIGHT')
    w.show()
    app.exec()
