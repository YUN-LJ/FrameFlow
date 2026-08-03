"""设置界面"""
from SubAPI.WallPaper.ImportPack import *
from SubAPI.WallPaper import api


class SetWidget(FluentWidgetBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.slot = SetSlot(self)
        self.__initUI()
        self.__bind()

    def __initUI(self):
        self.__add_class_widget()
        self.__add_play_time_widget()
        self.__add_play_mode_widget()
        self.__add_play_order_widget()

    def __add_class_widget(self):
        """添加类别和分类选择"""
        self.widget_class = GlobalValue.WallHavenClassWidget(self)
        self.view_layout.addWidget(self.widget_class)

        for purity in api.Config.IMAGE_CHOICE_PURITY:
            if purity == '正常级':
                self.widget_class.checkBox_sfw.setChecked(True)
            elif purity == '粗略级':
                self.widget_class.checkBox_sketchy.setChecked(True)
            else:
                self.widget_class.checkBox_nsfw.setChecked(True)
        for category in api.Config.IMAGE_CHOICE_CATEGORIES:
            if category == '常规':
                self.widget_class.checkBox_general.setChecked(True)
            elif category == '动漫':
                self.widget_class.checkBox_anime.setChecked(True)
            elif category == '人物':
                self.widget_class.checkBox_people.setChecked(True)

    def __add_play_time_widget(self):
        """添加播放时间"""
        self.play_time_widget = HeaderCardWidget(self)
        self.play_time_widget.setTitle('播放间隔')
        self.view_layout.addWidget(self.play_time_widget)

        self.spinBox_time = SpinBox(self.play_time_widget)
        self.spinBox_time.setMinimum(1)
        self.spinBox_time.setMaximum(600)
        self.play_time_widget.viewLayout.addWidget(self.spinBox_time)
        self.play_time_widget.viewLayout.addStretch()

    def __add_play_mode_widget(self):
        """添加播放模式"""
        self.play_mode_widget = HeaderCardWidget(self)
        self.play_mode_widget.setTitle('播放模式')
        self.view_layout.addWidget(self.play_mode_widget)

        self.comboBox_mode = ComboBox(self.play_mode_widget)
        self.comboBox_mode.addItems(['用户模式', '收藏夹模式', '视频模式'])
        self.play_mode_widget.viewLayout.addWidget(self.comboBox_mode)
        self.play_mode_widget.viewLayout.addStretch()

    def __add_play_order_widget(self):
        """添加播放顺序"""
        self.play_order_widget = HeaderCardWidget(self)
        self.play_order_widget.setTitle('播放顺序')
        self.view_layout.addWidget(self.play_order_widget)

        self.comboBox_order = ComboBox(self.play_order_widget)
        self.comboBox_order.addItems(['日期', '随机'])
        self.play_order_widget.viewLayout.addWidget(self.comboBox_order)
        self.play_order_widget.viewLayout.addStretch()

    def __bind(self):
        self.widget_class.checkBox_general.toggled.connect(
            lambda checked: api.select_categories('常规')
            if checked else api.deselect_categories('常规')
        )
        self.widget_class.checkBox_anime.toggled.connect(
            lambda checked: api.select_categories('动漫')
            if checked else api.deselect_categories('动漫')
        )
        self.widget_class.checkBox_people.toggled.connect(
            lambda checked: api.select_categories('人物')
            if checked else api.deselect_categories('人物')
        )
        self.widget_class.checkBox_sfw.toggled.connect(
            lambda checked: api.select_purity('正常级')
            if checked else api.deselect_purity('正常级')
        )
        self.widget_class.checkBox_sketchy.toggled.connect(
            lambda checked: api.select_purity('粗略级')
            if checked else api.deselect_purity('粗略级')
        )
        self.widget_class.checkBox_nsfw.toggled.connect(
            lambda checked: api.select_purity('限制级')
            if checked else api.deselect_purity('限制级')
        )
        # 防抖定时器
        self.spinBox_time_timer = debouncer_timer(self.slot.spinBox_time_timer)

        self.spinBox_time.valueChanged.connect(lambda _: self.spinBox_time_timer.start(500))
        # 设置UI初始值
        self.spinBox_time.setValue(api.Config.IMAGE_TIME)
        self.comboBox_mode.setCurrentIndex(api.Config.IMAGE_PLAY_MODE)
        self.comboBox_order.setCurrentIndex(int(api.Config.IMAGE_PLAY_SORT))
        self.comboBox_order.currentIndexChanged.connect(lambda index: api.set_sample(bool(index)))

    def showEvent(self, event):
        self.spinBox_time.setMinimumWidth(self.width() // 2)
        self.comboBox_mode.setMinimumWidth(self.width() // 2)
        self.comboBox_order.setMinimumWidth(self.width() // 2)
        super().showEvent(event)


class SetSlot:
    """信号槽"""

    def __init__(self, parent: SetWidget):
        self.parent = parent
        self.wallpaper_api = api.WallPaperAPI()

    def spinBox_time_timer(self):
        value = self.parent.spinBox_time.value()
        self.wallpaper_api.set_image_play_time(value)
