"""常用工具包"""
import os
from Fun.BaseTools.File import File, ImageFile
from Fun.BaseTools.Image import ImageLoad, ImageProcess, ImageEnum

__all__ = ['File', 'ImageFile', 'ImageLoad', 'ImageProcess', 'ImageEnum',
           'check_exist', 'get_files_path']


def check_exist(path: str | list[str], num_work=os.cpu_count(), chunk_size=1000) -> bool | list[bool]:
    """检查文件是否存在"""
    if isinstance(path, str):
        # 单个路径直接检查
        return os.path.exists(path)
    else:
        if len(path) < chunk_size:
            # 列表路径批量检查（利用列表推导式高效循环）
            return [os.path.exists(p) for p in path]
        else:
            # 使用多线程批量检查
            def split_list_generator(lst):
                """生成器版本，节省内存"""
                nonlocal chunk_size
                for i in range(0, len(lst), chunk_size):
                    yield lst[i:i + chunk_size]

            from multiprocessing.dummy import Pool
            with Pool(num_work) as pool:
                chunk_results = pool.map(lambda value: [os.path.exists(p) for p in value],
                                         split_list_generator(path))
            results = []
            for chunk_result in chunk_results:
                results.extend(chunk_result)
            return results


def get_files_path(dir_path: str = None, only_file: bool = False, only_dir: bool = False, deep: int = 0,
                   ext: list[str] = None) -> list[str]:
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
