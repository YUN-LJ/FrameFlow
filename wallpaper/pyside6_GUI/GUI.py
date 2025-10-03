# 图形库
from PySide6.QtWidgets import QHBoxLayout, QFrame
from PySide6.QtGui import QIcon
# 美化库
from qfluentwidgets import NavigationItemPosition, MSFluentWindow, setThemeColor
from qfluentwidgets import FluentIcon as FIF

# 导入资源文件
try:
    from . import res
except:
    import res

ICO_PATH = {
    '主页': FIF.HOME,
    '壁纸播放': FIF.PHOTO,
    '设置': FIF.SETTING,
}


class PySide6GUI(MSFluentWindow):
    """ 主界面 """

    def __init__(self):
        super().__init__()
        self.resize(1000, 600)
        self.setWindowIcon(QIcon(f":/icons/ico_main.png"))
        self.setWindowTitle('FrameFlow-画框')

        # 设置窗口居中
        rect = app.primaryScreen().availableGeometry()
        w, h = rect.width(), rect.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        # 设置主题色
        setThemeColor('#7da3d3')

        # 列出全部子窗口
        self.sub_widget()

        # 添加窗口
        self.initNavigation()

        # 切换至主页
        # self.stackedWidget.currentChanged.connect(lambda index: AddPage(self.stackedWidget.currentWidget(), index))

    def sub_widget(self):
        self.subwidget = {
            '主页': Widget('主页', self),
            '壁纸播放': Widget('壁纸播放', self),
            '设置': Widget('设置', self),
        }

    def initNavigation(self):
        # 子窗口
        for text, widget in self.subwidget.items():
            if text == '设置':
                continue
            self.addSubInterface(widget, ICO_PATH[text], text, position=NavigationItemPosition.SCROLL)

        # 设置
        self.addSubInterface(self.subwidget['设置'], ICO_PATH['设置'], '设置', position=NavigationItemPosition.BOTTOM)

    def show(self):
        self.stackedWidget.setCurrentIndex(0)
        super().show()


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)

        # 必须给子界面设置全局唯一的对象名
        self.setObjectName(text.replace(' ', '-'))


def start_GUI():
    from PySide6.QtWidgets import QApplication
    global app
    app = QApplication([])
    GUI = PySide6GUI()
    GUI.show()
    app.exec()


if __name__ == '__main__':
    start_GUI()
