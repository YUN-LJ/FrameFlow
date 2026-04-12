"""文件处理包"""
import os
import cv2
import shutil
import subprocess
import numpy as np
from typing import Optional
from io import BytesIO

IMAGE_EXTENSION = {'.png', '.jpg', '.jpeg'}  # 照片格式


# 文件类
class File:
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

    def join(self, *args) -> Optional['File']:
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

    def move(self, target_path: str, cover: bool = False) -> Optional['File']:
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

    def copy(self, target_path: str, cover: bool = False) -> Optional['File'] | None:
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
        target = File(target_path)
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
        return File(target_path_full)


class ImageFile(File):
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
