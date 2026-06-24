"""
主页
各个Page结尾的为子窗口
SlotFunc内为各窗口控件文件(数据层与显示层分离设计)
WorkFlow为具体工作流
"""
from SubWidget.ImportPack import *


class HomeWin(FluentWidgetBase):

    def __init__(self, parent=None):
        super().__init__(parent)
