"""M层数据获取和保存"""
import pandas as pd
from Fun.Norm import file, general

from . import GlobalValues

RUN_PATH = GlobalValues.run_path  # 程序运行路径
COLUMNS = ['所在目录', '子文件路径', '是否播放', '扫描时间']  # 列索引
IMAGE_EXTENSION = {'png', 'jpg', 'jpeg'}  # 照片格式
ALL_DIRS = GlobalValues.user_dir_path  # 照片文件夹路径
ALL_FILES = pd.DataFrame(columns=COLUMNS)  # 所有照片的信息


def get_new_data(clear=False) -> pd.DataFrame:
    """
    重新扫描磁盘获取数据

    :param clear:清除ALL_FILES全部内容
    """
    from threading import Thread
    if clear:
        ALL_FILES.drop(ALL_FILES.index, inplace=True)  # 对原数据生效

    # 获取全部文件路径
    def run(dir_path):
        files_path = file.get_files_path(dir_path, only_file=True)
        # 利用filter过滤其中的非照片路径
        image_files_path = filter(
            lambda file_path: file.get_file_extension(file_path) in IMAGE_EXTENSION,
            files_path)
        add_data(dir_path, image_files_path)

    # 存储线程的列表
    threads = []
    # 为每个元素创建线程
    for dir_path in ALL_DIRS:
        # 创建线程，target指定要执行的函数，args传递参数
        thread = Thread(
            target=run,
            args=(dir_path,),  # 注意：元组形式传递参数
            daemon=True  # 守护线程,主线程结束后子线程会被立即终止
        )
        threads.append(thread)
        # 启动线程
        thread.start()
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    return ALL_FILES


def add_data(dir_path: str, files_path: list) -> pd.DataFrame:
    """
    将数据新增到ALL_FILES中

    :param dir_path:所在文件夹,str
    :param files_path:照片路径,可以是str也可以是list
    """
    global ALL_FILES
    # 构造新数据
    import time
    now_time = general.stamp_to_strf(time.time(), format="%Y-%m-%d")
    data = [[dir_path, general.del_part_str(file, dir_path), False, now_time] for file in files_path]
    # 创建一个要添加的DataFrame
    new_data = pd.DataFrame(data, columns=COLUMNS)
    # 表合并
    ALL_FILES = pd.concat([ALL_FILES, new_data], ignore_index=True)  # 重置索引
    return ALL_FILES


def save_data(extension='xlsx') -> bool:
    """
    保存当前的ALL_FILES数据

    :param extension:保存的文件格式 -> xlsx、csv
    """
    import os
    try:
        target_path = os.path.join(RUN_PATH, f'temp/image_data.{extension}')
        if extension == 'xlsx':
            ALL_FILES.to_excel(target_path, index=False)
        elif extension == 'csv':
            ALL_FILES.to_csv(target_path, index=False, encoding='utf-8')
        return True
    except Exception as e:
        print(f'save_data 错误: {e}')
        return False
