"""壁纸播放模块"""
from wallpaper.Config import *

# 加载配置文件
if not file.check_exist(CONFIG_PATH) or PACK_NAME not in ini.INI(CONFIG_PATH).get_sections():
    default_config()  # 生成默认配置文件

load_config()  # 加载配置文件
print(f'{__name__}配置文件加载成功')
# 重新导入,确保wallpaper里的镜像变量被修改,外部可直接使用wallpaper.变量名来获取变量值
from wallpaper.Config import *
from wallpaper import WallPaperPlay, Tools

# 声明对外接口
__all__ = ['WallPaperPlay', 'Tools']  # 明确导出的成员
