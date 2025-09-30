"""
获取基本数据
"""
import sys, os


def run_path() -> str:
    """
    获取启动路径
    """
    return os.path.dirname(sys.argv[0])


def ProgramStartTime(pid: int) -> float:
    """
    获取指定pid程序的启动时间
    :param pid:程序pid数值
    如果找到了返回程序的启动时间戳,否则返回None
    """
    import psutil
    pids = psutil.process_iter()
    for process in pids:
        if process.pid == pid:
            return process.create_time()
    return -1.0


def NowTime(format="%Y-%m-%d-%H-%M-%S"):
    """
    获取当前时间
    :param format:获取时间的格式
    :返回值:格式化时间
    """
    import time
    format_time = time.strftime(format, time.localtime())
    return format_time


def NTPTime(local_time=True) -> float:
    """
    通过NTP获取网络时间,无网络时返回本地时间
    :param local_time:是否允许返回本地时间,默认启用
    :return:返回时间戳
    """
    import ntplib, subprocess, time
    # 检查是否有网络
    response = subprocess.run('ping ntp.tuna.tsinghua.edu.cn -n 1', encoding='utf-8')
    if response.returncode == 0:
        # 网络同步时间,需要管理员权限
        ntp_client = ntplib.NTPClient()
        # 请求网络时间
        response = ntp_client.request('ntp.tuna.tsinghua.edu.cn', timeout=2)
        ntp_timestamp = response.tx_time
        return ntp_timestamp
    else:
        if local_time:
            return time.time()
        return -1.0


def SubDirPath(dir_path: str) -> list[str]:
    """
    获取指定目录下全部的子目录绝对路径

    :param dir_path:文件夹绝对路径
    :return:子目录绝对路径的列表
    """
    dirs_path = []
    for root, dirs, files in os.walk(dir_path):
        # print("root", root)  # 当前目录路径
        # print("dirs", dirs)  # 当前路径下所有子目录
        # print("files", files)  # 当前路径下所有非目录子文件
        if root == dir_path:
            continue
        dirs_path.append(root)  # 添加该目录下的全部目录绝对路径
    return dirs_path


def AllFilePath(dir_path: str) -> list[str]:
    """
    获取目录下全部文件的绝对路径
    :param dir_path:文件夹绝对路径
    返回值:文件列表
    """
    files_path = []
    for root, dirs, files in os.walk(dir_path):
        for i in files:
            # 添加该目录下的文件绝对路径
            files_path.append(os.path.join(root, i))
    return files_path


def TheDirFilePath(dir_path: str) -> list[str]:
    """
    获取该目录下文件的绝对路径

    :param dir_path:文件夹绝对路径
    返回值:文件列表
    """
    files_path = []
    for root, dirs, files in os.walk(dir_path):
        for i in files:
            files_path.append(os.path.join(root, i))
        return files_path


def UserPicturesPath():
    """
    获取用户图库路径
    """
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
    value, _ = winreg.QueryValueEx(key, "My Pictures")
    winreg.CloseKey(key)
    return value


def UserDesktopPath():
    """
    获取用户桌面路径
    """
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
        desktop_path, _ = winreg.QueryValueEx(key, "Desktop")
        return desktop_path


def CheckIsAdmin() -> bool:
    """
    获取程序是否以管理员身份运行
    :是 返回True , 否 返回 Flase
    """
    import ctypes
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def CheckIsStartup(name: str) -> bool:
    """
    获取程序是否开机自启动,仅适用于使用AddtoStartup函数添加的启动项

    :param name:程序全称
    """
    import winreg
    main_path = RunPath()
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run",
                         winreg.KEY_SET_VALUE,
                         winreg.KEY_ALL_ACCESS | winreg.KEY_WRITE | winreg.KEY_CREATE_SUB_KEY)  # By IvanHanloth
    try:
        # 尝试打开键
        value, _ = winreg.QueryValueEx(key, name)
        if value == main_path:
            return True
    except FileNotFoundError:
        # 如果抛出FileNotFoundError，说明键不存在
        return False


def CheckIsRun(title: str, count: int = 1, accurate: bool = True) -> bool:
    """
    判断程序是否重复运行

    :param title:进程全称包含扩展名
    :param count:主进程数量,默认1
    :param accurate:是否启用精确匹配,默认启用
    :有重复运行返回True,否则返回Flase
    """
    import psutil
    main_pid = os.getpid()  # 主线程pid
    pids = psutil.process_iter()  # 获取全部进程pid
    find_list = []
    for pid in pids:
        if accurate == True and \
                pid.pid != main_pid and \
                pid.name() == title:
            print(f'CheckIsRun精确匹配:{pid.name(), pid.pid}')
            find_list.append(pid.pid)
        elif accurate == False and \
                pid.pid != main_pid \
                and pid.name().find(title):
            print(f'CheckIsRun模糊匹配:{pid.name(), pid.pid}')
            find_list.append(pid.pid)
    if len(find_list) > count:
        return True
    else:
        return False
