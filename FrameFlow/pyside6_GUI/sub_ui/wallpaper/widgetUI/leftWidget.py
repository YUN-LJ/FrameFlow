"""左侧布局"""
from pyside6_GUI.sub_ui.wallpaper.widgetUI.Config import *

THUMB_SIZE = (512, 512)  # 略缩图尺寸


class LeftWidget(Ui_leftwidget, QWidget):

    def __init__(self, wallpaper: WallPaperPlay, parent=None):
        super().__init__()
        self.wallpaper = wallpaper
        self.__parent = parent
        self.mode_value = None  # 当前模式
        # 全部的单元格{key:{'widget','checkbox','image_widget','button'}},部分单元格内不一定有全部控件
        self.all_cells = {}
        self.__thumb = {}  # 打开的图片
        self.setupUi(self)
        self.uiIint()
        self.bind()

    def __delWidget(self, widget: QWidget):
        """表格内单元格被删除时触发信号"""
        checkBox = widget.findChild(QCheckBox)
        if checkBox is not None:
            key = checkBox.text().replace('\n', '')
            del self.all_cells[key]
            self.wallpaper.del_dir(key)
        self.updateHight()

    def setCustomMode(self):
        """设置为用户模式"""
        self.mode_value = wallpaper.IMAGE_CUSTOM_MODE
        self.stackedWidget.setCurrentIndex(0)

        def create_cell(image_dir: str) -> QWidget:
            """生成一个单元格内容"""
            # 创建容器
            widget = QWidget()
            # 添加垂直布局
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            # 添加checkbox,button
            layout_button = QHBoxLayout(widget)
            layout_button.setContentsMargins(0, 0, 0, 0)
            layout_button.setSpacing(0)
            checkBox = QCheckBox(text=image_dir)
            checkBox.setChecked(image_dir in self.wallpaper.image_dir)
            checkBox.stateChanged.connect(
                lambda state, text=image_dir:
                self.wallpaper.add_dir(text) if state else self.wallpaper.del_dir(text)
            )
            button = PrimaryToolButton(FIF.DELETE)
            button.clicked.connect(
                lambda _, value=widget: (self.tableWidget_userDir.delWidget(value),
                                         self.tableWidget_userDir.realign()))
            button.setFixedSize(30, 30)
            layout_button.addWidget(checkBox)
            layout_button.addWidget(button)
            layout.addLayout(layout_button)
            image_widget = ImageWidget()
            image_widget.enable_zoom_and_drag()
            image = self.__thumb.get(image_dir, None)
            if image is None:  # 设置图片
                image_list = file.get_files_path(image_dir, only_file=True, ext=file.IMAGE_EXTENSION)
                if image_list:
                    image = Image_PIL(random.choice(image_list))
                    image.resize(THUMB_SIZE)
                    image = image.get_BytesIO
                    self.__thumb[image_dir] = image
            image_widget.set_image(image)
            layout.addWidget(image_widget)
            # 保存到实例属性中
            self.all_cells[image_dir] = {
                'widget': widget,
                'checkbox': checkBox,
                'image': image,
                'image_widget': image_widget if image_widget is not None else None,
                'button': button}
            return widget

        def create_add() -> QWidget:
            """创建一个新增单元格"""

            def button_add(widget: QWidget):
                """新增目录"""
                last_dir = os.path.dirname(self.wallpaper.image_dir[-1]) if self.wallpaper.image_dir else '.'
                image_dir = get_exist_dir(caption='选择播放目录', dir_path=last_dir)
                if image_dir and image_dir not in self.all_cells:
                    self.tableWidget_userDir.delWidget(widget)
                    self.tableWidget_userDir.realign()  # 重新调整部件
                    self.wallpaper.add_dir(image_dir)
                    self.tableWidget_userDir.addWidget(
                        create_cell(image_dir),
                        lambda value=image_dir: create_cell(value))
                    self.tableWidget_userDir.addWidget(
                        create_add(), create_add)
                else:
                    TeachingTip.create(
                        target=widget,
                        icon=InfoBarIcon.ERROR,
                        title='添加错误',
                        content=f'未选择或已存在!',
                        isClosable=True,
                        tailPosition=TeachingTipTailPosition.BOTTOM,
                        duration=3000,
                        parent=self.__parent)

            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(0)
            label = QLabel(text='新增目录')
            layout.addWidget(label)
            button = PrimaryToolButton(FIF.FOLDER_ADD)
            button.clicked.connect(lambda _, value=widget: button_add(value))
            layout.addWidget(button)
            self.all_cells['add'] = {
                'widget': widget,
                'button': button,
            }
            return widget

        # 添加数据
        for image_dir in self.wallpaper.image_dir:
            if image_dir not in self.all_cells:
                self.tableWidget_userDir.addWidget(
                    create_cell(image_dir),
                    lambda value=image_dir: create_cell(value))
        if 'add' not in self.all_cells:
            self.tableWidget_userDir.addWidget(
                create_add(), create_add)

    def setKeyMode(self):
        """设置为收藏夹模式"""
        self.mode_value = wallpaper.IMAGE_KEY_MODE
        self.stackedWidget.setCurrentIndex(1)

    def setVideoMode(self):
        """设置为视频模式"""
        self.mode_value = wallpaper.IMAGE_VIDEO_MODE
        self.stackedWidget.setCurrentIndex(2)

    def set_mode(self, value: int):
        if value == wallpaper.IMAGE_CUSTOM_MODE:
            self.setCustomMode()
        elif value == wallpaper.IMAGE_KEY_MODE:
            self.setKeyMode()
        elif value == wallpaper.IMAGE_VIDEO_MODE:
            self.setVideoMode()

    def uiIint(self):
        """界面初始化"""
        for table in self.stackedWidget.findChildren(QTableWidget):
            # 设置列数
            table.setColumnCount(3)
            # 自适应列宽
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            # 禁止编辑
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            # 隐藏垂直表头即左侧表头
            table.verticalHeader().setVisible(True)
            # 隐藏水平表头即顶侧表头
            table.horizontalHeader().setVisible(False)
            # 交替行变色
            table.setAlternatingRowColors(True)

    def bind(self):
        """槽函数绑定"""
        self.tableWidget_userDir.delWidgetSignal.connect(self.__delWidget)
        self.tableWidget_userDir.addWidgetSignal.connect(self.updateHight)
        self.tableWidget_userDir.realignSignal.connect(self.updateHight)

    def updateHight(self):
        """自适应单元格高度,将自动调整单元格内的checkBox文件显示问题"""
        width = self.tableWidget_userDir.columnWidth(0)  # 获取列宽
        height = min(self.tableWidget_userDir.height() * 0.5, width * 4 / 3)
        # 根据当前列宽设置行高
        for row in range(self.tableWidget_userDir.rowCount()):
            self.tableWidget_userDir.setRowHeight(row, height)
        for text, cell in self.all_cells.items():
            # 根据列宽自动调整文本换行符
            text = '\n'.join([text[i:i + int(width / 8)] for i in range(0, len(text), int(width / 8))])
            checkBox = cell.get('checkbox', None)
            if checkBox is not None:
                checkBox.setText(text)

    def showEvent(self, event):
        """重写showEvent，在控件显示时调用"""
        super().showEvent(event)
        self.updateHight()

    def closeEvent(self, event):
        super().closeEvent(event)
        for path in self.all_cells.keys():
            if os.path.isdir(path):
                self.wallpaper.add_dir(path)

    def resizeEvent(self, event):
        """自适应列宽"""
        super().resizeEvent(event)
        self.updateHight()
        self.update()
