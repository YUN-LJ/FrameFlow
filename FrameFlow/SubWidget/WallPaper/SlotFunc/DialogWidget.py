"""弹窗类"""
from SubWidget.ImportPack import *
from ImportFile import Config
from SubWidget.WallPaper.DesignFile.SetDialog import Ui_Sets
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from SubWidget.WallPaper import WallPaperWin


class SetDialog(Ui_Sets, MessageBoxBase):
    def __init__(self, parent: Optional['WallPaperWin']):
        self.parent = parent
        super().__init__(Config.TOP_WINDOWS)
        self.slot = SetDialogSlot(self)
        self.__uiInit()
        self.__bind()

    def __uiInit(self):
        """界面初始化"""
        widget = SimpleCardWidget(self)
        # 所有子控件继承样式
        widget.setStyleSheet("""SetDialog, SetDialog * {background-color: transparent;}""")

        self.hideCancelButton()
        self.setupUi(widget)
        self.viewLayout.addWidget(widget)

        self.checkBox_use_tag.setOnText('使用标签')
        self.checkBox_use_tag.setOffText('使用关键词')
        self.checkBox_use_tag.hide()
        # 设置类别和分级复选框状态
        self.checkBox_general.setChecked('常规' in WP.Config.IMAGE_CHOICE_CATEGORIES)
        self.checkBox_anime.setChecked('动漫' in WP.Config.IMAGE_CHOICE_CATEGORIES)
        self.checkBox_people.setChecked('人物' in WP.Config.IMAGE_CHOICE_CATEGORIES)
        self.checkBox_sfw.setChecked('正常级' in WP.Config.IMAGE_CHOICE_PURITY)
        self.checkBox_sketchy.setChecked('粗略级' in WP.Config.IMAGE_CHOICE_PURITY)
        self.checkBox_nsfw.setChecked('限制级' in WP.Config.IMAGE_CHOICE_PURITY)
        self.comboBox_mode.setCurrentIndex(WP.Config.IMAGE_PLAY_MODE)
        self.comboBox.setCurrentIndex(WP.Config.IMAGE_PLAY_SORT)

        self.resizeSize()
        self.checkBox_sfw.setTextColor(QColor(0, 255, 0), QColor(0, 255, 0))
        self.checkBox_sketchy.setTextColor(QColor(255, 255, 0), QColor(255, 255, 0))
        self.checkBox_nsfw.setTextColor(QColor(170, 0, 0), QColor(170, 0, 0))

    def __bind(self):
        """按钮绑定"""
        self.checkBox_use_tag.checkedChanged.connect(self.slot.checkBox_use_tag)
        self.checkBox_general.checkStateChanged.connect(self.slot.checkBox_general)
        self.checkBox_anime.checkStateChanged.connect(self.slot.checkBox_anime)
        self.checkBox_people.checkStateChanged.connect(self.slot.checkBox_people)
        self.checkBox_sfw.checkStateChanged.connect(self.slot.checkBox_sfw)
        self.checkBox_sketchy.checkStateChanged.connect(self.slot.checkBox_sketchy)
        self.checkBox_nsfw.checkStateChanged.connect(self.slot.checkBox_nsfw)
        self.comboBox_mode.currentIndexChanged.connect(self.slot.comboBox_mode)
        self.comboBox.currentIndexChanged.connect(self.slot.comboBox)
        AppCore().getSignal('resize').connect(self.resizeSize)

    def resizeSize(self):
        """与主窗口保持缩放"""
        self.widget.setMinimumWidth(Config.TOP_WINDOWS.width() * 0.5)
        self.widget.setMinimumHeight(Config.TOP_WINDOWS.height() * 0.5)


class SetDialogSlot:
    def __init__(self, parent: SetDialog):
        self.parent = parent
        self.wallpaper_api = WPAPI()

    def comboBox_mode(self, index):
        if index == WP.Config.IMAGE_KEY_MODE:
            self.parent.checkBox_use_tag.show()
        else:
            self.parent.checkBox_use_tag.hide()
        self.parent.parent.left_widget.stackedWidget.setCurrentIndex(index)
        self.wallpaper_api.set_image_play_mode(index)

    def checkBox_use_tag(self, checked):
        if checked:
            for cell in self.parent.parent.left_widget.tableWidget_key.all_cells.values():
                cell.checkBox.setEnabled(False)
            self.wallpaper_api.image_key_mode.enable_tags_mode(True)
        else:
            for cell in self.parent.parent.left_widget.tableWidget_key.all_cells.values():
                cell.checkBox.setEnabled(True)
            self.wallpaper_api.image_key_mode.enable_tags_mode(False)

    def checkBox_general(self, checked):
        if checked == Qt.CheckState.Checked:
            self.wallpaper_api.select_categories('常规')
        else:
            self.wallpaper_api.deselect_categories('常规')

    def checkBox_anime(self, checked):
        if checked == Qt.CheckState.Checked:
            self.wallpaper_api.select_categories('动漫')
        else:
            self.wallpaper_api.deselect_categories('动漫')

    def checkBox_people(self, checked):
        if checked == Qt.CheckState.Checked:
            self.wallpaper_api.select_categories('人物')
        else:
            self.wallpaper_api.deselect_categories('人物')

    def checkBox_sfw(self, checked):
        if checked == Qt.CheckState.Checked:
            self.wallpaper_api.select_purity('正常级')
        else:
            self.wallpaper_api.deselect_purity('正常级')

    def checkBox_sketchy(self, checked):
        if checked == Qt.CheckState.Checked:
            self.wallpaper_api.select_purity('粗略级')
        else:
            self.wallpaper_api.deselect_purity('粗略级')

    def checkBox_nsfw(self, checked):
        if checked == Qt.CheckState.Checked:
            self.wallpaper_api.select_purity('限制级')
        else:
            self.wallpaper_api.deselect_purity('限制级')

    def comboBox(self, index):
        self.wallpaper_api.set_sample(bool(index))
