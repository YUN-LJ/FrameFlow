"""壁纸播放UI"""
import wallpaper
from pyside6_GUI.sub_ui.wallpaper.ThreadTask import *
from pyside6_GUI.sub_ui.wallpaper.widgetUI.rightWidget import RightWidget
from pyside6_GUI.sub_ui.wallpaper.widgetUI.leftWidget import LeftWidget


class WallPaperWin(Ui_wallpaper, QWidget):
    image_play_signal = Signal(tuple)  # 用于子线程的壁纸切换时的信号(图像名称,图像数据)
    image_erro_stop_signal = Signal(bool)  # 用于子线程的壁纸发生错误时的信号

    def __init__(self, parent=None):
        super().__init__(parent)
        if parent is None:
            parent = self
        self.__parent = parent
        self.setupUi(self)
        self.wallpaper = WallPaperPlay()  # 壁纸播放后端类
        self.uiInit()  # 界面初始化
        self.threadInit()  # 后台线程
        self.bind()  # 槽函数绑定

    def uiInit(self):
        """界面初始化"""
        # 设置按钮图标
        self.pushButton_set.setIcon(FIF.SETTING)
        self.pushButton_play.setIcon(FIF.PLAY)
        self.spinBox_time.setValue(self.wallpaper.image_time)
        # 实例化左右布局
        self.left_widget = LeftWidget(self.wallpaper, self.__parent)
        self.right_widget = RightWidget(self.wallpaper, self.__parent)
        # 实例化进度对话框
        # self.load_dialog: LoadDialog = None
        # 创建QSplitter对象，指定为水平方向（左右分栏）
        self.splitter = QSplitter(Qt.Horizontal)
        # 关闭实时更新
        # self.splitter.setOpaqueResize(False)
        # 将左右部件添加到splitter
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        # 设置初始比例,数字代表宽度像素
        self.splitter.setSizes([500, 300])
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

        def pushButton_play():
            if self.pushButton_play.text() == '播放':
                self.pushButton_play.setText('停止')
                self.pushButton_play.setIcon(FIF.PAUSE)
                self.wallpaper.start()
            else:
                self.pushButton_play.setText('播放')
                self.pushButton_play.setIcon(FIF.PLAY)
                self.wallpaper.stop()

        def comboBox_mode(index: int):
            """设置播放模式"""
            self.wallpaper.set_mode(index)
            self.left_widget.set_mode(index)

        self.image_play_signal.connect(self.dispalyImage)  # 壁纸播放信号,用于更新UI
        self.image_erro_stop_signal.connect(
            lambda: (self.pushButton_play.click(),
                     TeachingTip.create(
                         target=self.pushButton_play,
                         icon=InfoBarIcon.ERROR,
                         title='播放错误',
                         content=f'当前播放列表数量:{len(self.wallpaper.image_list)}张',
                         isClosable=True,
                         tailPosition=TeachingTipTailPosition.BOTTOM,
                         duration=3000,
                         parent=self.__parent)
                     )
        )
        self.wallpaper.image_play_signal.connect(
            lambda value: self.image_play_signal.emit(value)
        )  # 壁纸播放时发送当前播放的图片和名称
        self.wallpaper.image_erro_stop_signal.connect(
            lambda value: self.image_erro_stop_signal.emit(value)
        )  # 壁纸播放时发生错误的信号
        self.pushButton_play.clicked.connect(pushButton_play)
        self.spinBox_time.valueChanged.connect(self.wallpaper.set_time)
        self.comboBox_mode.currentIndexChanged.connect(comboBox_mode)
        # 设置为上次关闭时的模式
        self.comboBox_mode.setCurrentIndex(wallpaper.CONFIG['image_mode'])
        comboBox_mode(wallpaper.CONFIG['image_mode'])

    def dispalyImage(self, value: tuple):
        """显示当前正在播放的图片"""
        name, image = value
        self.right_widget.setImage(name, image)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.wallpaper.stop()
        self.left_widget.close()  # 主动触发关闭事件
        self.wallpaper.save_config()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    w = WallPaperWin()
    w.show()
    app.exec()


if __name__ == '__main__':
    main()
