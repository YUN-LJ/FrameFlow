# 导入基本库
from Fun.Norm import get, ThreadSafe, file, ini, general
import requests, time, os, sys, random, pandas as pd
from io import BytesIO
# 导入线程
from queue import Empty, Queue
from concurrent.futures import ThreadPoolExecutor, Future  # 线程池
from threading import Thread, Timer, Lock  # 线程

PACK_NAME = 'wallhaven'
# 路径配置
RUN_PATH = get.run_dir()  # 获取当前程序运行路径
CONFIG_DIR = os.path.join(RUN_PATH, 'config')
SAVE_DIR = CONFIG_DIR  # 默认保存路径
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.ini')
KEY_WORD_PATH = os.path.join(CONFIG_DIR, 'key_word.feather')
IMAGE_INFO_PATH = os.path.join(CONFIG_DIR, 'image_info.feather')
NUM_WORK = 4
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
API_KEY = ""
SEARCH_URL = "https://wallhaven.cc/api/v1/search"  # 搜索API链接
IMAGE_INFO_URL = "https://wallhaven.cc/api/v1/w"  # 图片详细页API链接
REQUEST_FREQ = 60 / 45  # API请求频率每分钟45次
# 参数,更多内容请查看https://wallhaven.cc/help/api
SEARCH_PARAMS = {
    "q": "",  # 关键词
    "categories": "111",  # 类别码:100/101/111/等,三位数字每位上的意思(常规/动漫/人物)
    "purity": "111",  # 分级码:100/110/111/等,三位数字每位上的意思(正常级/粗略级/限制级) 0表示关闭,1表示开启
    "sorting": "date_added",  # 根据什么排序,默认根据添加时间排序,views预览量,favorites收藏量,relevance关系
    "order": "desc",  # 升序/降序:asc升序,desc降序
    "page": 1,  # 页码:1-∞,超过最大页时没结果
}
HEADERS = {"X-API-Key": API_KEY}  # 头文件
CATEGORY_DICT = {'general': '常规', 'anime': '动漫', 'people': '人物'}
PURITY_DICT = {'sfw': '正常级', 'sketchy': '粗略级', 'nsfw': '限制级'}
FILE_TYPE = {"image/jpeg": '.jpg', "image/png": '.png'}
KEY_WORD_COLUMNS = ['关键词', '总页数', '总数', '最新日期', '上次更新']
SEARCH_COLUMNS = ['id', '关键词', '类别', '分级', '文件大小', '文件扩展名',
                  '长', '宽', '比例', '预览量', '收藏量', '远程路径',
                  '略缩图_原', '略缩图_大', '略缩图_小', '日期',
                  '当前页码', '总页数', '总数', '类别码', '分级码']
IMAGE_COLUMNS = ['id', '关键词', '类别', '分级', '文件大小', '文件扩展名',
                 '长', '宽', '比例', '预览量', '收藏量', '本地路径',
                 '远程路径', '略缩图_原', '略缩图_大', '略缩图_小',
                 '日期', '标签']
KEY_WORD_DTYPE = {'关键词': 'str', '总页数': 'UInt32', '总数': 'UInt32',
                  '最新日期': 'datetime64[ns]', '上次更新': 'datetime64[ns]'}
SEARCH_DTYPE = {'id': 'str', '关键词': 'str', '类别': 'str', '分级': 'str',
                '文件大小': 'UInt32', '文件扩展名': 'str', '长': 'UInt32', '宽': 'UInt32',
                '比例': 'float32', '预览量': 'UInt32', '收藏量': 'UInt32', '远程路径': 'str',
                '略缩图_原': 'str', '略缩图_大': 'str', '略缩图_小': 'str',
                '日期': 'datetime64[ns]', '当前页码': 'UInt32', '总页数': 'UInt32',
                '总数': 'UInt32', '类别码': 'UInt8', '分级码': 'UInt8'}
IMAGE_DTYPE = {'id': 'str', '关键词': 'str', '类别': 'str', '分级': 'str', '文件大小': 'UInt32', '文件扩展名': 'str',
               '长': 'UInt32', '宽': 'UInt32', '比例': 'float32', '预览量': 'UInt32', '收藏量': 'UInt32',
               '本地路径': 'str', '远程路径': 'str', '略缩图_原': 'str', '略缩图_大': 'str', '略缩图_小': 'str',
               '日期': 'datetime64[ns]', '标签': 'str'}


# 函数配置
def request_api(url, params=None, timeout=(3, 10), retry=3, header=None) -> bool | requests.Response:
    """
    请求API结果
    :param url:请求链接
    :param params:参数
    :param timeout:设置超时(连接超时,读取超时)
    :param retry:连接超时进行的重试次数
    :param header:请求头
    """
    header = HEADERS if header is None and API_KEY else header
    for _ in range(retry):
        while True:
            try:
                response = requests.get(url,
                                        stream=True,  # 允许流式获取
                                        params=params,  # 请求参数
                                        headers=header,  # 头文件
                                        timeout=timeout,  # 超时
                                        # verify=False,  # 忽略SSL证书验证
                                        )
                status_code = response.status_code
                if status_code == 200:
                    return response
                elif status_code == 429:
                    time.sleep(5)
                elif status_code == 401:
                    print('未经授权的请求,请开启api_key请求')
                    return False
                else:
                    return False
            except Exception as e:
                print(f'\n连接超时{url},正在重试...')
                time.sleep(0.2)
                break


def default_config():
    """默认配置文件"""
    default = {
        'save_path': CONFIG_DIR,
        'categories': '111',
        'purity': '110',
        'num_work': 4,
        'api_key': ''
    }
    config = ini.INI(CONFIG_PATH, 'wallhaven')
    config.append_values(default)


def save_config(save_path, category, purity, num_work, api_key):
    """保存配置文件"""
    config_dict = {
        'save_path': save_path,
        'categories': category,
        'purity': purity,
        'num_work': num_work,
        'api_key': api_key
    }
    config = ini.INI(CONFIG_PATH, 'wallhaven')
    config.append_values(config_dict)


def load_config():
    """加载配置文件"""
    global SAVE_DIR, SEARCH_PARAMS, NUM_WORK, API_KEY, HEADERS
    config = ini.INI(CONFIG_PATH, 'wallhaven')
    values = config.get_values()
    SAVE_DIR = values['save_path']
    SEARCH_PARAMS['categories'] = values['categories']
    SEARCH_PARAMS['purity'] = values['purity']
    NUM_WORK = int(values['num_work'])
    API_KEY = values['api_key']
    HEADERS = {"X-API-Key": API_KEY}  # 头文件
