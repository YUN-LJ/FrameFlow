"""壁纸播放窗口"""
import sys, os

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.realpath(__file__))
# 计算父级目录的路径(wallpaper路径)
parent_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
# 将父级目录添加到模块搜索路径
sys.path.append(parent_dir)

# UI界面-PySide6模块及其美化库
from PySide6.QtWidgets import (QWidget, QHBoxLayout,
                               QAbstractItemView, QHeaderView)
from qfluentwidgets.components.widgets.button import PrimaryToolButton
from qfluentwidgets import FluentIcon as FIF

# 壁纸播放的功能实现
from play_wallpaper import play

# 本项目公用库
from Fun.GUI_Qt import PySide6Mod, PlotCv2Mod
from Fun.Norm import get, file

# 导入UI界面
try:
    from .ui.wallpaper_ui import Ui_wallpaper
except:
    from ui.wallpaper_ui import Ui_wallpaper


class WallPaperWin(Ui_wallpaper, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        # 初始化图像显示
        self.__show_image = PlotCv2Mod.Cv2ShowQt(self.label_image)
        # 初始化壁纸播放
        self.__wallpaper = play.WallPaper()
        self.__wallpaper.load_data()
        self.__wallpaper.set_play_func(self.__show_image.show)

        # 设置界面元素
        self.__init_ui()
        # 绑定控件
        self.__bind()

    def __init_ui(self):
        """界面元素初始化"""
        # 禁止编辑
        self.tableWidget_dirs_path.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 隐藏垂直表头即右侧表头
        self.tableWidget_dirs_path.verticalHeader().setVisible(False)
        # 交替行变色
        self.tableWidget_dirs_path.setAlternatingRowColors(True)
        # 设置列宽模式
        # 设置填充剩余空间,第一个参数不填时默认全部生效
        self.tableWidget_dirs_path.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # 设置列自适应列宽,第一个参数不填时默认全部生效
        self.tableWidget_dirs_path.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tableWidget_dirs_path.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

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
            self.tableWidget_dirs_path.setStyleSheet(LIGHT_table)
        elif change == 'dark':
            self.tableWidget_dirs_path.setStyleSheet(DACK_table)

    def __pushButton_add(self, dirs_path: list | set = None, init=False):
        if dirs_path is None:
            dirs_path = [PySide6Mod.get_exist_dir()]
        if isinstance(dirs_path, set):
            dirs_path = list(dirs_path)
        if dirs_path != []:
            for dir_path in dirs_path:
                if init or dir_path not in self.__wallpaper.get_dirs_path:
                    # 创建一个按钮
                    widget = QWidget()
                    btn = PrimaryToolButton(FIF.FOLDER)
                    btn_layout = QHBoxLayout(widget)
                    btn_layout.setContentsMargins(5, 5, 5, 5)
                    btn_layout.setSpacing(10)
                    btn_layout.addWidget(btn)
                    btn.clicked.connect(lambda: file.open_file_use_explorer(dir_path))
                    # 获取当前时间
                    now_time = get.now_time('%Y-%m-%d')
                    PySide6Mod.add_table_widget_row(self.tableWidget_dirs_path, [dir_path, now_time, widget])
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

    def __bind(self):
        """控件绑定"""

        self.pushButton_add.clicked.connect(lambda: self.__pushButton_add())
        self.pushButton_start.clicked.connect(self.__pushButton_start)


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    w = WallPaperWin()
    w.update_theme_color('LIGHT')
    w.show()
    app.exec()
