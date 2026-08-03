"""搜索配置"""
from SubAPI.WallHaven.ImportPack import *
from SubAPI.WallHaven import api
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SubAPI.WallHaven.Desktop import SearchPage

TOP_PARENT = None


class SearchConfig(FluentWidgetBase):

    def __init__(self, parent: 'SearchPage' = None):
        super().__init__(parent)
        self.parent = parent
        self.slot = SearchConfigSlot(self)
        self.__uiInit()
        self.__bind()

    def __uiInit(self):
        # 与搜索按钮
        self.pushButton_header = HeaderCardWidget(title='内置搜索', parent=self)
        self.pushButton_latest = PrimaryPushButton(text='最新', parent=self)
        self.pushButton_hot = PrimaryPushButton(text='最热', parent=self)
        self.pushButton_header.viewLayout.addWidget(self.pushButton_latest)
        self.pushButton_header.viewLayout.addWidget(self.pushButton_hot)
        self.pushButton_header.viewLayout.addStretch()
        self.view_layout.addWidget(self.pushButton_header)

        # 搜索分类/类别
        self.wallhaven_class = GlobalValue.WallHavenClassWidget(self)
        self.checkBoxsCategories = [self.wallhaven_class.checkBox_general,
                                    self.wallhaven_class.checkBox_anime,
                                    self.wallhaven_class.checkBox_people]
        self.checkBoxsPurity = [self.wallhaven_class.checkBox_sfw,
                                self.wallhaven_class.checkBox_sketchy,
                                self.wallhaven_class.checkBox_nsfw]
        self.view_layout.addWidget(self.wallhaven_class)

        # 搜索切换
        self.checkBox_header = HeaderCardWidget(title='搜索切换', parent=self)
        self.checkBox_use_network = SwitchButton(text='本地搜索', parent=self)
        self.checkBox_use_network.setOnText('联网搜索')
        self.checkBox_use_tags = SwitchButton(text='检索关键词', parent=self)
        self.checkBox_use_tags.setOnText('检索标签')
        self.checkBox_header.viewLayout.addWidget(self.checkBox_use_network)
        self.checkBox_header.viewLayout.addWidget(self.checkBox_use_tags)
        self.view_layout.addWidget(self.checkBox_header)

    def __bind(self):
        # 根据配置文件设置UI状态
        self.checkBox_use_network.checkedChanged.connect(self.slot.checkBox_use_network)
        self.checkBox_use_network.setChecked(api.Config.USE_NETWORK)
        self.checkBox_use_tags.checkedChanged.connect(self.slot.checkBox_use_tags)
        self.checkBox_use_tags.setChecked(api.Config.USE_TAGS)

        for obj in self.checkBoxsCategories:
            obj.toggled.connect(self.slot.checkBoxsCategories)
        for obj in self.checkBoxsPurity:
            obj.toggled.connect(self.slot.checkBoxsPurity)
        # 设置选中状态
        purity = api.get_search_params().purity
        for index, obj in enumerate(self.checkBoxsPurity):
            obj.setChecked(int(purity[index]))
        categories = api.get_search_params().categories
        for index, obj in enumerate(self.checkBoxsCategories):
            obj.setChecked(int(categories[index]))


class SearchConfigSlot:
    def __init__(self, parent: 'SearchConfig'):
        self.parent = parent

    @staticmethod
    def checkBox_use_tags(checked):
        SEARCH_DATA.clear()
        api.Config.USE_TAGS = checked

    @staticmethod
    def checkBox_use_network(checked):
        SEARCH_DATA.clear()
        if checked:
            api.Config.USE_NETWORK = True
        else:
            api.Config.USE_NETWORK = False

    def checkBoxsCategories(self):
        categories = []
        for obj in self.parent.checkBoxsCategories:
            categories.append(str(int(obj.isChecked())))
            obj.setEnabled(True)
        categories = ''.join(categories)
        if categories.count('1') == 1:
            self.parent.checkBoxsCategories[categories.find('1')].setEnabled(False)

    def checkBoxsPurity(self):
        purity = []
        for obj in self.parent.checkBoxsPurity:
            purity.append(str(int(obj.isChecked())))
            obj.setEnabled(True)
        purity = ''.join(purity)
        if purity.count('1') == 1:
            self.parent.checkBoxsPurity[purity.find('1')].setEnabled(False)

        checked = bool(api.Config.API_KEY) if self.parent.checkBox_use_network.isChecked() else True
        self.parent.wallhaven_class.checkBox_nsfw.setEnabled(checked)
