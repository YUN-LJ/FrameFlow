"""左侧布局"""
import random

from pyside6_GUI.sub_ui.wallpaper.widgetUI.Config import *


class LeftWidget(Ui_leftwidget, QWidget):
    LoadKeyUISigal = Signal(bool)  # 收藏夹表格UI加载信号
    LoadThumbSigal = Signal(tuple)  # 加载略缩图信号

    def __init__(self, wallpaper: WallPaperPlay, parent=None):
        super().__init__()
        self.wallpaper = wallpaper
        self.__parent = parent
        self.mode_value = None  # 当前模式
        # 全部的单元格{key:dict} 详细查看creatBaseCell的返回值
        self.all_cells = {}
        # 存储了加载过的略缩图
        self.__thumbs = {}
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

    def setThumb(self, key, image):
        """设置略缩图"""
        cell = self.all_cells.get(key, None)
        if cell is not None:
            if isinstance(image, tuple):
                cell['widget'].setTitle(f'共{image[0]}张')
                cell['image_widget'].set_image(image[1])
                self.__thumbs[key] = image[1]
            else:
                cell['image_widget'].set_image(image)
                self.__thumbs[key] = image

    def creatBaseCell(self, key) -> dict:
        """
        创建一个基本的单元格内容
        return: 包含了创建的全部控件的字典
        """
        # 构建基本框架
        widget = QGroupBox()
        widget.setTitle('共xxx张')
        # 添加垂直布局
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 5)
        layout.setSpacing(0)
        # 添加水平布局
        layout_checkbox = QHBoxLayout(widget)
        layout_checkbox.setContentsMargins(0, 0, 0, 0)
        layout_checkbox.setSpacing(0)
        layout.addLayout(layout_checkbox)
        # 添加内容控件
        checkBox = QCheckBox()
        image_widget = ImageWidget(self.__thumbs.get(key, None))
        # 添加到布局中
        layout_checkbox.addWidget(checkBox)
        layout.addWidget(image_widget)
        return {
            'widget': widget,
            'checkbox': checkBox,
            'image_widget': image_widget,
            'vlayout': layout,
            'hlayout': layout_checkbox,
            'self': self.mode_value  # 所属stackedWidget的索引
        }

    def setCustomMode(self, load_thumb=True):
        """
        设置为用户模式
        :param load_thumb: 是否加载略缩图
        """

        def create_cell(image_dir: str) -> QWidget:
            """生成一个单元格内容"""
            cell = self.creatBaseCell(image_dir)
            # 设置checkbox
            checkBox: QCheckBox = cell['checkbox']
            checkBox.setText(image_dir)
            checkBox.setChecked(image_dir in self.wallpaper.image_dir)
            checkBox.stateChanged.connect(
                lambda state, text=image_dir:
                self.wallpaper.add_dir(text) if state else self.wallpaper.del_dir(text)
            )
            button = PrimaryToolButton(FIF.DELETE)
            button.clicked.connect(
                lambda _, value=cell['widget']: (self.tableWidget_userDir.delWidget(value),
                                                 self.tableWidget_userDir.realign()))
            button.setFixedSize(30, 30)
            cell['hlayout'].addWidget(button)
            # 保存到实例属性中
            cell['button'] = button
            cell['self'] = 0
            self.all_cells[image_dir] = cell
            return cell['widget']

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
                    if not self.__thumbs.get(image_dir, False):
                        self.LoadThumbSigal.emit((image_dir, [(image_dir, image_dir)]))  # 发送需要加载略缩图
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
        load_thumb_dir = []
        for image_dir in self.wallpaper.image_dir:
            if image_dir not in self.all_cells:
                self.tableWidget_userDir.addWidget(
                    create_cell(image_dir),
                    lambda value=image_dir: create_cell(value))
            if image_dir not in self.__thumbs:
                load_thumb_dir.append((image_dir, image_dir))
        if 'add' not in self.all_cells:
            self.tableWidget_userDir.addWidget(
                create_add(), create_add)
        if load_thumb and load_thumb_dir:
            self.LoadThumbSigal.emit(('load_custom_thumb', load_thumb_dir))
        self.updateHight()

    def setKeyMode(self, load_thumb=True):
        """
        设置为收藏夹模式
        :param load_thumb: 是否加载略缩图
        """

        def create_cell(key: str) -> QWidget:
            """生成一个单元格内容"""
            cell = self.creatBaseCell(key)
            # 添加checkbox
            checkBox: QCheckBox = cell['checkbox']
            checkBox.setText(key)
            checkBox.setChecked(key in self.wallpaper.image_choice_key)
            checkBox.stateChanged.connect(
                lambda state, text=key:
                self.wallpaper.add_key(text) if state else self.wallpaper.del_key(text)
            )
            image_info = self.wallpaper.get_key_image_list(key)
            cell['widget'].setTitle(f'共{image_info.shape[0] if not image_info.empty else 0}张')
            # 保存到实例属性中
            cell['self'] = 1
            self.all_cells[key] = cell
            return cell['widget']

        load_thumb_dir = []
        # 获取全部关键词
        key_add = False if self.wallpaper.image_choice_key else True
        for key in self.wallpaper.image_key:
            if key_add:
                self.wallpaper.add_key(key)
            if key not in self.all_cells:
                self.tableWidget_key.addWidget(
                    create_cell(key),
                    lambda value=key: create_cell(value)
                )
            if key not in self.__thumbs:
                image_info = self.wallpaper.get_key_image_list(key)
                load_thumb_dir.append(
                    (key, image_info.loc[random.randint(0, image_info.shape[0] - 1), '本地路径'])
                )
        if load_thumb and load_thumb_dir:
            self.LoadThumbSigal.emit(('load_key_thumb', load_thumb_dir))
        self.updateHight()

    def setVideoMode(self):
        """设置为视频模式"""
        self.updateHight()

    def set_mode(self, value: int):
        if value == wallpaper.IMAGE_CUSTOM_MODE:
            self.mode_value = wallpaper.IMAGE_CUSTOM_MODE
            self.stackedWidget.setCurrentIndex(0)
            self.setCustomMode()
        elif value == wallpaper.IMAGE_KEY_MODE:
            self.mode_value = wallpaper.IMAGE_KEY_MODE
            self.stackedWidget.setCurrentIndex(1)
            self.setKeyMode()
        elif value == wallpaper.IMAGE_VIDEO_MODE:
            self.mode_value = wallpaper.IMAGE_VIDEO_MODE
            self.stackedWidget.setCurrentIndex(2)
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
        self.LoadKeyUISigal.connect(
            lambda value: self.setKeyMode(
                load_thumb=True if self.stackedWidget.currentIndex() == 1 else False)
            if value else None)
        self.tableWidget_userDir.delWidgetSignal.connect(self.__delWidget)
        self.tableWidget_userDir.addWidgetSignal.connect(self.updateHight)
        self.tableWidget_userDir.realignSignal.connect(self.updateHight)

    def updateHight(self):
        """自适应单元格高度,将自动调整单元格内的checkBox文件显示问题"""
        width = self.tableWidget_userDir.columnWidth(0)  # 获取列宽
        height = min(self.tableWidget_userDir.height() * 0.5, width * 4 / 3)
        # 根据当前列宽设置行高
        for table in self.stackedWidget.findChildren(QTableWidget):
            for row in range(table.rowCount()):
                table.setRowHeight(row, height)
        for text, cell in self.all_cells.items():
            checkBox: QCheckBox = cell.get('checkbox', None)
            if checkBox is not None:
                # 根据列宽自动调整文本换行符
                limit_width = checkBox.width()
                text_split = []
                weight = 0  # 权重,一个汉字的权重为21,其余字符权重为7
                for char in text:
                    if weight > limit_width:
                        text_split.append('\n')
                        weight = 0
                    weight += 21 if '\u4e00' <= char <= '\u9fff' else 7
                    text_split.append(char)
                checkBox.setText(''.join(text_split))

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
