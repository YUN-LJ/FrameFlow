"""壁纸播放窗口"""
import sys, os

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.realpath(__file__))
# 计算父级目录的路径(wallpaper路径)
parent_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
# 将父级目录添加到模块搜索路径
sys.path.append(parent_dir)

from play_wallpaper import play
from PySide6.QtWidgets import QWidget, QAbstractItemView, QHeaderView

# 导入UI界面
try:
    from .ui.wallpaper_ui import Ui_wallpaper
except:
    from ui.wallpaper_ui import Ui_wallpaper


class WallPaperWin(Ui_wallpaper, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 设置界面元素
        self.__init_ui()

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


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    w = WallPaperWin()
    w.show()
    app.exec()
