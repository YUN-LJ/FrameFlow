"""
wallhavenAPI集成
面向对象编程方式
"""
from SubAPI.WallHaven import api
import multiprocessing

# 检测是否为主进程
_is_main_process = multiprocessing.current_process().name == 'MainProcess'
if _is_main_process:
    # 加载配置文件
    api.load_config()
