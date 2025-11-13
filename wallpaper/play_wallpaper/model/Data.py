"""M层数据获取和保存"""
import os, pandas as pd, numpy as np
from Fun.Norm import file, general

from . import GlobalValues

RUN_PATH = GlobalValues.run_path  # 程序运行路径
COLUMNS = ['所在目录', '子文件路径', '是否播放', '扫描时间', 'image_path']  # 列索引
IMAGE_EXTENSION = {'png', 'jpg', 'jpeg'}  # 照片格式
ALL_DIRS = GlobalValues.user_dir_path  # 照片文件夹路径
ALL_FILES = pd.DataFrame(columns=COLUMNS)  # 所有照片的信息
TEMP_DIR = os.path.join(RUN_PATH, 'temp')  # 缓存路径,默认在程序启动目录下
file.ensure_exist(TEMP_DIR)

# 保存文件和加载文件的名称,
# 目前只支持xlsx、csv、pkl格式，
# csv加载快占用空间大,xlsx占用空间小加载慢
# pkl由于采用了gzip压缩所以后缀为pkl.gz,加载速度最快的格式(大约13ms)
DATA_NAME = 'image_data.pkl.gz'


@general.timer_decorator
def load_data(data_path: str = None) -> bool:
    """
    加载本地数据

    :param data_path:数据路径
    """
    if data_path is None:
        data_path = os.path.join(TEMP_DIR, DATA_NAME)
    if not file.check_exist(data_path):
        return False
    global ALL_DIRS, ALL_FILES
    if not file.check_exist(data_path):
        raise FileNotFoundError(f'文件{data_path}不存在')
    try:
        if file.get_file_extension(data_path) == 'csv':
            ALL_FILES = pd.read_csv(data_path)
        elif file.get_file_extension(data_path) == 'xlsx':
            ALL_FILES = pd.read_excel(data_path)
        elif file.get_file_extension(data_path) == 'gz':
            ALL_FILES = pd.read_pickle(data_path, compression='gzip')
        check_valid()  # 检查数据
        ALL_DIRS = set(ALL_FILES.groupby('所在目录').groups.keys())
        GlobalValues.user_dir_path = ALL_DIRS
        return True
    except:
        return False


def check_valid():
    """检查ALL_FILES表中是否有无效数据,如果有则会删除无效数据"""
    global ALL_FILES

    # 1. 向量化拼接路径（替代逐行拼接）
    # ALL_FILES['image_path'] = ALL_FILES['所在目录'] + ALL_FILES['子文件路径']

    # 2. 批量判断目录是否在ALL_DIRS中（向量化操作）
    dir_valid = ALL_FILES['所在目录'].isin(ALL_DIRS)
    # 3. 获取ALL_DIRS下的全部文件(检查全部文件是否存在于all_files)
    all_files = []
    for path in ALL_DIRS:
        all_files.extend(file.get_files_path(path, only_file=True, ext=IMAGE_EXTENSION))
    path_valid = ALL_FILES['image_path'].isin(all_files)

    # 3. 批量检查文件是否存在（关键优化：减少IO调用次数）
    # 方法1：如果file.check_exist支持批量路径（推荐，需file模块支持）
    # path_valid = np.array(file.check_exist(ALL_FILES['image_path'].tolist()))

    # 方法2：如果file.check_exist仅支持单个路径，用np.vectorize加速（比apply快）
    # path_valid = np.vectorize(file.check_exist)(ALL_FILES['image_path'])

    # 4. 合并条件，过滤有效数据
    ALL_FILES = ALL_FILES[dir_valid & path_valid]


def check_valid_old():
    """检查ALL_FILES表中是否有无效数据,如果有则会删除无效数据"""
    global ALL_FILES

    def check(row):
        dir_path = row['所在目录']
        image_name = row['子文件路径']
        # state = row['是否播放']
        image_path = dir_path + image_name
        if dir_path in ALL_DIRS and file.check_exist(image_path):
            # 目录被选择且文件存在,保留
            return True
        else:
            return False

    ALL_FILES = ALL_FILES[ALL_FILES.apply(check, axis=1)]


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
        if files_path != []:
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


def get_random_row(whitelist: list = [], blacklist: list = []) -> pd.Series:
    """
    从未播放的数据中随机获取一行数据
    :param whitelist:白名单,获取image_path中包含特定文字
    :param blacklist:黑名单,获取除了image_path中包含特定文字
    """
    try:
        filter_files = ALL_FILES[ALL_FILES['是否播放'] == False]
        # 处理白、黑名单,生成对于掩码
        white_mask = filter_files['image_path'].str.contains('|'.join(whitelist))
        black_mask = filter_files['image_path'].str.contains('|'.join(blacklist))
        # 合并条件筛选
        filter_files = filter_files[white_mask & ~black_mask]
        return filter_files.sample(n=1)
    except ValueError as e:
        if reset_state():
            filter_files = ALL_FILES[ALL_FILES['是否播放'] == False]
            # 处理白、黑名单,生成对于掩码
            white_mask = filter_files['image_path'].str.contains('|'.join(whitelist))
            black_mask = filter_files['image_path'].str.contains('|'.join(blacklist))
            # 合并条件筛选
            filter_files = filter_files[white_mask & ~black_mask]
            return filter_files.sample(n=1)


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
    data = [[dir_path, general.del_part_str(file, dir_path), False, now_time, file] for file in files_path]
    # 创建一个要添加的DataFrame
    new_data = pd.DataFrame(data, columns=COLUMNS)
    # 表合并
    ALL_FILES = pd.concat([ALL_FILES, new_data], ignore_index=True)  # 重置索引
    # 数据去重
    ALL_FILES.drop_duplicates(subset=['所在目录', '子文件路径'], keep='first', inplace=True)
    return ALL_FILES


def add_image_dir(dir_path: str) -> bool:
    """新增照片目录"""
    if file.check_exist(dir_path) and file.check_dir(dir_path):
        ALL_DIRS.add(dir_path)
        GlobalValues.user_dir_path.add(dir_path)
        return True
    else:
        return False


def del_image_dir(dir_path: list) -> bool:
    """删除照片路径"""
    try:
        for item in dir_path:
            ALL_DIRS.remove(item)
        check_valid()
        return True
    except:
        check_valid()
        return False


def clear_image_dir() -> bool:
    """清空照片目录"""
    global ALL_FILES
    ALL_DIRS.clear()
    GlobalValues.user_dir_path.clear()
    ALL_FILES = pd.DataFrame(columns=COLUMNS)
    return True


def update_state(row: pd.DataFrame, state=True) -> bool:
    """更新表中照片的播放状态"""
    ALL_FILES.loc[row.index[0], '是否播放'] = state
    return True


def reset_state() -> bool:
    """重置全部图片的状态"""
    global ALL_FILES
    ALL_FILES['是否播放'] = False
    return True


def save_data() -> bool:
    """
    保存当前的ALL_FILES数据,
    修改DATA_NAME的后缀即可修改保存文件的格式
    """
    global DATA_NAME
    try:
        extension = file.get_file_extension(DATA_NAME)
        target_path = os.path.join(TEMP_DIR, DATA_NAME)
        if extension == 'xlsx':
            ALL_FILES.to_excel(target_path, index=False)
        elif extension == 'csv':
            ALL_FILES.to_csv(target_path, index=False, encoding='utf-8')
        elif extension == 'gz':
            # compression：可选参数，默认为
            # 'infer'，表示自动根据文件扩展名检测压缩格式，也可以显式指定为
            # 'gzip'、'bz2'、'xz'等。
            ALL_FILES.to_pickle(target_path, compression='gzip')
        return True
    except Exception as e:
        print(f'save_data 错误: {e}')
        return False
