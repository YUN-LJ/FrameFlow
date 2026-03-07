import time
from GlobalModule import DataManage, GlobalValue, LogManage, TaskManage

config_data = DataManage.ConfigData()  # 配置文件类
image_info = DataManage.ImageInfo()  # 图像数据
key_word = DataManage.KeyWord()  # 关键词数据
search_data = DataManage.SearchData()  # 搜索数据
data_manage = DataManage.DataManage()  # 数据管理
_config_task = data_manage.add_data_object(config_data)
_search_data_task = data_manage.add_data_object(search_data)
image_info_task = data_manage.add_data_object(image_info)
key_word_task = data_manage.add_data_object(key_word)
for _ in range(100):  # 最多等待1秒钟
    if not _config_task.done():
        time.sleep(0.01)

__all__ = [
    'config_data',
    'data_manage',
    'image_info',
    'key_word',
    'search_data',
    'image_info_task',
    'key_word_task',
    'DataManage',
    'GlobalValue',
    'LogManage',
    'TaskManage'
]
