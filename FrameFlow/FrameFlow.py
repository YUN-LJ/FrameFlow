"""
name: 动态画框
func: 主要实现windows下更换壁纸功能
author:LJ
start_time: 2025/9/26
基于python3.12.9
"""
from ImportFile.ImportPack import *
from ImportFile import Config
from SubWidget import FrameFlowWin


def process_startup_parameters():
    is_show = True
    # 参数映射字典
    argv_dict = {
        '--hide': 'hide',
    }

    # 启动时的参数
    for key in sys.argv[1:]:
        key_func = argv_dict.get(key, False)
        if key_func:
            if key_func == 'hide':
                is_show = False
            else:
                key_func()

    if is_show:
        Config.TOP_WINDOWS.show()


def create_tray_icon():
    """创建系统托盘,必须在主窗口创建后"""
    top_window: FrameFlowWin = Config.TOP_WINDOWS
    tray = TrayIcon(top_window)
    Config.TRAY = tray
    tray.showClicked.connect(top_window.show)
    tray.quitClicked.connect(top_window.exit_)
    tray.show()


def create_main_window():
    """创建主窗口"""
    main_window = FrameFlowWin(False)
    main_window.pageChange(2)  # 提前加载设置页面,快速隐藏启动窗口
    QTimer.singleShot(0, lambda: main_window.pageChange(0))  # 延迟加载主页


def start_GUI():
    app = QApplication([])
    Config.APP = app
    # 创建主窗口
    create_main_window()
    # 创建系统托盘
    create_tray_icon()
    # 处理启动参数
    process_startup_parameters()
    # 进入事件循环
    app.exec()


if __name__ == '__main__':
    file.del_file(GlobalValue.image_cache_dir)
    start_GUI()
    AppCore().stopWorkFlow()
    DataManage.stop()
