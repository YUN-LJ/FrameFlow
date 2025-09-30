"""
有关PySide6类的高级封装操作
"""
from Fun import Get
from PySide6 import QtCore, QtGui, QtWidgets


def Get_QCheckBox_State(obj_list: list[QtWidgets.QCheckBox]) -> list[(QtWidgets.QCheckBox, bool)]:
    """
    批量获取QCheckBox的状态
    :param obj_list:对象列表
    :return :返回所有checkBox的状态list[('QtWidgets.QCheckBox',bool)]
    """
    all_state = [(obj, obj.isChecked()) for obj in obj_list]
    return all_state


def Get_QLineEdit_Text(obj_list: list[QtWidgets.QLineEdit]) -> list[(QtWidgets.QLineEdit, str)]:
    """
    批量获取QLineEdit的文本内容
    :param obj_list:对象列表
    :return :返回所有QLineEdit的文本内容list[(QtWidgets.QLineEdit,str)]
    """
    all_text = [(obj, obj.text()) for obj in obj_list]
    return all_text


def QPushButton_Bind(obj_list: list[(QtWidgets.QPushButton, 'def_name')]) -> bool:
    """
    批量绑定QPushButton
    :param obj_list:对象列表元组[(对象,绑定函数名)]
    :return :bool
    """
    for obj, def_name in obj_list:
        obj.clicked.connect(def_name)
    return True


def Get_QTextEdit_Text(obj_list: list[QtWidgets.QTextEdit]) -> list[(QtWidgets.QTextEdit, str)]:
    """
    批量获取QTextEdit的文本内容
    :param obj_list:对象列表
    :return :返回所有QTextEdit的文本内容list[(QtWidgets.QTextEdit,str)]
    """
    all_text = [(obj, obj.toPlainText()) for obj in obj_list]
    return all_text


def GetExistDir(caption: str = '', dir_path: str = Get.RunPath()) -> str:
    """
    用于选择单个目录,外部调用时需要用lambda :方法

    :param caption:窗口标题
    :param dir_path:初始目录,默认为文件启动路径
    :return dir:str
    """
    dir = QtWidgets.QFileDialog.getExistingDirectory(parent=None,  # 父对象
                                                     caption=caption,  # 对话框标题提示词
                                                     dir=dir_path,  # 默认显示目录
                                                     options=QtWidgets.QFileDialog.ShowDirsOnly  # 只显示文件夹
                                                     )
    return dir


def GetExistFile(caption: str = '', dir_path: str = Get.RunPath(), ext=None) -> list[str]:
    """
    用于选择单个文件,外部调用时需要用lambda :方法
    :param caption:窗口标题
    :param dir_path:初始目录,默认为文件启动路径
    :param ext:设置文件的扩展名
    :return file:list[str]
    """
    # ext="视频(*.mp4;*.wmv;*.flv;*.avi);;文本(*.txt);;All file(*)"
    file, _ = QtWidgets.QFileDialog.getOpenFileNames(None,  # 父对象
                                                     caption,  # 窗口标题
                                                     dir_path,  # 默认启动路径
                                                     ext  # 选择格式
                                                     )
    return file


def GetListWidgetAllValue(listwidget: QtWidgets.QListWidget) -> list[str]:
    # 获取listwidget对象全部内容
    count = listwidget.count()  # 获取全部项目数量
    # 根据索引获取项目对象
    value = [listwidget.item(i).text() for i in range(count)]
    return value


def DelListWidgetcurrentItem(listwidget: QtWidgets.QListWidget):
    # 返回当前选中的项目
    item = listwidget.currentItem()
    # 获取该项目的索引值
    index = listwidget.row(item)
    # 根据索引值删除该项目
    listwidget.takeItem(index)


def AppendListWidgetitems(items: list, listwidget: QtWidgets.QListWidget):
    # 添加新的条目,名称重复将不添加
    allitems = GetListWidgetAllValue(listwidget)
    new_items = (item for item in items if item and item not in allitems)
    listwidget.addItems(new_items)


def EmbeddedWindow(title: str, window: QtWidgets, accurate: bool = True):
    """
    将窗口嵌入到pyside6窗口中

    :param title:查找的窗口标题str,由于pyside6嵌入窗口时不能使用大写字母
    :param window:需要嵌入的窗口对象QtWidgets
    :param accurate:是否开启精确查找bool
    :return :bool
    """
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
            print(f'Pyside6Mod精确句柄:{hwnd}')
            print(f'窗口名称:{win32gui.GetWindowText(hwnd)}')
            break
        elif accurate == False and \
                win32gui.GetWindowText(hwnd).find(title) != -1:  # 需要优化
            pid = win32process.GetWindowThreadProcessId(hwnd)[1]
            # print('找到的PID:', pid)
            print(f'Pyside6Mod模糊句柄:{hwnd}')
            print(f'窗口名称:{win32gui.GetWindowText(hwnd)}')
            break
        else:
            hwnd = 0
    if hwnd == 0:  # 没有匹配到窗口
        return False
    # 根据窗口句柄嵌入到pyqt5界面中
    consolewindow = QtGui.QWindow.fromWinId(hwnd)
    # 创建一个Qwiget用于容纳consolewindow
    pyside6window = QtWidgets.QWidget.createWindowContainer(consolewindow)
    # 创建新的容器用于容纳widget
    Layout = QtWidgets.QHBoxLayout(window)
    Layout.setContentsMargins(0, 0, 0, 0)
    Layout.addWidget(pyside6window)
    return True


class ReMouseWidget(QtWidgets.QWidget):
    # 重写了鼠标响应事件
    def __init__(self, ):
        # 继承QWidget父对象
        super(ReMouseWidget, self).__init__()
        # 鼠标相对窗口的位置(x,y)
        self.__startPos = None
        # 鼠标移动的距离(x,y)
        self.__wmGap = None
        # 屏幕边界坐标
        self.screen_x_left = None
        self.screen_x_right = None
        self.screen_y_top = None
        self.screen_y_bottom = None

    def mousePressEvent(self, event):
        # 鼠标按下时，记录鼠标相对窗口的位置
        if event.button() == QtCore.Qt.LeftButton:
            # event.pos() 鼠标相对窗口的位置
            # event.globalPos() 鼠标在屏幕的绝对位置
            self.__startPos = event.pos()

    def mouseMoveEvent(self, event):
        # 鼠标移动时，移动窗口跟上鼠标；同时限制窗口位置，不能移除主屏幕
        # event.pos()减去最初相对窗口位置，获得移动距离(x,y)
        self.__wmGap = event.pos() - self.__startPos
        # 移动窗口,保持鼠标与窗口的相对位置不变
        final_pos = self.pos() + self.__wmGap
        # 检查是否移除了当前主屏幕
        # 左方界限
        if self.frameGeometry().topLeft().x() + self.__wmGap.x() <= 0:
            final_pos.setX(0)
        # 上方界限
        if self.frameGeometry().topLeft().y() + self.__wmGap.y() <= 0:
            final_pos.setY(0)
        # 右方界限
        if self.frameGeometry().bottomRight().x() + self.__wmGap.x() >= 1920/1.25:
            final_pos.setX(1920/1.25 - self.width())
        # 下方界限
        if self.frameGeometry().bottomRight().y() + self.__wmGap.y() >= 1080/1.24:
            final_pos.setY(1080/1.24 - self.height())
        # 移动窗口
        self.move(final_pos)

    def mouseReleaseEvent(self, event):
        # 鼠标释放后重置
        if event.button() == QtCore.Qt.LeftButton:
            self.__startPos = None
            self.__wmGap = None
        if event.button() == QtCore.Qt.RightButton:
            self.__startPos = None
            self.__wmGap = None

    def ScreenLim(self):
        """获取屏幕边界,支持多屏"""
        # 获取显示器数量
        self.desktop = QtWidgets.QApplication.screens()
        # 获取各个屏幕的边界坐标
        self.screen_x = []
        self.screen_y = []
        # x [0, 1920, -1920, 0]
        # y [0, 1080, 0, 1200]
        for screen in self.desktop:
            geometry = screen.geometry()
            # device_pixel_ratio = screen.devicePixelRatio()#屏幕缩放比
            self.screen_x.append(geometry.x())
            # self.screen_x.append(geometry.x() + geometry.width() * device_pixel_ratio)
            self.screen_x.append(geometry.x() + geometry.width())
            self.screen_y.append(geometry.y())
            # self.screen_y.append(geometry.y() + geometry.height() * device_pixel_ratio)
            self.screen_y.append(geometry.y() + geometry.height())

    def enterEvent(self, event):
        # 鼠标进入窗口时
        pass

    def leaveEvent(self, event):
        # 鼠标离开窗口
        pass


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    widget = ReMouseWidget()
    widget.show()
    app.exec()
