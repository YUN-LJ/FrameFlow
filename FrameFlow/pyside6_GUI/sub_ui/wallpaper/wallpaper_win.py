"""壁纸播放UI"""
from pyside6_GUI.sub_ui.wallpaper.ThreadTask import *


class WallPaperWin(Ui_wallpaper, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        if parent is None:
            parent = self
        self.setupUi(self)
        self.uiInit()  # 界面初始化

    def uiInit(self):
        """界面初始化"""
        # 设置按钮图标
        self.pushButton_set.setIcon(FIF.SETTING)
        self.pushButton_play.setIcon(FIF.PLAY)
        # 实例化左右布局
        # self.left_widget = LeftWidget(self.__parent)
        # self.right_widget = RigetWidget(self.__parent)
        # 实例化进度对话框
        # self.load_dialog: LoadDialog = None
        # 创建QSplitter对象，指定为水平方向（左右分栏）
        self.splitter = QSplitter(Qt.Horizontal)
        # 关闭实时更新
        # self.splitter.setOpaqueResize(False)
        # 将左右部件添加到splitter
        # self.splitter.addWidget(self.left_widget)
        # self.splitter.addWidget(self.right_widget)
        # 设置初始比例,数字代表宽度像素
        self.splitter.setSizes([500, 0])
        # 设置分界线样式
        self.splitter.setStyleSheet(
            """QSplitter::handle { 
                            background-color: rgb(220,220,220); 
                            border: 1px solid rgb(220,220,220); 
                            margin: 1px;}""")
        # 将splitter添加到主布局
        self.horizontalLayout.addWidget(self.splitter)

    def threadInit(self):
        """后台线程初始化"""

    def bind(self):
        """槽函数绑定"""


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    w = WallPaperWin()
    w.show()
    app.exec()


if __name__ == '__main__':
    main()
