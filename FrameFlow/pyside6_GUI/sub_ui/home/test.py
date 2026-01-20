import time

import pandas as pd

# KEY_WORD_COLUMNS = ['关键词', '总页数', '总数', '最新日期']
# df = pd.DataFrame(columns=KEY_WORD_COLUMNS)
# old_df = pd.read_excel('./config/key_word.xlsx')
# key_word = old_df['关键词'].drop_duplicates(keep='last', ignore_index=True)
# key_word = key_word.sort_values(key=lambda col: col.str.lower(),ignore_index=True)
# df['关键词'] = key_word
# df.to_excel('./config/key_word.xlsx',index=False)
IMAGE_DTYPE = {'id': 'str', '关键词': 'str', '类别': 'str', '分级': 'str', '文件大小': 'UInt32', '文件扩展名': 'str',
               '长': 'UInt16', '宽': 'UInt16', '比例': 'float32', '预览量': 'UInt32', '收藏量': 'UInt32',
               '本地路径': 'str', '远程路径': 'str', '略缩图_原': 'str', '略缩图_大': 'str', '略缩图_小': 'str',
               '日期': 'datetime64[ns]', '标签': 'str'}
KEY_WORD_DTYPE = {'关键词': 'str', '总页数': 'UInt16', '总数': 'UInt16',
                  '最新日期': 'datetime64[ns]', '上次更新': 'datetime64[ns]'}
# old_df = pd.read_excel('./config/image_info.xlsx').astype(IMAGE_DTYPE)
# # 只对字符串类型的列进行空值替换
# # for col in old_df.columns:
# #     if old_df[col].dtype == 'object':  # 字符串类型列
# #         old_df[col] = old_df[col].replace({'nan': ''})
# old_df.to_feather('./config/image_info.feather')
# old_df = pd.read_excel('./config/key_word.xlsx').astype(KEY_WORD_DTYPE)
# old_df.to_feather('./config/key_word.feather')

# old_df = pd.read_feather('./config/key_word.feather').astype(KEY_WORD_DTYPE)
# old_df.to_excel('./config/key_word.xlsx', index=False)

old_df = pd.read_feather('./config/image_info.feather').astype(IMAGE_DTYPE)
old_df.to_excel('./config/image_info.xlsx', index=False)
