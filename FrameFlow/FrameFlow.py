"""
name: 动态画框
func: 主要实现windows下更换壁纸功能
author:LJ
start_time: 2025/9/26
基于python3.12.9
"""


def process_startup_parameters():
    import sys
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
                print('----调试模式----')
    if Config.IS_HIED_TERMINAL:
        hide_python_terminal()


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
    main_window.notLazyLoad(False)
    if Config.IS_SHOW:
        main_window.show()


def start():
    app = QApplication([])
    Config.APP = app
    # 创建主窗口
    create_main_window()
    # 创建系统托盘
    create_tray_icon()
    # 进入事件循环
    app.exec()


def stop():
    AppCore().stopWorkFlow()
    DataManage.stop()
    FileBase(GlobalValue.image_cache_dir).delete()


if __name__ == '__main__':
    from Fun.BaseTools.Terminal import hide_python_terminal, CapturePythonTerminal
    from Fun.BaseTools.Get import get_threads, monitor_threads
    from ImportFile import Config

    # 处理启动参数
    process_startup_parameters()
    if Config.IS_HIED_TERMINAL:
        hide_python_terminal()

    from ImportFile.ImportPack import *
    from SubWidget import FrameFlowWin

    # 启用输出捕获
    captrue_python_terminal = CapturePythonTerminal()
    Config.CAPTURE_PYTHON_TERMINAL = captrue_python_terminal
    if Terminal.is_python_terminal_visible() == -1:  # 控制台不可见时启用捕获
        captrue_python_terminal.start(GlobalValue.log_path)
    if Config.IS_DEBUG:
        try:
            captrue_python_terminal.stop()
            start()
        except Exception as e:
            print(e)
            stop()
    else:
        start()
        stop()
    # 打印当前剩余线程
    for index, thread in enumerate(get_threads()):
        print(f'{index} - {thread.name:30s} | daemon={thread.daemon}')
    print(f'程序已退出')
