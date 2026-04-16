"""配置文件"""
LIGHT = 'rgb(245,245,245)'
DARK = 'rgb(45,45,45)'
CURRENT_THEME = None  # 当前主题值,'Dark' 或 'Light'
TOP_WINDOWS = None  # 顶层窗口
APP = None  # 应用控制实例
TRAY = None  # 托盘图标
CAPTURE_PYTHON_TERMINAL = None  # 全局捕获实例,仅打包后捕获,编程环境下不捕获
# 启动参数
IS_CAPTURE = True  # 是否捕获python终端输出
IS_SHOW = True  # 是否显示窗口
IS_HIED_TERMINAL = True  # 是否隐藏终端
IS_DEBUG = False  # 是否启用调式模式
