"""设置界面"""
from SubAPI.WallPaper.ImportPack import *
from SubAPI.WallPaper import api
from SubAPI.WallPaper.Desktop.SetPage.DesignFile.SetDialog import Ui_Sets


class SetWidget(FluentWidgetFromUI, Ui_Sets):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__bind()

    def __initUI(self):
        self.checkBox_use_tag.setOnText("使用标签")
        self.checkBox_use_tag.setOffText("使用关键词")
        for purity in api.Config.IMAGE_CHOICE_PURITY:
            if purity == '正常级':
                self.checkBox_sfw.setChecked(True)
            elif purity == '粗略级':
                self.checkBox_sketchy.setChecked(True)
            else:
                self.checkBox_nsfw.setChecked(True)
        for category in api.Config.IMAGE_CHOICE_CATEGORIES:
            if category == '常规':
                self.checkBox_general.setChecked(True)
            elif category == '动漫':
                self.checkBox_anime.setChecked(True)
            elif category == '人物':
                self.checkBox_people.setChecked(True)
        self.comboBox_mode.setCurrentIndex(api.Config.IMAGE_PLAY_MODE)
        self.comboBox.setCurrentIndex(int(api.Config.IMAGE_PLAY_SORT))

    def __bind(self):
        self.checkBox_general.stateChanged.connect(
            lambda checked: api.select_categories('常规') if checked else api.deselect_categories('常规')
        )
        self.checkBox_anime.stateChanged.connect(
            lambda checked: api.select_categories('动漫') if checked else api.deselect_categories('动漫')
        )
        self.checkBox_people.stateChanged.connect(
            lambda checked: api.select_categories('人物') if checked else api.deselect_categories('人物')
        )
        self.checkBox_sfw.stateChanged.connect(
            lambda checked: api.select_purity('正常级') if checked else api.deselect_purity('正常级')
        )
        self.checkBox_sketchy.stateChanged.connect(
            lambda checked: api.select_purity('粗略级') if checked else api.deselect_purity('粗略级')
        )
        self.checkBox_nsfw.stateChanged.connect(
            lambda checked: api.select_purity('限制级') if checked else api.deselect_purity('限制级')
        )
        self.comboBox.currentIndexChanged.connect(lambda index: api.set_sample(bool(index)))

    def showEvent(self, event):
        self.__initUI()
        super().showEvent(event)
