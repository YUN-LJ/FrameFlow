"""
通用函数
"""
import sys
from . import get


def add_start_user(name: str, file_path: str) -> bool:
    """
    添加开机启动,用户登录时才会启动(普通权限)

    :param name:键名称
    :param file_path:键值,使用文件绝对路径
    """
    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, key_path,
        winreg.KEY_SET_VALUE,
        winreg.KEY_ALL_ACCESS | winreg.KEY_WRITE | winreg.KEY_CREATE_SUB_KEY)  # By IvanHanloth
    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, file_path)
    print(f"{name}已设置开机自启")
    winreg.CloseKey(key)
    return True


def add_start_system(name: str, file_path: str) -> bool:
    """
    添加开机启动,系统启动时启动(管理员权限)

    :param name:键名称
    :param file_path:键值,使用文件绝对路径
    """
    import winreg
    try:
        # 系统级开机自启注册表路径（SYSTEM权限相关）
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        # 打开系统级注册表项（HKEY_LOCAL_MACHINE）
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            key_path,
            0,  # 保留参数，通常为0
            # 系统级注册表需要的权限（读写）
            winreg.KEY_SET_VALUE | winreg.KEY_WRITE
        )
        # 设置开机自启项（REG_SZ字符串类型）
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, file_path)
        print(f"{name}已设置为系统级开机自启（将以SYSTEM关联的系统权限运行）")
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"设置失败：{e}（可能需要管理员权限）")
        return False


def remove_start_user(name: str) -> bool:
    """
    删除开机启动(与上述添加的方式对应)

    :param name:键名称
    """
    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, key_path,
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


def remove_start_system(name: str) -> bool:
    """
    删除开机启动(与上述添加的方式对应)

    :param name:键名称
    """
    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    # 打开系统级注册表项（HKEY_LOCAL_MACHINE）
    key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        key_path,
        0,  # 保留参数，通常为0
        # 系统级注册表需要的权限（读写）
        winreg.KEY_SET_VALUE | winreg.KEY_WRITE
    )
    try:
        winreg.DeleteValue(key, name)
    except FileNotFoundError:
        print(f"{name} 没有找到.")
        return False
    else:
        print(f"{name} 已移除开机自启.")
    winreg.CloseKey(key)
    return True


def check_is_start(name: str, power: str = 'user') -> bool:
    """
    获取程序是否开机自启动
    (仅适用于使用add_start_user/add_start_system函数添加的开机自启)

    :param name:键名称
    :param power:检查user注册表内还是system表
    """
    import winreg
    main_file = get.run_file()
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    if power == 'user':
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, key_path,
            winreg.KEY_SET_VALUE,
            winreg.KEY_ALL_ACCESS | winreg.KEY_WRITE | winreg.KEY_CREATE_SUB_KEY)  # By IvanHanloth
    elif power == 'system':
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, key_path,
            winreg.KEY_SET_VALUE,
            winreg.KEY_ALL_ACCESS | winreg.KEY_WRITE | winreg.KEY_CREATE_SUB_KEY)  # By IvanHanloth
    else:
        raise ValueError(f'参数power只能取 user/system\n而输入的是{power}')
    try:
        # 尝试打开键
        value, _ = winreg.QueryValueEx(key, name)
        if value == main_file:
            return True
        else:
            return False
    except FileNotFoundError:
        # 如果抛出FileNotFoundError，说明键不存在
        return False


def check_is_run(title: str, count: int = 1, accurate: bool = True) -> bool:
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


def check_is_admin() -> bool:
    """
    获取程序是否以管理员身份运行
    :是 返回True , 否 返回 Flase
    """
    import ctypes
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def cmd_admin_run(command: str):
    """调用管理员权限执行cmd命令"""
    import ctypes
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, command, None, 1)


def kill_program(pid_program=None, title=None) -> bool:
    """
    关闭程序

    :param pid_program:程序PID
    :param title:程序全程
    :return :bool
    两个参数不能同时输入
    """
    if pid_program is None and title is None:
        raise ValueError('参数不可同时输入')
    import psutil, subprocess
    if pid_program:
        try:
            command = f'taskkill /PID {pid_program} /F /T'
            subprocess.run(command,
                           shell=True,
                           check=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE
                           )
            return True
        except subprocess.CalledProcessError as e:
            print(f"终止进程失败: {e.stderr.decode('gbk')}")  # Windows 通常用 gbk 编码
            return False
    if title:
        try:
            pids = psutil.process_iter()
            for pid in pids:
                # os.getpid()#获取主进程ID
                if title != None and pid.name() == title:
                    # pid.terminate() # 以正常方式终止程序
                    command = f'taskkill /PID {pid.pid} /F /T'
                    subprocess.run(command,
                                   shell=True,
                                   check=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE
                                   )
        except subprocess.CalledProcessError as e:
            print(f"终止进程失败: {e.stderr.decode('gbk')}")  # Windows 通常用 gbk 编码
            return False


def sync_time() -> bool:
    """
    用于将系统时间与NTP网络时间同步
    需要有管理员权限才能设置成功
    """
    import subprocess, time
    ntp_timestamp = get.NTP_time()
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


# 自定义装饰器返回函数的执行耗时
def timer_decorator(func):
    from functools import wraps
    import time
    # 使用 @wraps 保留被装饰函数的元信息（如函数名、文档字符串）
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 装饰器逻辑：执行前记录时间
        start_time = time.time()
        # 调用被装饰的函数，并获取返回值
        result = func(*args, **kwargs)
        # 装饰器逻辑：执行后计算耗时
        end_time = time.time()
        print(f"函数 {func.__name__} 执行耗时：{end_time - start_time:.4f} 秒")
        return result  # 必须返回被装饰函数的结果

    return wrapper  # 返回包装后的函数
