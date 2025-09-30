"""
有关PyQt5类的高级封装操作
"""
from . import Get
from PyQt5 import QtWidgets, QtGui


def GetExistDir(initialpath=Get.RunPath()):
    """
    用于选择单个目录

    :param initialpath:初始目录,默认为文件启动路径
    :return selected_dirs:str
    """
    dir = QtWidgets.QFileDialog.getExistingDirectory(None, "请选择文件夹路径", initialpath)
    dir = dir.replace("/", "\\")
    if dir == '':
        return None
    return dir


def GetExistDirs_old(initialpath=Get.RunPath()):
    """
    用于选择多个目录

    :param initialpath:初始目录,默认为文件启动路径
    :return selected_dirs:list
    """
    from PyQt5.QtCore import QUrl, QStandardPaths
    import ctypes
    from ctypes import wintypes
    # 创建文件对话框
    dialog = QtWidgets.QFileDialog()
    dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)  # 只显示目录
    dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)  # 禁用原生对话框(否则无法多选)
    dialog.setWindowTitle("选择多个目录")

    # 获取目录选择视图并设置多选
    tree_view = dialog.findChild(QtWidgets.QTreeView)
    if tree_view:
        tree_view.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection)  # 支持Shift/Ctrl多选

    list_view = dialog.findChild(QtWidgets.QListView)
    if list_view:
        list_view.setSelectionMode(QtWidgets.QListView.ExtendedSelection)

    # Windows系统：获取所有磁盘驱动器作为根目录
    # 调用Windows API获取所有逻辑驱动器
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel32.GetLogicalDriveStringsW.argtypes = [wintypes.DWORD, wintypes.LPWSTR]

    buf = ctypes.create_unicode_buffer(1024)
    length = kernel32.GetLogicalDriveStringsW(ctypes.sizeof(buf), buf)
    drives = [buf[i:i + 4].rstrip('\x00') for i in range(0, length, 4) if buf[i]]
    # 添加所有驱动器到侧边栏
    custom_urls = [QUrl.fromLocalFile(drive) for drive in drives]

    # 获取系统常用目录（使用QStandardPaths自动适配不同操作系统）
    # 图库目录
    pictures_dir = QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)
    # 下载目录
    download_dir = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
    # 文档目录
    documents_dir = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
    # 桌面目录
    desktop_dir = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)

    # 将目录转换为QUrl格式(setSidebarUrls需要QUrl列表)
    custom_urls.extend([
        QUrl.fromLocalFile(desktop_dir),
        QUrl.fromLocalFile(download_dir),
        QUrl.fromLocalFile(pictures_dir),
        QUrl.fromLocalFile(documents_dir),
    ])

    # 设置左侧侧边栏目录
    dialog.setSidebarUrls(custom_urls)

    # 显示对话框并获取结果
    if dialog.exec_():
        selected_dirs = dialog.selectedFiles()
        return selected_dirs


def GetExistDirs(initialpath=None):
    """
    用于选择多个目录，支持搜索功能（修复搜索无结果问题）

    :param initialpath: 初始目录，默认为当前脚本所在目录
    :return: 选中的目录列表和下拉框当前内容
    """
    import os
    from PyQt5 import QtCore, QtWidgets
    from PyQt5.QtCore import QUrl, QStandardPaths, QRegExp
    import ctypes
    from ctypes import wintypes

    # 设置默认初始路径为当前脚本所在目录
    if initialpath is None:
        initialpath = os.path.dirname(os.path.abspath(__file__))

    # 创建自定义对话框
    dialog = QtWidgets.QFileDialog()
    dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
    dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
    dialog.setWindowTitle("选择多个目录")
    dialog.setDirectory(initialpath)
    dialog.resize(1000, 400)

    # 先显示一次确保布局初始化
    dialog.show()
    dialog.hide()

    # 获取目录选择视图并设置多选
    tree_view = dialog.findChild(QtWidgets.QTreeView)
    list_view = dialog.findChild(QtWidgets.QListView)
    original_model = None

    # 确保获取到正确的模型（QFileSystemModel）
    if tree_view:
        tree_view.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection)
        original_model = tree_view.model()
        # 启用目录模型的名称过滤功能
        if hasattr(original_model, 'setNameFilters'):
            original_model.setNameFilterDisables(False)  # 不显示不匹配的项

    if list_view:
        list_view.setSelectionMode(QtWidgets.QListView.ExtendedSelection)

    # 创建搜索控件
    search_input = QtWidgets.QLineEdit()
    search_input.setPlaceholderText("搜索目录...")
    search_input.setClearButtonEnabled(True)
    search_input.setMinimumWidth(200)

    search_btn = QtWidgets.QPushButton("🔍搜索")
    # search_btn.setIcon(dialog.style().standardIcon(QtWidgets.QStyle.SP_FileIcon))

    # 添加搜索控件到布局
    main_layout = dialog.layout()
    if main_layout:
        top_layout = None
        for i in range(main_layout.count()):
            item = main_layout.itemAt(i)
            if isinstance(item.layout(), QtWidgets.QHBoxLayout):
                top_layout = item.layout()
                break

        if top_layout:
            top_layout.addSpacing(10)
            top_layout.addWidget(QtWidgets.QLabel("搜索:"))
            top_layout.addWidget(search_input)
            top_layout.addWidget(search_btn)
            top_layout.addStretch()
        else:
            new_top_layout = QtWidgets.QHBoxLayout()
            while main_layout.count():
                item = main_layout.takeAt(0)
                if item.widget():
                    new_top_layout.addWidget(item.widget())
                elif item.layout():
                    new_top_layout.addLayout(item.layout())

            new_top_layout.addSpacing(10)
            new_top_layout.addWidget(QtWidgets.QLabel("搜索:"))
            new_top_layout.addWidget(search_input)
            new_top_layout.addWidget(search_btn)
            new_top_layout.addStretch()

            main_layout.addLayout(new_top_layout)
            main_layout.addStretch()

    # 修复搜索无结果问题：使用文件系统模型的名称过滤
    def filter_directories(text):
        if not tree_view or not original_model or not hasattr(original_model, 'setNameFilters'):
            return

        # 清除之前的筛选
        original_model.setNameFilters([])  # 清空过滤规则
        tree_view.setModel(original_model)

        if not text.strip():  # 空文本时显示所有目录
            return

        # 使用QFileSystemModel的名称过滤功能（更适合目录筛选）
        # 匹配包含关键词的目录（支持通配符）
        filter_text = f"*{text}*"
        original_model.setNameFilters([filter_text])

    # 绑定搜索事件
    search_btn.clicked.connect(lambda: filter_directories(search_input.text()))
    search_input.returnPressed.connect(lambda: filter_directories(search_input.text()))

    # 配置Windows驱动器和常用目录
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel32.GetLogicalDriveStringsW.argtypes = [wintypes.DWORD, wintypes.LPWSTR]
    buf = ctypes.create_unicode_buffer(1024)
    length = kernel32.GetLogicalDriveStringsW(ctypes.sizeof(buf), buf)
    drives = [buf[i:i + 4].rstrip('\x00') for i in range(0, length, 4) if buf[i]]
    custom_urls = [QUrl.fromLocalFile(drive) for drive in drives]

    pictures_dir = QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)
    download_dir = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
    documents_dir = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
    desktop_dir = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)

    custom_urls.extend([
        QUrl.fromLocalFile(desktop_dir),
        QUrl.fromLocalFile(download_dir),
        QUrl.fromLocalFile(pictures_dir),
        QUrl.fromLocalFile(documents_dir),
    ])

    dialog.setSidebarUrls(custom_urls)

    # 显示对话框并获取结果
    selected_dirs = []
    if dialog.exec_():
        selected_dirs = dialog.selectedFiles()

    return selected_dirs


def GetExistFile(initialpath=Get.RunPath(), ext=None):
    """
    用explorer打开文件选择窗口
    :param initialpath:设置初始目录
    :param ext:设置文件的扩展名
    """
    # ext="视频(*.mp4;*.wmv;*.flv;*.avi);;文本(*.txt);;All file(*)"
    file, _ = QtWidgets.QFileDialog.getOpenFileNames(None, "请选择文件路径", initialpath, ext)
    if file == []:
        return None
    file = file[0].replace("/", "\\")
    return file


def GetListWidgetAllValue(listwidget):
    # 获取listwidget对象全部内容
    count = listwidget.count()  # 获取全部项目数量
    # 根据索引获取项目对象
    value = [listwidget.item(i).text() for i in range(count)]
    return value


def DelListWidgetcurrentItem(listwidget):
    # 返回当前选中的项目
    item = listwidget.currentItem()
    # 获取该项目的索引值
    index = listwidget.row(item)
    # 根据索引值删除该项目
    listwidget.takeItem(index)


def AppendListWidgetitems(items, listwidget):
    # 添加新的条目,名称重复将不添加
    allitems = GetListWidgetAllValue(listwidget)
    new_items = [item for item in items if item not in allitems]
    listwidget.addItems(new_items)


def EmbeddedWindow(title, window, accurate=True):
    # 将窗口嵌入到pyqt5界面中,需要传入窗口标题和qwidget对象
    # accurate是否精确查找
    import win32gui, win32process
    # 获取窗口句柄
    # windowhandle = win32gui.FindWindowEx(0, 0,
    #                                     "ConsoleWindowClass",#类名
    #                                     r'管理员: 命令提示符 - H:\Python\simple\simpleModular\python3.9\Scripts\python.exe   H:\Python\simple\simpleModular\AutoSetWallpaper.py')#窗口标题
    # print('windowhandle',windowhandle)
    hwnd_list = []

    def callback(hwnd, extra):
        hwnd_list.append(hwnd)

    # 历遍全部窗口,callback是回调函数
    win32gui.EnumWindows(callback, None)
    # # 获取当前时间,用于模糊匹配时捕获启动时间相近的窗口句柄
    # start_time = time.time()
    # print('EmbeddedWindow启动时间:',start_time)
    # # 主线程PID
    # pid_main = os.getpid()
    # print('主线程PID:', pid_main)
    # 根据窗口标题寻找该窗口的句柄
    for hwnd in hwnd_list:
        # 获取程序pid
        # pid = win32process.GetWindowThreadProcessId(hwnd)[1]
        # 根据窗口句柄获取程序的窗口标题,精确匹配模式
        if accurate == True and win32gui.GetWindowText(hwnd) == title:
            print(f'PyQt5Mod精确句柄:{hwnd}')
            print(f'窗口名称:{win32gui.GetWindowText(hwnd)}')
            break
        elif accurate == False and \
                win32gui.GetWindowText(hwnd).find(title) != -1:  # 需要优化
            pid = win32process.GetWindowThreadProcessId(hwnd)[1]
            # print('找到的PID:', pid)
            print(f'PyQt5Mod模糊句柄:{hwnd}')
            print(f'窗口名称:{win32gui.GetWindowText(hwnd)}')
            break
        else:
            hwnd = 0
    if hwnd == 0:  # 没有匹配到窗口
        return False
    # 根据窗口句柄嵌入到pyqt5界面中
    consolewindow = QtGui.QWindow.fromWinId(hwnd)
    # 创建一个Qwiget用于容纳consolewindow
    pyqt5window = QtWidgets.QWidget.createWindowContainer(consolewindow)
    # 创建新的容器用于容纳widget
    Layout = QtWidgets.QHBoxLayout(window)
    Layout.setContentsMargins(0, 0, 0, 0)
    Layout.addWidget(pyqt5window)
    print('EmbeddedConsoleSuccess')
    return True



