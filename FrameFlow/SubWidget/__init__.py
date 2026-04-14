from ImportFile.ImportPack import *
from ImportFile import Config

# 导入子窗口
from SubWidget.Home import HomeWin
from SubWidget.WallPaper import WallPaperWin
from SubWidget.Sets import SetsWin


class FrameFlowWin(LazyLoadMS):
    resizeSignal = Signal(bool)  # 缩放信号
    keywordLoadFinishedSignal = Signal()  # 收藏夹数据加载完成
    imageinfoLoadFinishedSignal = Signal()  # 图像信息数据加载完成

    def __init__(self, lazy=True):
        """
        :param lazy:是否启用懒加载,默认启用
        """
        Config.TOP_WINDOWS = self
        self.sub_widget_list = [
            ('主页', FIF.HOME, HomeWin, False),
            ('壁纸播放', FIF.PHOTO, WallPaperWin, False),
            ('设置', FIF.SETTING, SetsWin, True)
        ]
        self.initTheme()
        # 初始化
        super().__init__(self.sub_widget_list, lazy, ':/icons/ico_main.png')
        self.setWindowTitle('FrameFlow-画框')
        self.bind()

    @staticmethod
    def initTheme():
        """初始化主题"""
        # 获取系统主题
        system_theme = darkdetect.theme()  # 返回字符串 'Dark' 或 'Light'
        if system_theme == 'Dark':
            Config.CURRENT_THEME = 'Dark'
            setTheme(Theme.DARK)
        else:
            Config.CURRENT_THEME = 'Light'
            setTheme(Theme.LIGHT)
        # 全局主题
        # 只能获取 Windows 和 macOS 的主题色
        if sys.platform in ["win32", "darwin"]:
            # save=True时对后续创建的对象也会生效,否则只对当前存在的对象生效
            setThemeColor(getSystemAccentColor(), save=False, lazy=True)

    def bind(self):
        """事件绑定"""
        AppCore().addSignal('resize', self.resizeSignal)
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
        ImageInfo.load_callback(lambda _: self.imageinfoLoadFinishedSignal.emit())
        KeyWord.load_callback(lambda _: self.keywordLoadFinishedSignal.emit())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resizeSignal.emit(True)

    def closeEvent(self, event):
        # 重写关闭函数,只隐藏窗口不退出
        event.ignore()
        self.hide()

    def exit_(self):
        """退出"""
        self.hide()
        Config.TRAY.hide()
        self.load_sub_widget.page_close()
        Config.APP.exit()

    def restart(self, *argv):
        Terminal.admin_run(f'{Get.run_file()} {' '.join(argv)}')
        self.exit_()

    def show(self):
        if not self.isMaximized():
            self.resize(1000, 600)
            # 设置窗口居中
            rect = Config.APP.primaryScreen().availableGeometry()
            w, h = rect.width(), rect.height()
            self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        # 设置主题色
        # setThemeColor('#7da3d3')
        super().show()
