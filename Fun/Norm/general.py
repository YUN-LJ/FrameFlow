"""
通用函数
"""
import sys
from . import get


def AddStartup(name: str, file_path) -> bool:
    """
    添加开机启动
    :param name:键名称
    :param file_path:键值,使用文件绝对路径
    """
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run",
                         winreg.KEY_SET_VALUE,
                         winreg.KEY_ALL_ACCESS | winreg.KEY_WRITE | winreg.KEY_CREATE_SUB_KEY)  # By IvanHanloth
    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, file_path)
    print(f"{name}已设置开机自启")
    winreg.CloseKey(key)
    return True


def RemoveStartup(name: str) -> bool:
    """
    删除开机启动
    :param name:键名称
    """
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run",
                         winreg.KEY_SET_VALUE,
                         winreg.KEY_ALL_ACCESS | winreg.KEY_WRITE | winreg.KEY_CREATE_SUB_KEY)  # By IvanHanloth
    try:
        winreg.DeleteValue(key, name)
    except FileNotFoundError:
        print(f"{name} 没有找到.")
        return False
    else:
        print(f"{name} 已移除开机自启.")
    winreg.CloseKey(key)
    return True


def AdminRunCmd(command: str):
    import ctypes
    if sys.version_info[0] == 3:
        # sys.executable退出程序,pycharm中好像会失效
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, command, None, 1)
    else:  # in python2.x
        ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(__file__),
                                            None, 1)


def KillProgram(pid_program=None, title=None) -> bool:
    """
    关闭程序

    :param title:程序全程
    :param pid_program:程序PID
    两个参数不能同时输入
    """
    import psutil, subprocess
    pids = psutil.process_iter()
    for pid in pids:
        # os.getpid()#获取主进程ID
        if title != None and pid.name() == title:
            # pid.terminate() # 以正常方式终止程序
            command = f'taskkill /PID {pid.pid} /F'
        elif pid_program != None:
            command = f'taskkill /PID {pid_program} /F'
        subprocess.run(command, shell=True)


def sync_time() -> bool:
    """
    用于将系统时间与NTP网络时间同步
    需要有管理员权限才能设置成功
    """
    import subprocess, time
    ntp_timestamp = Get.NTPTime()
    if not Get.CheckIsAdmin():
        print('sync_time:无管理员权限')
        return False
    if ntp_timestamp is not False:
        # 设置本地时间
        local_time = time.localtime(ntp_timestamp)  # 将时间本地化
        format_time = time.strftime("%Y-%m-%d-%H-%M-%S", local_time)  # 格式化时间
        format_time = format_time.split('-')
        set_date = format_time[0] + '-' + format_time[1] + '-' + format_time[2]
        set_time = format_time[3] + ':' + format_time[4] + ':' + format_time[5]
        command = f'date {set_date} && time {set_time}'
        subprocess.run(command, shell=True)
        return True
    else:
        print('sync_time:没有网络')
        return False


def stamp_to_strf(time_stamp: float, format="%Y-%m-%d-%H-%M-%S") -> str:
    """
    将时间戳转成格式化时间
    """
    import time
    local_time = time.localtime(time_stamp)  # 时间戳对象
    format_time = time.strftime(format, local_time)
    return format_time


def Print(content, prompt_start='', prompt_end='', str_long=None, color="reset"):
    """
    自定义print输出

    :param content:要打印的内容
    :param prompt_start:前缀
    :param prompt_end:后缀
    :param str_long:字符长度,常用于content是int或float类型
    :param color:颜色
    """
    from colorama import Fore, init
    init(autoreset=True)  # 每次打印完后自动重置样式
    # 定义常用颜色的 ANSI 转义码,cmd窗口下失效
    # RED = "\033[31m"; GREEN = "\033[32m";YELLOW = "\033[33m"
    # BLUE = "\033[34m";RESET = "\033[0m"  # 重置为默认样式
    # 背景颜色
    # BRESET = Back.RESET
    # BRED = Back.RED
    # BGREEN = Back.GREEN
    # BYELLOW = Back.YELLOW
    # BBLUE = Back.BLUE
    # BBKCK = Back.BLACK
    # BCYAN = Back.CYAN
    # 字体颜色
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    BKCK = Fore.BLACK
    CYAN = Fore.CYAN
    RESET = Fore.RESET
    color_dict = {'red': RED, 'green': GREEN, 'yellow': YELLOW, 'blue': BLUE, 'cyan': CYAN, 'reset': Fore.RESET}
    color = color_dict[color]
    # 覆盖上一行内容并刷新
    # \r 回到行首，用新内容覆盖旧内容
    # 格式化字符串固定长度，避免残留旧字符3d表示整型固定3个字符，6.2f表示浮点型总宽度6，含2位小数
    if isinstance(content, str):
        print(f'\r{prompt_start}{color + content}{RESET + prompt_end}', end='')
        return True
    elif isinstance(content, float) and str_long == None:
        str_long = '6.2f'
    elif isinstance(content, int) and str_long == None:
        str_long = '3d'
    print(f'\r{BRED + prompt_start}{color + content:{str_long}}{RESET + prompt_end}', end='')
    # print(f'\r{prompt_start}{color}{content:{str_long}}{RESET}{prompt_end}', end='')
    return True


def del_part_str(org_str: str, del_str: str) -> str:
    """
    删除字符串中部分字符串

    :param org_str:原字符串
    :param del_str:需要删除的字符串内容
    如果能找到需要删除的字符串内容则返回删除后的字符串
    否则返回原字符串
    """
    index_find = org_str.find(del_str)
    if index_find != -1:
        org_str = org_str[:index_find] + org_str[index_find + len(del_str):]
    return org_str
