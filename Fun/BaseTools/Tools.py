"""工具类函数"""
import psutil
import subprocess
from Fun.BaseTools import Get


def chunk_list(lst, chunk_size):
    """将列表分割成指定大小的子列表"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


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
    main_file = Get.run_file()
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
