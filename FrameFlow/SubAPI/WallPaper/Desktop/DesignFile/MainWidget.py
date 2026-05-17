# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

from Fun.QtWidget import SidebarWidget
from qfluentwidgets import CardWidget
from qfluentwidgets.components.widgets import (BodyLabel, CheckBox, ComboBox, PrimaryPushButton,
    PrimaryToolButton, SearchLineEdit, SpinBox, SubtitleLabel,
    SwitchButton)

class Ui_wallpaper(object):
    def setupUi(self, wallpaper):
        if not wallpaper.objectName():
            wallpaper.setObjectName(u"wallpaper")
        wallpaper.resize(798, 529)
        self.verticalLayout = QVBoxLayout(wallpaper)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget_sets = SidebarWidget(wallpaper)
        self.widget_sets.setObjectName(u"widget_sets")
        self.widget_sets.setMinimumSize(QSize(0, 100))
        self.verticalLayout_2 = QVBoxLayout(self.widget_sets)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_purity = SubtitleLabel(self.widget_sets)
        self.label_purity.setObjectName(u"label_purity")
        self.label_purity.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_purity, 0, 1, 1, 1)

        self.label_categories = SubtitleLabel(self.widget_sets)
        self.label_categories.setObjectName(u"label_categories")
        self.label_categories.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_categories, 1, 1, 1, 1)

        self.checkBox_people = CheckBox(self.widget_sets)
        self.checkBox_people.setObjectName(u"checkBox_people")

        self.gridLayout.addWidget(self.checkBox_people, 0, 4, 1, 1)

        self.checkBox_sketchy = CheckBox(self.widget_sets)
        self.checkBox_sketchy.setObjectName(u"checkBox_sketchy")

        self.gridLayout.addWidget(self.checkBox_sketchy, 1, 3, 1, 1)

        self.checkBox_sfw = CheckBox(self.widget_sets)
        self.checkBox_sfw.setObjectName(u"checkBox_sfw")

        self.gridLayout.addWidget(self.checkBox_sfw, 1, 2, 1, 1)

        self.checkBox_general = CheckBox(self.widget_sets)
        self.checkBox_general.setObjectName(u"checkBox_general")

        self.gridLayout.addWidget(self.checkBox_general, 0, 2, 1, 1)

        self.checkBox_anime = CheckBox(self.widget_sets)
        self.checkBox_anime.setObjectName(u"checkBox_anime")

        self.gridLayout.addWidget(self.checkBox_anime, 0, 3, 1, 1)

        self.checkBox_nsfw = CheckBox(self.widget_sets)
        self.checkBox_nsfw.setObjectName(u"checkBox_nsfw")

        self.gridLayout.addWidget(self.checkBox_nsfw, 1, 4, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 0, 5, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_3)

        self.label_mode = SubtitleLabel(self.widget_sets)
        self.label_mode.setObjectName(u"label_mode")
        self.label_mode.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.horizontalLayout_6.addWidget(self.label_mode)

        self.comboBox_mode = ComboBox(self.widget_sets)
        self.comboBox_mode.addItem("")
        self.comboBox_mode.addItem("")
        self.comboBox_mode.addItem("")
        self.comboBox_mode.setObjectName(u"comboBox_mode")
        self.comboBox_mode.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_6.addWidget(self.comboBox_mode)

        self.label_order = SubtitleLabel(self.widget_sets)
        self.label_order.setObjectName(u"label_order")
        self.label_order.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.horizontalLayout_6.addWidget(self.label_order)

        self.comboBox = ComboBox(self.widget_sets)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_6.addWidget(self.comboBox)

        self.checkBox_use_tag = SwitchButton(self.widget_sets)
        self.checkBox_use_tag.setObjectName(u"checkBox_use_tag")

        self.horizontalLayout_6.addWidget(self.checkBox_use_tag)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_4)


        self.verticalLayout_2.addLayout(self.horizontalLayout_6)


        self.verticalLayout.addWidget(self.widget_sets)

        self.widget_options = CardWidget(wallpaper)
        self.widget_options.setObjectName(u"widget_options")
        self.horizontalLayout = QHBoxLayout(self.widget_options)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton_play = PrimaryToolButton(self.widget_options)
        self.pushButton_play.setObjectName(u"pushButton_play")
        self.pushButton_play.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_play)

        self.pushButton_set = PrimaryToolButton(self.widget_options)
        self.pushButton_set.setObjectName(u"pushButton_set")
        self.pushButton_set.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_set)

        self.label_progress = BodyLabel(self.widget_options)
        self.label_progress.setObjectName(u"label_progress")

        self.horizontalLayout.addWidget(self.label_progress)

        self.lineEdit_search = SearchLineEdit(self.widget_options)
        self.lineEdit_search.setObjectName(u"lineEdit_search")
        self.lineEdit_search.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.lineEdit_search)

        self.pushButton_select = PrimaryPushButton(self.widget_options)
        self.pushButton_select.setObjectName(u"pushButton_select")
        self.pushButton_select.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_select)

        self.pushButton_cancel_select = PrimaryPushButton(self.widget_options)
        self.pushButton_cancel_select.setObjectName(u"pushButton_cancel_select")
        self.pushButton_cancel_select.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_cancel_select)

        self.label_3 = BodyLabel(self.widget_options)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.horizontalLayout.addWidget(self.label_3)

        self.spinBox_time = SpinBox(self.widget_options)
        self.spinBox_time.setObjectName(u"spinBox_time")
        self.spinBox_time.setMinimumSize(QSize(0, 40))
        self.spinBox_time.setMinimum(1)
        self.spinBox_time.setMaximum(600)

        self.horizontalLayout.addWidget(self.spinBox_time)


        self.verticalLayout.addWidget(self.widget_options)

        self.widget_splitter = CardWidget(wallpaper)
        self.widget_splitter.setObjectName(u"widget_splitter")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_splitter)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")

        self.verticalLayout.addWidget(self.widget_splitter)

        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(wallpaper)

        QMetaObject.connectSlotsByName(wallpaper)
    # setupUi

    def retranslateUi(self, wallpaper):
        wallpaper.setWindowTitle(QCoreApplication.translate("wallpaper", u"wallpaper", None))
        self.label_purity.setText(QCoreApplication.translate("wallpaper", u"\u7c7b\u522b\u9009\u62e9", None))
        self.label_categories.setText(QCoreApplication.translate("wallpaper", u"\u5206\u7ea7\u9009\u62e9", None))
        self.checkBox_people.setText(QCoreApplication.translate("wallpaper", u"\u4eba\u7269", None))
        self.checkBox_sketchy.setText(QCoreApplication.translate("wallpaper", u"\u7c97\u7565\u7ea7", None))
        self.checkBox_sfw.setText(QCoreApplication.translate("wallpaper", u"\u6b63\u5e38\u7ea7", None))
        self.checkBox_general.setText(QCoreApplication.translate("wallpaper", u"\u5e38\u89c4", None))
        self.checkBox_anime.setText(QCoreApplication.translate("wallpaper", u"\u52a8\u6f2b", None))
        self.checkBox_nsfw.setText(QCoreApplication.translate("wallpaper", u"\u9650\u5236\u7ea7", None))
        self.label_mode.setText(QCoreApplication.translate("wallpaper", u"\u64ad\u653e\u6a21\u5f0f", None))
        self.comboBox_mode.setItemText(0, QCoreApplication.translate("wallpaper", u"\u7528\u6237\u6a21\u5f0f", None))
        self.comboBox_mode.setItemText(1, QCoreApplication.translate("wallpaper", u"\u6536\u85cf\u5939\u6a21\u5f0f", None))
        self.comboBox_mode.setItemText(2, QCoreApplication.translate("wallpaper", u"\u89c6\u9891\u6a21\u5f0f", None))

        self.label_order.setText(QCoreApplication.translate("wallpaper", u"\u64ad\u653e\u987a\u5e8f", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("wallpaper", u"\u65e5\u671f", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("wallpaper", u"\u968f\u673a", None))

        self.checkBox_use_tag.setText(QCoreApplication.translate("wallpaper", u"\u4f7f\u7528\u5173\u952e\u8bcd", None))
        self.pushButton_play.setText("")
        self.pushButton_set.setText("")
        self.label_progress.setText("")
        self.lineEdit_search.setPlaceholderText(QCoreApplication.translate("wallpaper", u"\u8f93\u5165\u5173\u952e\u8bcd\u6216\u9996\u5b57\u6bcd\u53ef\u8fdb\u884c\u5b9a\u4f4d/\u9009\u62e9\u6761\u4ef6", None))
        self.pushButton_select.setText(QCoreApplication.translate("wallpaper", u"\u9009\u62e9", None))
        self.pushButton_cancel_select.setText(QCoreApplication.translate("wallpaper", u"\u53d6\u6d88", None))
        self.label_3.setText(QCoreApplication.translate("wallpaper", u"\u64ad\u653e\u95f4\u9694:", None))
    # retranslateUi

