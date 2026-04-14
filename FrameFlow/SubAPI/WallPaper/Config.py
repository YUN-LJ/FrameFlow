"""壁纸播放全局变量"""
PACK_NAME = 'WallPaper'
# 播放模式
IMAGE_CUSTOM_MODE = 0  # 自定义模式,从用户选择的本地文件夹中读取照片
IMAGE_KEY_MODE = 1  # 关键词模式,按照wallhaven模块中的收藏的关键词获取图像数据
IMAGE_VIDEO_MODE = 2  # 视频模式,仅在IMAGE_WINDOWS_QT模式下支持
# 播放接口
IMAGE_WINDOWS_API = 0  # windows系统API播放壁纸
IMAGE_WINDOWS_QT = 1  # windows系统使用qt创建桌面窗口播放壁纸
IMAGE_LINUX_API = 2  # liunx系统API播放壁纸
IMAGE_PLAY_SORT_DATE = 0  # 日期播放
IMAGE_PLAY_SORT_SAMPLE = 1  # 随机播放

# 壁纸播放时的全局变量
IMAGE_DIR = []  # 用户选择的图片文件夹
IMAGE_CHOICE_KEY = []  # 用户选择的关键词
IMAGE_CHOICE_TAG = []  # 用户选择的标签
IMAGE_CHOICE_CATEGORIES = []  # 用户选择的类别筛选(使用中文:常规/动漫/人物)
IMAGE_CHOICE_PURITY = []  # 用户选择的分级筛选(使用中文:正常级/粗略级/限制级)
IMAGE_PLAY_MODE = IMAGE_KEY_MODE
IMAGE_TIME = 10.0  # 播放间隔,默认10秒
IMAGE_TEMP_NUM = 3  # 图片缓冲数量,默认3张
IMAGE_PLAY_SORT = 0  # 默认日期播放
