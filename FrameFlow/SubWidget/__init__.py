"""
主程序窗口
各类子窗口的实际实现都在其内部包的destop包中
"""
from SubWidget.ImportPack import *
# 导入子窗口
from SubWidget.Home import HomeWin
from SubWidget.WallPaper import WallPaperWin
from SubWidget.SetPage import SetsWin


class FrameFlowWin(LazyLoadMS):
    keywordLoadFinishedSignal = Signal()  # 收藏夹数据加载完成
    imageinfoLoadFinishedSignal = Signal()  # 图像信息数据加载完成
    limitHTTPSignal = Signal(int)  # HTTP请求速率限制

    def __init__(self, lazy=True):
        """
        :param lazy:是否启用懒加载,默认启用
        """
        self.sub_widget_list = [
            ('主页', FIF.HOME, HomeWin, False),
            ('壁纸播放', FIF.PHOTO, WallPaperWin, False),
            ('设置', FIF.SETTING, SetsWin, True)
        ]
        # 初始化
        super().__init__(self.sub_widget_list, lazy, ':/icons/ico_main.png')
        self.setWindowTitle('FrameFlow-画框')
        self.bind()

    def bind(self):
        """事件绑定"""
        # 数据加载完成提示
        self.keywordLoadFinishedSignal.connect(
            lambda: InfoBar.success(
                title='数据加载完成', content='收藏夹数据加载完成', orient=Qt.Horizontal,
                isClosable=True, position=InfoBarPosition.TOP,
                duration=1500, parent=self))
        self.imageinfoLoadFinishedSignal.connect(
            lambda: InfoBar.success(
                title='数据加载完成', content='图像信息数据加载完成', orient=Qt.Horizontal,
                isClosable=True, position=InfoBarPosition.TOP,
                duration=1500, parent=self))

        # 创建节流定时器
        self._limit_http_timer = debouncer_timer(self._limitHTTPSlot)
        self.limitHTTPSignal.connect(lambda rate_limit: self._limit_http_timer.start(1000))

        IMAGE_INFO.load_callback(lambda _: self.imageinfoLoadFinishedSignal.emit())
        KEY_WORD.load_callback(lambda _: self.keywordLoadFinishedSignal.emit())
        GlobalValue.GLOBAL_ASYNC_HTTP_MANAGE.rate_limit_signal.connect(self.limitHTTPSignal.emit)

    def _limitHTTPSlot(self):
        """HTTP速率限制提示（通过debouncer_timer节流）"""
        if self.isVisible():
            InfoBar.new(
                icon=InfoBarIcon.WARNING, title='速率已达上限',
                content=f'速率已达上限 {GlobalValue.GLOBAL_ASYNC_HTTP_MANAGE.rate_limit}',
                orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP,
                duration=1000, parent=self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        TopWindowSignal.top_signal.resizeSignal.emit()

    def closeEvent(self, event):
        # 重写关闭函数,只隐藏窗口不退出
        event.ignore()
        self.hide()

    def exit_(self):
        """退出"""
        self.hide()
        Config.TRAY.hide()
        self.load_sub_widget.page_close()
        QApplication.instance().exit()

    def restart(self, *argv):
        Terminal.admin_run(f'{Get.run_file()} {' '.join(argv)}')
        self.exit_()

    def show(self):
        if not self.isMaximized():
            self.resize(1000, 600)
            # 设置窗口居中
            rect = QApplication.instance().primaryScreen().availableGeometry()
            w, h = rect.width(), rect.height()
            self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        # 设置主题色
        # setThemeColor('#7da3d3')
        super().show()
