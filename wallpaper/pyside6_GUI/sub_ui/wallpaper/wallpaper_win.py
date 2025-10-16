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
from Fun.GUI_Qt import PySide6Mod
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

    def __pushButton_add(self, dir_path: str = None):
        if dir_path is None:
            dir_path = PySide6Mod.get_exist_dir()
        if dir_path != '':
            # 创建一个按钮
            widget = QWidget()
            btn = PrimaryToolButton(FIF.FOLDER)
            btn_layout = QHBoxLayout(widget)
            btn_layout.setContentsMargins(5, 5, 5, 5)
            btn_layout.setSpacing(10)
            btn_layout.addWidget(btn)
            btn.clicked.connect(lambda: file.open_file_use_explorer(dir_path))
            # 获取当前时间
            now_time = get.now_time()
            PySide6Mod.add_table_widget_row(self.tableWidget_dirs_path, [dir_path, now_time, widget])

    def __bind(self):
        """控件绑定"""

        self.pushButton_add.clicked.connect(lambda: self.__pushButton_add())


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    w = WallPaperWin()
    # 设置所有QWidget类背景色为浅色
    LIGHT = 'QWidget {background-color: rgb(250,248,252);color: black;}'
    DACK = 'QWidget {background-color: rgb(45,45,45);color: black;}'
    w.setStyleSheet(LIGHT)
    w.show()
    app.exec()
