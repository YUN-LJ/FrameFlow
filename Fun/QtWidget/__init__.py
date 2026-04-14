from PySide6.QtWidgets import QFileDialog
from Fun.BaseTools import Get
from Fun.QtWidget.FWidget import ImageWidget, LazyLoadMS, TrayIcon
from Fun.QtWidget.FTabel import TableCell, TableRow, TableBase

__all__ = ['ImageWidget', 'LazyLoadMS', 'TrayIcon',
           'TableCell', 'TableRow', 'TableBase']


def get_exist_dir(caption: str = '选择文件夹', dir_path: str = Get.run_dir()) -> str:
    """
    用于选择单个目录,外部调用时需要用lambda :方法

    :param caption:窗口标题
    :param dir_path:初始目录,默认为文件启动路径
    :return dir:str
    """
    dir = QFileDialog.getExistingDirectory(parent=None,  # 父对象
                                           caption=caption,  # 对话框标题提示词
                                           dir=dir_path,  # 默认显示目录
                                           options=QFileDialog.ShowDirsOnly  # 只显示文件夹
                                           )
    return dir


def get_exist_files(caption: str = '', dir_path: str = Get.run_dir(), ext=None) -> list[str]:
    """
    用于选择单个文件,外部调用时需要用lambda :方法
    :param caption:窗口标题
    :param dir_path:初始目录,默认为文件启动路径
    :param ext:设置文件的扩展名
    :return file:list[str]
    """
    # ext="视频(*.mp4;*.wmv;*.flv;*.avi);;文本(*.txt);;All file(*)"
    file, _ = QFileDialog.getOpenFileNames(None,  # 父对象
                                           caption,  # 窗口标题
                                           dir_path,  # 默认启动路径
                                           ext  # 选择格式
                                           )
    return file
