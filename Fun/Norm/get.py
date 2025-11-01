"""
获取基本数据
"""
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


def now_time(format="%Y-%m-%d-%H-%M-%S"):
    """
    获取当前时间

    :param format:获取时间的格式
    :返回值:格式化时间
    """
    import time
    format_time = time.strftime(format, time.localtime())
    return format_time


def NTP_time(local_time=True) -> float:
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
