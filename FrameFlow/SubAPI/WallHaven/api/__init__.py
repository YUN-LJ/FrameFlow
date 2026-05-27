"""后端api包"""
from enum import Enum
from SubAPI.WallHaven.api.Tools import *
from SubAPI.WallHaven.api import WorkFlow


# 使用枚举值运行任务
def run_task(task_event: GlobalValue.WallHavenTaskClassEnum, *args, **kwargs) -> Any:
    """
    运行任务
    :param task_event:任务类型枚举值
    :param args:任务所需参数
    :param kwargs:任务所需参数
    """
