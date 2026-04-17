"""全局常量"""
import os
from Fun.BaseTools import Get

# 程序路径配置
run_dir = Get.run_dir()
config_dir = os.path.join(run_dir, 'config')
# 数据文件路径配置
log_path = os.path.join(config_dir, 'log.txt')
image_cache_dir = os.path.join(config_dir, 'image_cache')
image_info_path = os.path.join(config_dir, 'image_info.feather')
key_word_path = os.path.join(config_dir, 'key_word.feather')
image_history_path = os.path.join(config_dir, 'image_history.feather')
config_path = os.path.join(config_dir, 'config.ini')
# pandas表格字段
search_columns = ['id', '关键词', '类别', '分级', '文件大小', '文件扩展名',
                  '长', '宽', '比例', '预览量', '收藏量', '远程路径',
                  '略缩图_原', '略缩图_大', '略缩图_小', '日期',
                  '当前页码', '总页数', '总数', '类别码', '分级码']
search_dtype = {'id': 'str', '关键词': 'str', '类别': 'str', '分级': 'str',
                '文件大小': 'UInt32', '文件扩展名': 'str', '长': 'UInt32', '宽': 'UInt32',
                '比例': 'float32', '预览量': 'UInt32', '收藏量': 'UInt32', '远程路径': 'str',
                '略缩图_原': 'str', '略缩图_大': 'str', '略缩图_小': 'str',
                '日期': 'datetime64[ns]', '当前页码': 'UInt32', '总页数': 'UInt32',
                '总数': 'UInt32', '类别码': 'str', '分级码': 'str'}
image_info_columns = ['id', '关键词', '类别', '分级', '文件大小', '文件扩展名',
                      '长', '宽', '比例', '预览量', '收藏量', '本地路径',
                      '远程路径', '略缩图_原', '略缩图_大', '略缩图_小',
                      '日期', '标签']
image_info_dtype = {'id': 'str', '关键词': 'str', '类别': 'str', '分级': 'str', '文件大小': 'UInt32',
                    '文件扩展名': 'str',
                    '长': 'UInt32', '宽': 'UInt32', '比例': 'float32', '预览量': 'UInt32', '收藏量': 'UInt32',
                    '本地路径': 'str', '远程路径': 'str', '略缩图_原': 'str', '略缩图_大': 'str', '略缩图_小': 'str',
                    '日期': 'datetime64[ns]', '标签': 'str'}
key_word_columns = ['关键词', '总页数', '总数', '最新日期', '上次更新', '类别码', '分级码']
key_word_dtype = {'关键词': 'str', '总页数': 'UInt32', '总数': 'UInt32',
                  '最新日期': 'datetime64[ns]', '上次更新': 'datetime64[ns]',
                  '类别码': 'str', '分级码': 'str'}
image_history_columns = image_info_columns
image_history_dtype = image_info_dtype


class ImageInfoColumns:

    def __init__(self):
        self.id = 'id'
        self.key_word = '关键词'
        self.categories = '类别'
        self.purity = '分级'
        self.size = '文件大小'
        self.type = '文件扩展名'
        self.long = '长'
        self.wide = '宽'
        self.ratio = '比例'
        self.view = '预览量'
        self.collect = '收藏量'
        self.local_path = '本地路径'
        self.remote_path = '远程路径'
        self.thumb_original = '略缩图_原'
        self.thumb_big = '略缩图_大'
        self.thumb_min = '略缩图_小'
        self.date = '日期'
        self.tags = '标签'

    def to_list(self) -> list:
        return [value for value in self.__dict__.values()]


class KeyWordColumns:

    def __init__(self):
        self.key_word = '关键词'
        self.total_page = '总页数'
        self.total = '总数'
        self.date_latest = '最新日期'
        self.date_updata = '上次更新'
        self.categories_code = '类别码'
        self.purity_code = '分级码'

    def to_list(self) -> list:
        return [value for value in self.__dict__.values()]
