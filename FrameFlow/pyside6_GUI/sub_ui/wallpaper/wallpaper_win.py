"""壁纸播放UI"""
from pyside6_GUI.sub_ui.wallpaper.ThreadTask import *
from pyside6_GUI.sub_ui.wallpaper.widgetUI.rightWidget import RightWidget
from pyside6_GUI.sub_ui.wallpaper.widgetUI.leftWidget import LeftWidget


class WallPaperWin(Ui_wallpaper, QWidget):
    image_play_signal = Signal(tuple)  # 用于子线程的壁纸切换时的信号(图像名称,图像数据)
    image_info_signal = Signal(pd.DataFrame)  # 用于子线程的壁纸播放功能在关键词模式下会收到当前图像的信息
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
        # 创建QSplitter对象，指定为水平方向（左右分栏）
        self.splitter = LeftandRightSplitter(self.horizontalLayout, Qt.Horizontal)
        # 将左右部件添加到splitter
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)

    def threadInit(self):
        """后台线程初始化"""
        self.thread_task = ThreadTask(self.wallpaper, self.__parent)
        self.thread_task.finished.connect(self.taskFinished)
        self.thread_task.add_task(self.thread_task.LOADUI, self.thread_task.LOADUI, None)

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

        def pushButton_choice_all():
            if self.wallpaper.isRunning:
                self.pushButton_play.click()
            state = True if self.pushButton_choice_all.text() == '全选' else False
            current_index = self.left_widget.stackedWidget.currentIndex()
            for widget in self.left_widget.all_cells.values():
                if isinstance(widget, GroupBoxCell):
                    if widget.parent == current_index:
                        widget.setState(state)
            text = '取消全选' if state else '全选'
            self.pushButton_choice_all.setText(text)

        def comboBox_mode(index: int):
            """设置播放模式"""
            self.wallpaper.set_mode(index)
            self.left_widget.set_mode(index)
            current_index = self.left_widget.stackedWidget.currentIndex()
            for widget in self.left_widget.all_cells.values():
                if isinstance(widget, GroupBoxCell):
                    if widget.parent == current_index and widget.getState():
                        self.pushButton_choice_all.setText('取消全选')
                        break
            else:
                self.pushButton_choice_all.setText('全选')

        # 壁纸播放控件连接
        self.image_play_signal.connect(self.dispalyImage)  # 壁纸播放信号,用于更新UI
        self.image_info_signal.connect(self.dispalyInfo)  # 显示图像信息
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
                         parent=self.__parent))
        )
        self.wallpaper.image_play_signal.connect(
            lambda value: self.image_play_signal.emit(value)
        )  # 壁纸播放时发送当前播放的图片路径和名称
        self.wallpaper.image_info_signal.connect(
            lambda value: self.image_info_signal.emit(value)
        )  # 壁纸播放在关键词模式下会发送当前图像的信息
        self.wallpaper.image_erro_stop_signal.connect(
            lambda value: self.image_erro_stop_signal.emit(value)
        )  # 壁纸播放时发生错误的信号

        # 子窗口的信号连接
        self.left_widget.LoadThumbSigal.connect(
            lambda value: self.thread_task.add_task(value[0], self.thread_task.LOADTHUMB, value[1])
        )  # 提交加载略缩图任务

        # 设置为上次关闭时的模式
        self.comboBox_mode.setCurrentIndex(wallpaper.CONFIG['image_mode'])
        comboBox_mode(wallpaper.CONFIG['image_mode'])

        # 主窗口控件连接
        self.pushButton_play.clicked.connect(pushButton_play)
        self.pushButton_choice_all.clicked.connect(pushButton_choice_all)
        self.spinBox_time.valueChanged.connect(self.wallpaper.set_time)
        self.comboBox_mode.currentIndexChanged.connect(comboBox_mode)

    def taskFinished(self, args):
        task_name, task_enum, task_state = args
        if task_enum == self.thread_task.LOADUI:
            self.left_widget.LoadKeyUISigal.emit(task_state[0])
        elif task_enum == self.thread_task.LOADTHUMB:
            self.left_widget.setThumb(*task_state[1])

    def dispalyImage(self, value: tuple):
        """显示当前正在播放的图片"""
        name, image = value
        self.right_widget.setImage(name, image)

    def dispalyInfo(self, value: pd.DataFrame):
        self.right_widget.setInfo(
            image_purity=value['分级'].values[0],
            image_categories=value['类别'].values[0],
            image_time=value['日期'].values[0],
            image_tags=value['标签'].values[0].split(';')
        )

    def closeEvent(self, event):
        super().closeEvent(event)
        self.thread_task.stop()  # 关闭后台任务
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
