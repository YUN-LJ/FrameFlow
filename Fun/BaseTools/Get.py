"""常用值获取"""
import sys, os


def run_dir() -> str:
    """
    获取启动所在目录
    """
    return os.path.dirname(sys.argv[0])


def run_file() -> str:
    """
    获取启动路径
    """
    return sys.argv[0]


def python_path() -> str:
    """获取当前python解释器路径"""
    return sys.executable


def python_cmd_hwnd() -> int:
    """获取Python解释器终端句柄"""
    import ctypes
    return ctypes.windll.kernel32.GetConsoleWindow()


def find_hwnd(target_inf: str | int, class_name: list[str] = None, accurate: bool = True) -> int:
    """
    查找窗口句柄

    :param target_inf:查找的窗口标题str或进程pid
    :param widget:需要嵌入的窗口对象QWidget
    :param class_name:窗口所属的类,[cmd:'ConsoleWindowClass',终端:'CASCADIA_HOSTING_WINDOW_CLASS']
    :param accurate:是否开启精确查找bool
    :return :窗口句柄hwnd
    """
    # 主线程PID
    pid_main = os.getpid()

    # 历遍全部窗口,callback是回调函数(即每次查找一个窗口句柄时执行的操作)
    hwnd_list = []  # 找到的窗口句柄,按理来说只有一个,如果有多个则取最后一个

    def callback(hwnd, extra):
        # extra是EnumWindows的第二个参数
        pid = win32process.GetWindowThreadProcessId(hwnd)[1]  # 当前窗口pid,第一个元素是线程id也就是tid
        if pid == pid_main:
            return False
        # 如果输入的target_inf是pid
        elif pid == extra:
            hwnd_list.append(hwnd)
            return True
        # 如果输入的target_inf是窗口标题
        elif isinstance(extra, str):
            window_title = win32gui.GetWindowText(hwnd)  # 当前窗口标题
            if accurate == True and window_title == extra:  # 精确查找
                window_class_name = win32gui.GetClassName(hwnd)  # 当前窗口类别
                if class_name is None:
                    hwnd_list.append((hwnd, window_title, window_class_name, pid))
                else:
                    if window_class_name in class_name:
                        hwnd_list.append((hwnd, window_title, window_class_name, pid))
            elif accurate == False and window_title.find(extra) != -1:  # 模糊查询
                window_class_name = win32gui.GetClassName(hwnd)  # 当前窗口类别
                if class_name is None:
                    hwnd_list.append((hwnd, window_title, window_class_name, pid))
                else:
                    if window_class_name in class_name:
                        hwnd_list.append((hwnd, window_title, window_class_name, pid))

    win32gui.EnumWindows(callback, target_inf)

    if hwnd_list == []:  # 没有匹配到窗口
        return False
    else:
        hwnd = hwnd_list[-1]
    return hwnd


def program_start_time(pid: int) -> float:
    """
    获取指定pid程序的启动时间

    :param pid:程序pid
    如果找到了返回程序的启动时间戳,否则返回-1.0
    """
    import psutil
    pids = psutil.process_iter()
    for process in pids:
        if process.pid == pid:
            return process.create_time()
    return -1.0


def main_pid() -> int:
    """返回主进程PID"""
    return os.getpid()
