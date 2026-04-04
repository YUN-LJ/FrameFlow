"""全局常量"""
import os
from Fun.Norm import get

# 程序路径配置
run_dir = get.run_dir()
config_dir = os.path.join(run_dir, 'config')
# 数据文件路径配置
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
image_history_columns = ['id']  # 如果是图像ID则去图像信息文件中查找图像的地址,如果是图像地址则直接排除
image_history_dtype = {'id': 'str'}
