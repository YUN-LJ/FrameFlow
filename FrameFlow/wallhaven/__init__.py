"""wallhavenAPI集成"""
from GlobalModule import config_data
from wallhaven import WallHavenAPI, Config

# 加载配置文件
if config_data.data:
    with config_data.lock:
        value = config_data.data.get_values(section_name=Config.PACK_NAME)
        if value:
            Config.THREAD_NUM = value['num_work']
            Config.SAVE_DIR = value['save_dir']
            Config.SEARCH_PARAMS['categories'] = value['categories']
            Config.SEARCH_PARAMS['purity'] = value['purity']
            Config.SEARCH_PARAMS['sorting'] = value['sorting']
            Config.SEARCH_PARAMS['order'] = value['order']
            Config.API_KEY = value['api_key']
            Config.HEADERS = {"X-API-Key": Config.API_KEY}
# 声明对外接口
__all__ = ['WallHavenAPI']  # 明确导出的成员
