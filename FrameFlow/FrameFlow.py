"""
name: 动态画框
func: 主要实现windows下更换壁纸功能
author:LJ
start_time: 2025/9/26
基于python3.12.9
"""


def process_startup_parameters():
    import sys
    from SubWidget import Config
    # 参数映射字典
    argv_dict = {
        '--hide': 'hide',
        '--terminal': 'terminal',
        '--captrue': 'captrue',
        '--debug': 'debug'
    }
    # 启动时的参数
    for key in sys.argv[1:]:
        key_func = argv_dict.get(key, False)
        if key_func:
            if key_func == 'hide':
                Config.IS_SHOW = False
            elif key_func == 'terminal':
                Config.IS_HIED_TERMINAL = False
            elif key_func == 'captrue':
                Config.IS_CAPTURE = False
            elif key_func == 'debug':
                Config.IS_DEBUG = True
                Config.IS_CAPTURE = False
                Config.IS_HIED_TERMINAL = False


def create_tray_icon(top_window):
    """创建系统托盘,必须在主窗口创建后"""
    from Fun.QtWidget import TrayIcon

    from SubWidget import Config
    tray = TrayIcon(top_window)
    Config.TRAY = tray
    tray.showClicked.connect(top_window.show)
    tray.quitClicked.connect(top_window.exit_)
    tray.show()


def create_main_window():
    """创建主窗口"""

    from SubWidget import Config
    from SubWidget import FrameFlowWin
    main_window = FrameFlowWin(False)
    main_window.notLazyLoad(False)
    if Config.IS_SHOW:
        main_window.show()
    return main_window


def start():
    # 创建主窗口
    top_window = create_main_window()
    # 创建系统托盘
    create_tray_icon(top_window)
    return top_window


if __name__ == '__main__':
    from SubAPI import StartAPI, StartEnum

    process_startup_parameters()
    start_api = StartAPI(func=start, console_level=StartEnum.LogLevel.WARNING)
    start_api.start_thread()
