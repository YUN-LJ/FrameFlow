"""wallhavenAPI集成"""
from wallhaven.Config import *

# 加载配置文件
if not file.check_exist(CONFIG_PATH) or PACK_NAME not in ini.INI(CONFIG_PATH).get_sections():
    default_config()  # 生成默认配置文件
load_config()  # 加载配置文件
print(f'{__name__}配置文件加载成功')

from wallhaven import WallHavenAPI, Tools

# 声明对外接口
__all__ = ['WallHavenAPI', 'Tools']  # 明确导出的成员
