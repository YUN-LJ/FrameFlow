"""配置文件"""
from typing import Optional
from Fun.QtWidget import TrayIcon

LIGHT = 'rgb(245,245,245)'
DARK = 'rgb(45,45,45)'
CURRENT_THEME: Optional[str] = None  # 当前主题值,'Dark' 或 'Light'
TRAY: Optional[TrayIcon] = None  # 托盘图标
# 启动参数
IS_CAPTURE = True  # 是否捕获python终端输出
IS_SHOW = True  # 是否显示窗口
IS_HIED_TERMINAL = True  # 是否隐藏终端
IS_DEBUG = False  # 是否启用调式模式
