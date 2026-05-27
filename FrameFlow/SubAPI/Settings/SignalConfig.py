"""信号配置"""
# PySide6原生组件
from PySide6.QtCore import Signal, QObject


class TopWindowSignal:
    """顶层窗口对外暴露的信号"""

    class TopSignal(QObject):
        """顶层窗口信号"""
        resizeSignal = Signal()  # 缩放信号

    class HomeSignal(QObject):
        """主页窗口信号"""
        switchPageSignal = Signal(object)  # 发送需要切换页面的对象即可切换到指定页面,QWidget|int

    top_signal = TopSignal()
    home_signal = HomeSignal()


class WallHavenSignal:
    """WallHaven功能对外暴露的信号"""

    class SearchSignal(QObject):
        """搜索功能对外暴露的信号"""
        searchSignal = Signal(object)  # 发送搜索任务 SearchTask
        startSignal = Signal(object)  # 搜索开始 SearchTask
        progressSignal = Signal(object)  # 搜索进度 SearchTask
        finishedSignal = Signal(object)  # 搜索完成 SearchTask
        stopSignal = Signal(object)  # 搜索停止 SearchTask
        refreshViewSignal = Signal()  # 刷新视图

        def __init__(self):
            super().__init__()

    class DownloadSignal(QObject):
        """下载功能对外暴露的信号"""
        refreshViewSignal = Signal()  # 刷新视图

        def __init__(self):
            super().__init__()

    class LikeSignal(QObject):
        """收藏功能对外暴露的信号"""
        startSignal = Signal(object)  # 更新任务开始 SerialUpdateWorkFlow
        progressSignal = Signal(object)  # 更新进度 TaskProgress
        finishSignal = Signal(object)  # 更新任务结束 SerialUpdateWorkFlow
        stopSignal = Signal(object)  # 更新任务结束/停止 SerialUpdateWorkFlow

        def __init__(self):
            super().__init__()

    search_signal = SearchSignal()
    download_signal = DownloadSignal()
    like_signal = LikeSignal()


class WallPaperSignal:
    """壁纸功能对外暴露的信号"""

    class MainSignal(QObject):
        """主窗口对外暴露的信号"""
        startPlaySignal = Signal()  # 播放开始信号
        pausePlaySignal = Signal(bool)  # 播放停止信号
        playImageSignal = Signal(object)  # 播放的图片信号ImageProcessTask

    main_signal = MainSignal()
