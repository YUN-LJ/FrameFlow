"""
文件基础操作
"""
import os, sys, shutil
import threading
from queue import Queue
from typing import List

FILE_PATH = None  # 文件路径
DIR_PATH = None  # 文件夹路径

IMAGE_EXTENSION = {'png', 'jpg', 'jpeg'}  # 照片格式


def ensure_exist(dir_path: str = None) -> bool:
    """
    确保目录存在

    :param dir_path:目录路径
    """
    if dir_path is None:
        if DIR_PATH is not None:
            dir_path = DIR_PATH
        else:
            raise ValueError('没有指定目录->请指定DIR_PATH或传入dir_path')
    if not os.path.isdir(dir_path):  # 判断文件夹是否存在,如果不存在isdir返回Flase
        os.makedirs(dir_path)
        return True


def check_exist(path: str) -> bool:
    """检查文件是否存在"""
    return os.path.exists(path)


def check_dir(dir_path: str) -> bool:
    if os.path.isdir(dir_path):
        return True
    else:
        return False


def check_image(file_path: str) -> bool:
    """检查文件是否是图像"""
    if get_file_extension(file_path) in IMAGE_EXTENSION:
        return True
    else:
        return False


def open_file_use_explorer(file_path: str = None) -> bool:
    """
    用资源管理器打开文件并选中文件

    :param file_path:文件路径
    """
    if file_path is None:
        if FILE_PATH is not None:
            file_path = FILE_PATH
        else:
            raise ValueError('没有指定文件->请指定FILE_PATH或传入file_path')
    import subprocess
    # 用于返回指定路径的规范化绝对路径,会将相对路径转为绝对路径
    file_path = os.path.realpath(file_path)
    subprocess.Popen(f'explorer /select, {file_path}')
    return True


def get_file_name(file_path: str = None) -> str:
    """
    获取文件名

    :param file_path:文件绝对路径
    """
    if file_path is None:
        if FILE_PATH is not None:
            file_path = FILE_PATH
        else:
            raise ValueError('没有指定文件->请指定FILE_PATH或传入file_path')
    file_name = os.path.basename(file_path)
    return file_name


def get_file_root(file_path: str = None) -> str:
    """
    获取文件无扩展名的名称

    :param file_path:文件绝对路径
    """
    if file_path is None:
        if FILE_PATH is not None:
            file_path = FILE_PATH
        else:
            raise ValueError('没有指定文件->请指定FILE_PATH或传入file_path')
    file_name = get_file_name(file_path)
    file_name = os.path.splitext(file_name)[0]
    return file_name


def get_file_extension(file_path: str = None) -> str:
    """
    获取文件扩展名
    :param file_path:文件绝对路径
    :return :'exe'
    """
    if file_path is None:
        if FILE_PATH is not None:
            file_path = FILE_PATH
        else:
            raise ValueError('没有指定文件->请指定FILE_PATH或传入file_path')
    extension = os.path.splitext(file_path)[1].replace('.', '')
    return extension


def get_file_on_dir(file_path: str = None) -> str:
    """
    获取文件所在文件夹

    :param file_path:文件绝对路径
    """
    if file_path is None:
        if FILE_PATH is not None:
            file_path = FILE_PATH
        else:
            raise ValueError('没有指定文件->请指定FILE_PATH或传入file_path')
    file_dir = os.path.dirname(file_path)
    return file_dir


def get_files_path_one(dir_path: str = None, only_file=False, only_dir=False, deep=0) -> list:
    """
    获取指定目录下全部的文件路径,默认情况下包含文件夹和文件,单线程

    :param dir_path:文件夹绝对路径
    :param only_file:只包含文件
    :param only_dir:只包含文件夹
    :param deep:搜索深度,默认为0表示全部搜索,为1时表示只搜索该路径下不会搜索子目录,以此类推
    """
    if only_file and only_dir:
        raise ValueError(f'Fun包file模块下的get_files_path函数报错:\n  选项不可同时为True')
    path = []
    count = 0
    for root, dirs, files in os.walk(dir_path):
        # print("root", root)  # 当前目录路径
        # print("dirs", dirs)  # 当前路径下所有子目录
        # print("files", files)  # 当前路径下所有非目录子文件
        if deep == 0 or count <= deep:
            if not only_dir:
                for i in files:
                    # 添加该目录下文件的绝对路径
                    path.append(os.path.join(root, i))
            if not only_file:
                if root == dir_path:
                    continue
                path.append(root)  # 添加该目录下的全部目录绝对路径
        else:
            break
    return path


def get_files_path(dir_path: str = None, only_file=False, only_dir=False, deep=0) -> List[str]:
    """
    多线程获取指定目录下全部的文件路径,默认情况下包含文件夹和文件,多线程

    :param dir_path: 文件夹绝对路径
    :param only_file: 只包含文件
    :param only_dir: 只包含文件夹
    :param deep: 搜索深度,默认为0表示全部搜索,为1时表示只搜索该路径下不会搜索子目录,以此类推
    """
    if only_file and only_dir:
        raise ValueError(f'Fun包file模块下的get_files_path函数报错:\n  选项不可同时为True')

    if not dir_path or not os.path.isdir(dir_path):
        return []
    result_queue = Queue()
    threads = []
    max_threads = 10  # 最大线程数
    thread_semaphore = threading.Semaphore(max_threads)

    def process_directory(current_dir: str, current_depth: int):
        """处理单个目录并将结果放入队列"""
        with thread_semaphore:
            # 收集当前目录的文件（如果允许）
            if not only_dir:
                for filename in os.listdir(current_dir):
                    file_path = os.path.join(current_dir, filename)
                    if os.path.isfile(file_path):
                        result_queue.put(file_path)

            # 收集当前目录的子目录（如果允许）
            if not only_file:
                for dirname in os.listdir(current_dir):
                    subdir_path = os.path.join(current_dir, dirname)
                    if os.path.isdir(subdir_path) and subdir_path != current_dir:
                        result_queue.put(subdir_path)

            # 修复：递归条件不再受only_file影响，只要深度允许就继续搜索子目录
            # 即使only_file=True，也能深入子目录查找文件
            if deep == 0 or current_depth < deep:
                for dirname in os.listdir(current_dir):
                    subdir_path = os.path.join(current_dir, dirname)
                    if os.path.isdir(subdir_path) and subdir_path != current_dir:
                        thread = threading.Thread(
                            target=process_directory,
                            args=(subdir_path, current_depth + 1)
                        )
                        threads.append(thread)
                        thread.start()

    # 启动根目录处理
    root_thread = threading.Thread(
        target=process_directory,
        args=(dir_path, 1)  # 根目录为深度1
    )
    threads.append(root_thread)
    root_thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 收集结果
    result = []
    while not result_queue.empty():
        result.append(result_queue.get())

    return result


def get_files_size(file_path: str = None, unit='MB') -> float:
    """
    获取文件尺寸

    :param file_path: 文件路径
    :param unit: 度量单位MB、KB、B
    """
    if file_path is None:
        if FILE_PATH is not None:
            file_path = FILE_PATH
        else:
            raise ValueError('没有指定文件->请指定FILE_PATH或传入file_path')
    if unit == 'B':
        return os.path.getsize(file_path)
    elif unit == 'KB':
        return os.path.getsize(file_path) / 1024
    elif unit == 'MB':
        return os.path.getsize(file_path) / 1024 / 1024


def del_file(file_path: str) -> bool:
    """
    删除文件或者文件夹

    :param file_path:文件路径
    """
    try:
        file_path = os.path.realpath(file_path)
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        elif os.path.isfile(file_path):
            os.remove(file_path)
        return True
    except Exception as e:
        print(f'Fun包file模块下的del_file函数报错:\n  {file_path}{e}', file=sys.stderr)
        return False


def move_file(file_path: str, target_path: str, replace=False) -> bool:
    """
    移动文件或文件夹

    :param file_path:文件路径
    :param target_path:目标文件夹路径
    :param replace:文件存在时是否替换
    """
    try:
        if not os.path.isdir(target_path):
            raise ValueError('目标路径不是文件夹！')
        file_path = os.path.realpath(file_path)
        target_path = os.path.realpath(target_path)
        ensure_exist(target_path)
        if os.path.isfile(file_path):
            # 转为目标文件路径
            file_name = os.path.basename(file_path)
            tartat_path = os.path.join(file_path, file_name)
        # 文件不存在时移动
        if not os.path.exists(tartat_path):
            shutil.move(file_path, tartat_path)  # 移动文件
            return True
        # 开启替换时移动
        elif replace and os.path.exists(tartat_path):
            shutil.move(file_path, tartat_path)  # 移动文件
            return True
    except Exception as e:
        print(f'Fun包file模块下的move_file函数报错:\n  {file_path}{e}', file=sys.stderr)
        return False


def copy_file(file_path: str, target_path: str, replace=False) -> bool:
    """
    移动文件或文件夹

    :param file_path:文件路径
    :param target_path:目标文件夹路径
    :param replace:文件存在时是否替换
    """
    try:
        if not os.path.isdir(target_path):
            raise ValueError('目标路径不是文件夹！')
        file_path = os.path.realpath(file_path)
        target_path = os.path.realpath(target_path)
        ensure_exist(target_path)
        if os.path.isfile(file_path):
            # 转为目标文件路径
            file_name = os.path.basename(file_path)
            tartat_path = os.path.join(file_path, file_name)
        # 文件不存在时复制
        if not os.path.exists(tartat_path):
            shutil.copy(file_path, tartat_path)  # 移动文件
            return True
        # 开启替换时移动
        elif replace and os.path.exists(tartat_path):
            shutil.copy(file_path, tartat_path)  # 移动文件
            return True
    except Exception as e:
        print(f'Fun包file模块下的move_file函数报错:\n  {file_path}{e}', file=sys.stderr)
        return False
