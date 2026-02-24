"""左侧布局"""
import wallpaper
from pyside6_GUI.sub_ui.wallpaper.widgetUI.Config import *


class LeftWidget(Ui_leftwidget, QWidget):
    def __init__(self, wallpaper: WallPaperPlay, parent=None):
        super().__init__()
        self.wallpaper = wallpaper
        self.__parent = parent
        self.all_cells_custom = {}  # 用户模式下的全部单元格{本地路径:{'widget','checkbox','image','button'}}
        self.setupUi(self)
        self.uiIint()
        self.bind()

    def setCustomMode(self):
        """设置为用户模式"""

        def create_cell(image_dir: str) -> QWidget:
            """生成一个单元格内容"""
            # 创建容器
            widget = QWidget(self)
            # 添加垂直布局
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            # 添加checkbox
            checkBox = QCheckBox(text=image_dir)
            layout.addWidget(checkBox)
            print(111)
            if self.wallpaper.get_image_list():
                # 添加图片控件
                image = ImageWidget(self.wallpaper.image_list[0])

        # 添加数据
        for image_dir in self.wallpaper.image_dir:
            if image_dir not in self.all_cells_custom:
                self.add_cell(create_cell(image_dir))

    def set_mode(self, value: int):
        if value == wallpaper.IMAGE_CUSTOM_MODE:
            self.setCustomMode()
        elif value == wallpaper.IMAGE_KEY_MODE:
            pass
        elif value == wallpaper.IMAGE_VIDEO_MODE:
            pass

    def add_cell(self, widget: QWidget):
        """添加一个单元格内容"""

    def uiIint(self):
        """界面初始化"""
        # 设置列数
        self.tableWidget_userDir.setColumnCount(4)
        # 自适应列宽
        self.tableWidget_userDir.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 禁止编辑
        self.tableWidget_userDir.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 隐藏垂直表头即左侧表头
        self.tableWidget_userDir.verticalHeader().setVisible(True)
        # 隐藏水平表头即顶侧表头
        self.tableWidget_userDir.horizontalHeader().setVisible(False)
        # 交替行变色
        self.tableWidget_userDir.setAlternatingRowColors(True)

    def bind(self):
        """槽函数绑定"""
