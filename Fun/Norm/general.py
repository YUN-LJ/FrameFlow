"""
通用函数
"""
import sys, time
import subprocess
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
        if value.find(main_file) != -1:
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
    import psutil, os
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


def create_hidden_cmd_old() -> tuple[int, int]:
    """创建隐藏的 cmd 进程（返回：进程句柄, PID）不能发送信息"""
    import win32process, win32gui
    import win32console, win32con, win32api
    # 1. 配置 STARTUPINFO：强制隐藏窗口
    startup_info = win32process.STARTUPINFO()
    startup_info.dwFlags = win32process.STARTF_USESHOWWINDOW  # 启用窗口显示控制
    startup_info.wShowWindow = win32con.SW_HIDE  # 关键：隐藏窗口（0=隐藏）

    # 2. cmd 命令：UTF-8 编码 + 后台运行（/k 保持进程不退出）
    cmd_line = 'cmd.exe /k "chcp 65001 >nul && echo 🟢 隐藏 cmd 已启动（UTF-8）"'

    # 3. 进程创建标志：新进程组 + 新控制台（保留资源）+ 挂起（确保窗口先隐藏再启动）
    creation_flags = (win32process.CREATE_NEW_PROCESS_GROUP
                      | win32process.CREATE_NEW_CONSOLE
                      | win32process.CREATE_SUSPENDED)

    # 4. 调用 Windows 原生 API 创建进程
    try:
        (process_handle, thread_handle, process_id, thread_id) = win32process.CreateProcess(
            None,  # 不指定可执行文件路径（cmd.exe 系统自带，PATH 可找到）
            cmd_line,  # 命令行参数
            None,  # 进程安全属性（默认）
            None,  # 线程安全属性（默认）
            0,  # 不继承句柄
            creation_flags,  # 进程创建标志
            None,  # 环境变量（默认）
            None,  # 工作目录（默认）
            startup_info  # 启动信息（控制窗口隐藏）
        )
        # 恢复挂起的进程（此时窗口已隐藏，不会闪显）
        win32process.ResumeThread(thread_handle)
        # 关闭线程句柄（无需保留）
        win32api.CloseHandle(thread_handle)
        # print(f"隐藏 cmd 进程创建成功：PID={process_id}")
        return process_handle, process_id
    except Exception as e:
        return False
        # print(f"创建隐藏 cmd 失败：{e}")
        # sys.exit(1)


def kill_hidden_cmd(process_handle):
    """
    关闭隐藏的 cmd 进程
    :param process_handle:进程句柄
    """
    import win32api
    win32api.TerminateProcess(process_handle, 0)
    win32api.CloseHandle(process_handle)


def create_hidden_cmd(hide=True) -> subprocess.Popen | tuple[subprocess.Popen, int]:
    """创建隐藏的cmd进程,返回subprocess.Popen,和窗口句柄"""
    import win32gui, win32con
    # 关键标志：仅保留这两个（确保生成窗口句柄）
    if hide:
        creationflags = (subprocess.CREATE_NEW_PROCESS_GROUP  # 方便后续终止进程
                         | subprocess.CREATE_NO_WINDOW)  # 创建无窗口的cmd
    else:
        creationflags = (subprocess.CREATE_NEW_PROCESS_GROUP  # 方便后续终止进程
                         | subprocess.CREATE_NEW_CONSOLE)  # 强制创建窗口（获取句柄的前提）
    # 1. 创建 cmd 进程（保留窗口句柄：仅用 CREATE_NEW_CONSOLE + CREATE_NEW_PROCESS_GROUP）
    process = subprocess.Popen(
        ["cmd.exe", "/k", "chcp 65001 >nul"],
        creationflags=creationflags,
        shell=False,
        stdin=subprocess.PIPE,
        # stdout=subprocess.PIPE,  # 可选：重定向标准输出（如需捕获输出）
        # stderr=subprocess.PIPE,  # 可选：重定向标准错误（如需捕获错误）
        text=False,  # 保持字节流模式（write 需传 bytes，避免编码问题）
        bufsize=0,  # 禁用缓冲（立即发送命令，避免卡顿）
    )
    if hide:
        return process
    else:
        target_pid = process.pid
        hwnd = find_hwnd(target_pid)
        for i in range(10):
            hwnd = find_hwnd(target_pid)
            if not hwnd:
                time.sleep(0.1)
            else:
                break
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        return process, hwnd


def find_hwnd(target_inf: str | int, class_name: list[str] = None, accurate: bool = True) -> int:
    """
    查找窗口句柄

    :param target_inf:查找的窗口标题str或进程pid
    :param widget:需要嵌入的窗口对象QWidget
    :param class_name:窗口所属的类,[cmd:'ConsoleWindowClass',终端:'CASCADIA_HOSTING_WINDOW_CLASS']
    :param accurate:是否开启精确查找bool
    :return :窗口句柄hwnd
    """
    import win32gui, win32process, os

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


def hide_python_console():
    """隐藏python控制台"""
    import ctypes, win32con
    # 获取python控制台句柄
    python_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if python_hwnd != 0:
        ctypes.windll.user32.ShowWindow(python_hwnd, win32con.SW_HIDE)


def show_python_console():
    """显示python控制台"""
    import ctypes, win32con
    # 获取python控制台句柄
    python_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if python_hwnd != 0:
        ctypes.windll.user32.ShowWindow(python_hwnd, win32con.SW_SHOW)

    # import win32console
    # win32console.FreeConsole()  # 释放 cmd 控制台
    # win32console.AllocConsole()  # 重新创建 Python 控制台
    # sys.stdout = sys.__stdout__  # 恢复原 stdout


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
    if not check_is_admin():
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
