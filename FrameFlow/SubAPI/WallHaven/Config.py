"""后端常量"""
# API配置
# API_KEY_LIST = [
#     "mxYAr8xPS6J4gyVOtfu0YQHwftSO4p6x",
#     "tDm50CzRxRoxhd51msb1gnO48do6zAsM",
#     "v0wcHRypBXK5EjriNvlfB6kF0huAS94h",
#     "YjFjjwPh1uM4cuyTn6dt32mf6emJeBJf",
#     "qMczJD5d20sWn5QIG6iNozekstld4rYs",
#     "vPdJ4AYQJJsfECQjPipUEN5l0QzzYVyb",
#     "fEJqYw27z1fV1M1ChhzbwuiglM5ttJXy",
#     "RIynJj6HLkOn3xy0ZOWcaAwZiMk53R4A",
# ]  # 用户密钥,无密钥时无法查看限制级
USE_NETWORK = False
THUMB_SIZE = (300, 200)
PACK_NAME = 'WallHaven'
WALLHAVEN_URL = 'https://wallhaven.cc'
API_KEY = ""
PROXIES_URL = ''
SEARCH_URL = "https://wallhaven.cc/api/v1/search"  # 搜索API链接
IMAGE_INFO_URL = "https://wallhaven.cc/api/v1/w"  # 图片详细页API链接
CONNECT_TEST_URL = "https://wallhaven.cc/api/v1/w/g71erd"  # 用于测试是否可访问网站
API_KEY_TEST_URL = "https://wallhaven.cc/api/v1/w/pk6yv9"  # 用于测试api_key是否可用
# 参数,更多内容请查看https://wallhaven.cc/help/api
REQUEST_MAX_COUNT = 45  # 每分钟最多请求45次
THREAD_NUM = 4  # 默认线程数量,可根据配置文件动态修改
HEADERS = {"X-API-Key": API_KEY}  # 头文件
PROXIES = {'http': f'http://{PROXIES_URL}', 'https': f'http://{PROXIES_URL}'}  # 网络代理
# 字典映射
CATEGORY_DICT = {'general': '常规', 'anime': '动漫', 'people': '人物'}
PURITY_DICT = {'sfw': '正常级', 'sketchy': '粗略级', 'nsfw': '限制级'}
TYPE_DICT = {"image/jpeg": '.jpg', "image/png": '.png'}
COLOR_DICT = {'正常级': 'green', '粗略级': 'yellow', '限制级': 'red'}
# 路径信息
SAVE_DIR = ''  # 保存路径
SEARCH_HISTORY = []  # 搜索历史
SEARCH_HISTORY_COUNT = 10  # 限制搜索历史存储上限
LOCAL_SEARCH_MODE_KEY = '关键词'
LOCAL_SEARCH_MODE_TAGS = '标签'
USE_TAGS = False  # 本地搜索模式


class SearchParams:
    default_params = {
        "q": "",  # 关键词
        "categories": "111",  # 类别码:100/101/111/等,三位数字每位上的意思(常规/动漫/人物)
        "purity": "110",  # 分级码:100/110/111/等,三位数字每位上的意思(正常级/粗略级/限制级) 0表示关闭,1表示开启
        "sorting": "date_added",  # 根据什么排序,默认根据添加时间排序,views预览量,favorites收藏量,relevance关系
        "order": "desc",  # 升序/降序:asc升序,desc降序
        "page": 1,  # 页码:1-∞,超过最大页时没结果
    }

    def __init__(self, default: dict = None):
        self.q = self.__class__.default_params['q']
        self.categories = self.__class__.default_params['categories']
        self.purity = self.__class__.default_params['purity']
        self.sorting = self.__class__.default_params['sorting']
        self.order = self.__class__.default_params['order']
        self.page = self.__class__.default_params['page']

        # 允许通过关键字参数初始化
        if default is not None:
            self.set_dict(default)

    def set_dict(self, param_dict: dict):
        for key, value in param_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self):
        """将对象转换回字典"""
        return {
            "q": self.q,
            "categories": self.categories,
            "purity": self.purity,
            "sorting": self.sorting,
            "order": self.order,
            "page": self.page
        }

    def copy(self):
        return SearchParams(self.to_dict())

    def __repr__(self):
        return str(self.to_dict())

    def __str__(self):
        return str(self.to_dict())
