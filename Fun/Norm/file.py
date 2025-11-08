"""
文件基础操作
"""
import os, sys, shutil

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


def check_exist(path: str | list[str]) -> bool:
    """检查文件是否存在"""
    if isinstance(path, str):
        # 单个路径直接检查
        return os.path.exists(path)
    else:
        # 列表路径批量检查（利用列表推导式高效循环）
        return [os.path.exists(p) for p in path]


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


def get_files_path_one(dir_path: str = None, only_file=False, only_dir=False, deep=0) -> list[str]:
    """
    获取指定目录下全部的文件路径,默认情况下包含文件夹和文件,单线程

    :param dir_path:文件夹绝对路径
    :param only_file:只包含文件
    :param only_dir:只包含文件夹
    :param deep:搜索深度,默认为0表示全部搜索,为1时表示只搜索该路径下不会搜索子目录,以此类推
    """
    import threading
    from queue import Queue
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


def get_files_path_old(dir_path: str = None, only_file=False, only_dir=False, deep=0) -> list[str]:
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


def get_files_path(dir_path: str = None,
                   only_file: bool = False,
                   only_dir: bool = False,
                   deep: int = 0,
                   ext: list[str] = None
                   ) -> list[str]:
    """
    获取指定目录下全部的文件路径,默认情况下包含文件夹和文件,单线程

    :param dir_path: 文件夹绝对路径
    :param only_file: 只包含文件
    :param only_dir: 只包含文件夹
    :param deep: 搜索深度,默认为0表示全部搜索,为1时表示只搜索该路径下不会搜索子目录,以此类推
    :param ext: 筛选指定后缀的文件（如 ['.jpg', '.png']），不区分大小写，为None时不筛选
    """
    # 参数校验：避免矛盾选项和无效目录
    if only_file and only_dir:
        raise ValueError("only_file和only_dir不能同时为True")
    if not dir_path or not os.path.isdir(dir_path):
        return []
    # 处理后缀参数：统一转为小写，确保不区分大小写
    valid_ext = [e.lower() for e in ext] if (ext and isinstance(ext, list)) else None

    # 处理正反斜杠问题
    dir_path = dir_path.replace('\\', '/')

    result = []

    def traverse(current_dir: str, current_depth: int):
        # 遍历当前目录（使用os.scandir提升效率）
        try:
            with os.scandir(current_dir) as entries:
                for entry in entries:
                    # 处理文件
                    if entry.is_file():
                        # 满足条件：1.允许包含文件 2.后缀符合筛选（无筛选时直接通过）
                        if not only_dir:
                            # 后缀筛选逻辑
                            if valid_ext is None:
                                result.append(entry.path.replace('\\', '/'))
                            else:
                                # 获取文件后缀并转为小写，匹配筛选列表
                                file_ext = os.path.splitext(entry.name)[1].lower()
                                if file_ext in valid_ext:
                                    result.append(entry.path.replace('\\', '/'))
                    # 处理目录
                    elif entry.is_dir(follow_symlinks=False):
                        # 允许包含目录时添加
                        if not only_file:
                            result.append(entry.path.replace('\\', '/'))
                        # 递归遍历子目录（根据深度限制判断）
                        if (deep == 0 or current_depth < deep):
                            traverse(entry.path, current_depth + 1)
        except PermissionError:
            print(f"无权限访问目录：{current_dir}")
        except OSError as e:
            print(f"访问目录出错 {current_dir}：{e}")

    # 启动遍历（根目录深度为1）
    traverse(dir_path, current_depth=1)
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


def get_user_PicturesPath() -> str:
    """
    获取用户图库路径
    """
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
    value, _ = winreg.QueryValueEx(key, "My Pictures")
    winreg.CloseKey(key)
    return value


def get_user_DesktopPath() -> str:
    """
    获取用户桌面路径
    """
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
        desktop_path, _ = winreg.QueryValueEx(key, "Desktop")
        return desktop_path


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
        file_path = os.path.realpath(file_path)
        target_path = os.path.realpath(target_path)
        ensure_exist(target_path)
        if os.path.isfile(file_path):
            # 转为目标文件路径
            file_name = os.path.basename(file_path)
            target_path = os.path.join(target_path, file_name)
        # 文件不存在时移动
        if not os.path.exists(target_path):
            shutil.move(file_path, target_path)  # 移动文件
            return True
        # 开启替换时移动
        elif replace and os.path.exists(target_path):
            shutil.move(file_path, target_path)  # 移动文件
            return True
    except Exception as e:
        print(f'Fun包file模块下的move_file函数报错:\n\t{file_path}{e}', file=sys.stderr)
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
