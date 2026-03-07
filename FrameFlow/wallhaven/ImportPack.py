"""导入依赖库"""
import os
import time
import requests
import pandas as pd
from io import BytesIO
from typing import Callable
from wallhaven import Config
from threading import Lock, Thread
from Fun.Norm import get, file, general, ThreadSafe
from GlobalModule.TaskManage import Task, TaskManage
from GlobalModule import (data_manage, config_data,
                          GlobalValue, image_info,
                          key_word, search_data,
                          image_info_task, key_word_task)
