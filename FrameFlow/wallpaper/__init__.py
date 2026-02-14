"""壁纸播放模块"""
from wallpaper.Config import *

# 加载配置文件
if not file.check_exist(CONFIG_PATH):
    default_config()  # 生成默认配置文件
load_config()  # 加载配置文件
print(f'{__name__}配置文件加载成功')

from wallpaper import WallPaperPlay, Tools

# 声明对外接口
__all__ = ['WallPaperPlay', 'Tools']  # 明确导出的成员
