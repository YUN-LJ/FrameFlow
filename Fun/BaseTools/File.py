"""文件处理包"""
import os
import re
import cv2
import struct
import shutil
import win32con
import subprocess
import numpy as np
import configparser
import win32clipboard
from typing import Optional
from io import BytesIO

IMAGE_EXTENSION = {'.png', '.jpg', '.jpeg'}  # 照片格式


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


# 文件类
class FileBase:
    """文件类"""

    def __init__(self, path: str):
        self.path = os.path.realpath(path)

    @property
    def is_file(self) -> bool:
        """当文件存在且为文件时返回True"""
        return os.path.isfile(self.path)

    @property
    def is_dir(self) -> bool:
        """当文件存在且为文件夹时返回True"""
        return os.path.isdir(self.path)

    @property
    def is_image(self) -> bool:
        """当文件存在且是图片时返回True,只检查扩展名"""
        if self.exists:
            return self.extension in IMAGE_EXTENSION
        return False

    @property
    def exists(self) -> bool:
        """检查文件是否存在"""
        return os.path.exists(self.path)

    def ensure_exists(self):
        """确保文件夹存在"""
        if not self.exists:
            os.makedirs(self.path)

    @property
    def extension(self) -> str:
        """扩展名"""
        return os.path.splitext(self.path)[1]

    @property
    def name(self) -> str:
        """文件名(含扩展名)"""
        return os.path.basename(self.path)

    @property
    def name_base(self) -> str:
        """文件名(无扩展名)"""
        return self.name.split('.')[0]

    @property
    def dir_name(self) -> str:
        """文件夹名"""
        return os.path.dirname(self.path)

    def join(self, *args) -> Optional['FileBase']:
        """拼接路径"""
        self.path = os.path.join(self.path, *args)
        return self

    def size(self, unit='MB') -> float:
        """获取文件尺寸"""
        if self.exists:
            size = os.path.getsize(self.path)
            if unit == 'B':
                return size
            elif unit == 'KB':
                return size / 1024
            elif unit == 'MB':
                return size / 1024 / 1024
        return 0

    def open_use_explorer(self):
        """在资源管理器打开文件并选中"""
        subprocess.Popen(f'explorer /select, {self.path}')

    def open_bytesIO(self) -> BytesIO:
        if self.is_file:
            with open(self.path, 'rb') as f:
                return BytesIO(f.read())

    def delete(self):
        """删除"""
        if self.exists:
            if self.is_dir:
                shutil.rmtree(self.path)
            elif self.is_file:
                os.remove(self.path)

    def move(self, target_path: str, cover: bool = False) -> Optional['FileBase']:
        """
        移动文件

        :param target_path:目标文件夹路径
        :param cover:是否覆盖,默认不覆盖
        """
        if not self.exists:
            raise FileNotFoundError(f"源文件不存在: {self.path}")
        target = target_path if not os.path.isdir(target_path) else os.path.join(target_path, self.name)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        if os.path.exists(target) and not cover:
            raise FileExistsError(f"目标文件已存在: {target}")
        if os.path.exists(target) and cover:
            if os.path.isdir(target):
                shutil.rmtree(target)
            else:
                os.remove(target)
        shutil.move(self.path, target)
        self.path = os.path.realpath(target)
        return self  # 返回自身支持链式调用

    def copy(self, target_path: str, cover: bool = False) -> Optional['FileBase'] | None:
        """
        复制文件或文件夹到目标位置

        :param target_path: 目标路径（可以是目录路径或完整文件路径）
        :param cover: 是否覆盖已存在的文件，默认False
        :return: 新的File对象
        """
        # 检查源文件是否存在
        if not self.exists:
            raise FileNotFoundError(f"源文件不存在: {self.path}")
        # 转换目标路径为File对象
        target = FileBase(target_path)
        # 判断目标路径是目录还是文件路径
        if target.is_dir or target_path.endswith(('\\', '/')):
            # 目标是一个目录，保持原文件名
            target_path_full = os.path.join(target.path, self.name)
        else:
            # 目标是一个完整文件路径
            target_path_full = target.path
        # 确保目标目录存在
        target_dir = os.path.dirname(target_path_full)
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)
        # 检查目标文件是否已存在
        if os.path.exists(target_path_full):
            if cover:
                # 覆盖模式：删除已存在的目标
                if os.path.isdir(target_path_full):
                    shutil.rmtree(target_path_full)
                else:
                    os.remove(target_path_full)
            else:
                raise FileExistsError(f"目标文件已存在: {target.path}")
        # 执行复制
        if self.is_dir:
            # 复制文件夹
            shutil.copytree(self.path, target_path_full)
        else:
            # 复制文件
            shutil.copy2(self.path, target_path_full)  # copy2 会保留元数据
        # 返回新文件的File对象
        return FileBase(target_path_full)

    def copy_to_clipboard(self, file_paths: str | list = None):
        """复制文件到剪贴板"""
        if isinstance(file_paths, str):
            file_paths = [file_paths]
        else:
            file_paths = [self.path]

        # 转换为绝对路径
        file_paths = [os.path.abspath(p) for p in file_paths if os.path.exists(p)]

        if not file_paths:
            return

        # 构建 DROPFILES 结构
        # 文件列表：每个文件路径以 null 结尾，最后双 null 结束
        paths_bytes = []
        for path in file_paths:
            # Windows 使用 UTF-16 LE
            paths_bytes.append(path.encode('utf-16le'))

        # 计算总大小
        struct_size = 20  # DROPFILES 结构大小
        files_size = sum(len(p) + 2 for p in paths_bytes)  # 每个文件加 \0\0
        total_size = struct_size + files_size + 2  # 最后加 \0\0

        # 构建数据
        data = bytearray(total_size)

        # DROPFILES 结构
        struct.pack_into('<I', data, 0, struct_size)  # pFiles
        struct.pack_into('<I', data, 16, 1)  # fWide = 1 (使用宽字符)

        # 文件列表从偏移 20 开始
        offset = struct_size
        for path_bytes in paths_bytes:
            data[offset:offset + len(path_bytes)] = path_bytes
            offset += len(path_bytes)
            data[offset:offset + 2] = b'\0\0'  # UTF-16 null
            offset += 2

        # 最后的结束符
        data[offset:offset + 2] = b'\0\0'

        # 写入剪贴板
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_HDROP, data)

            # 同时设置文本格式（可选）
            text = '\n'.join(os.path.basename(p) for p in file_paths)
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        finally:
            win32clipboard.CloseClipboard()


class ImageFileBase(FileBase):
    def __init__(self, path: str):
        super().__init__(path)

    def open_image_array(self) -> np.ndarray:
        """打开图像并返回array数组"""
        if self.is_image:
            with open(self.path, 'rb') as f:
                array = np.frombuffer(f.read(), np.uint8)  # 读取数据
                image = cv2.imdecode(array, cv2.IMREAD_UNCHANGED)  # 解码图像
                return image

    def show_image(self):
        if self.is_image:
            cv2.imshow(self.name, self.open_image_array())


class EasyConfig:
    """
    便捷的存储配置文件
    该类在存储数据时会自动存储数据类型并在读取时转为python数据类型
    目前支持的数据类型:int、float、str、list、bool
    """

    def __init__(self, config_file: str = None, cur_section=None):
        """
        :param config_file:文件路径
        :param cur_section:当前要操作的节
        """
        self.cur_section = 'default'
        if cur_section is not None:
            self.set_section(cur_section)
        self.config_data = {}  # 存储的数据
        self.config_file = config_file

    def __str__(self):
        return str(self.config_data)

    def __repr__(self):
        return str(self.config_data)

    def load_config(self) -> bool:
        """加载本地配置文件"""
        if self.config_file is not None and check_exist(self.config_file):
            config = configparser.RawConfigParser()  # 实际存储数据的
            config.optionxform = lambda option: option  # 防止保存文件时键值小写
            config.read(self.config_file, encoding='utf-8')
            for section in config.sections():
                # 获取当前节的全部数据,数据格式是[(值名,值)]并转为字典类型
                value_dict = {}
                for key, value in config.items(section):
                    # 匹配规则去AI上查,()为只保留的匹配内容
                    if value.find('type=<class ') != 0:
                        value_type = re.findall(r" type=<class '(\w*)'>$", value)[0]
                        value = re.findall(r"(.*) type=<class '\w*'>$", value)[0]
                        if value_type == 'list':
                            value = value.split(';')
                        elif value_type == 'bool':
                            value = True if value == 'True' else False
                        elif value_type == 'int':
                            value = int(value)
                        elif value_type == 'float':
                            value = float(value)
                        value_dict[key] = value
                self.config_data[section] = value_dict
            return True
        return False

    def set_section(self, section: str) -> bool:
        """设置当前要操作的节,如果不存在则会创建"""
        if section not in self.config_data:
            self.add_section(section)
        self.cur_section = section

    def set_file_path(self, file_path: str):
        """设置文件路径"""
        self.config_file = file_path

    def add_section(self, section_name: str) -> bool:
        """
        新增节
        :param section_name:要添加的节的名称
        """
        if section_name not in self.config_data:
            self.config_data[section_name] = {}
            return True
        return False

    def add_values(self, value_dict: dict, section_name=None) -> bool:
        """
        新增数据

        :param value_dict:要添加的数据,数据格式{值名:值}
        :param section_name:将数据添加在哪个节下面,默认为当前操作的节,节不存在时会创建该节
        """
        if section_name is None:
            section_name = self.cur_section
        target_section = self.config_data.get(section_name, None)
        if target_section is None:
            self.add_section(section_name)
        self.config_data[section_name].update(value_dict)
        return True

    def del_section(self, section_name=None) -> bool:
        """
        删除节

        :param section_name:要删除的节的名称
        """
        if section_name is None:
            section_name = self.cur_section
        if section_name in self.config_data:
            del self.config_data[section_name]
            return True
        return False

    def del_values(self, value_name: str | list, section_name=None) -> bool:
        """
        删除数据

        :param section_name:要删除的数据在哪个节下面
        :param value_name:要删除的数据列表名称
        """
        if section_name is None:
            section_name = self.cur_section
        if isinstance(value_name, str):
            value_name = [value_name]
        target_section = self.config_data.get(section_name, None)
        if target_section is not None:
            for name in value_name:
                target_section.pop(name, None)
            return True
        return False

    def get_sections(self) -> list:
        """
        获取ini文件的全部节
        返回所有节列表,没有内容时返回[]
        """
        return list[self.config_data.keys()]

    def get_values(self, value_name: str = None, section_name: str = None) -> dict | list | str | float | int:
        """
        获取指定变量名的数据内容,不指定时默认返回全部
        返回数据内容,指定变量名时返回str类型,否则返回dict
        """
        if section_name is None:
            section_name = self.cur_section
        if section_name in self.config_data:
            if value_name is None:
                return self.config_data[section_name]
            else:
                return self.config_data[section_name].get(value_name, {})

    def save(self):
        if self.config_file is not None:
            FileBase(os.path.dirname(self.config_file)).ensure_exists()
            config = configparser.RawConfigParser()  # 实际存储数据的
            config.optionxform = lambda option: option  # 防止保存文件时键值小写
            for section, value in self.config_data.items():
                config.add_section(section)
                for key, value in value.items():
                    value_type = type(value)
                    if value_type in [int, float, list, str, bool]:
                        if value_type == list:
                            value = ';'.join(value) if value else ''
                        value = f'{value} type={value_type}'
                        config.set(section, key, value)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                config.write(f)
