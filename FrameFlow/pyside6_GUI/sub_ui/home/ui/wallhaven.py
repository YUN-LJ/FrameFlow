# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'wallhaven.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QHBoxLayout, QLabel, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from qfluentwidgets.components.widgets import PrimaryPushButton
from qfluentwidgets.components.widgets.line_edit import SearchLineEdit

class Ui_wallhaven(object):
    def setupUi(self, wallhaven):
        if not wallhaven.objectName():
            wallhaven.setObjectName(u"wallhaven")
        wallhaven.resize(800, 500)
        self.verticalLayout_2 = QVBoxLayout(wallhaven)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 5, -1, -1)
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.widget_categories = QWidget(wallhaven)
        self.widget_categories.setObjectName(u"widget_categories")
        self.widget_categories.setMinimumSize(QSize(0, 0))
        self.horizontalLayout_3 = QHBoxLayout(self.widget_categories)
        self.horizontalLayout_3.setSpacing(10)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_categories = QLabel(self.widget_categories)
        self.label_categories.setObjectName(u"label_categories")

        self.horizontalLayout_3.addWidget(self.label_categories)

        self.checkBox_general = QCheckBox(self.widget_categories)
        self.checkBox_general.setObjectName(u"checkBox_general")
        self.checkBox_general.setMinimumSize(QSize(0, 40))
        self.checkBox_general.setChecked(True)

        self.horizontalLayout_3.addWidget(self.checkBox_general)

        self.checkBox_anime = QCheckBox(self.widget_categories)
        self.checkBox_anime.setObjectName(u"checkBox_anime")
        self.checkBox_anime.setMinimumSize(QSize(0, 40))
        self.checkBox_anime.setChecked(True)

        self.horizontalLayout_3.addWidget(self.checkBox_anime)

        self.checkBox_people = QCheckBox(self.widget_categories)
        self.checkBox_people.setObjectName(u"checkBox_people")
        self.checkBox_people.setMinimumSize(QSize(0, 40))
        self.checkBox_people.setChecked(True)

        self.horizontalLayout_3.addWidget(self.checkBox_people)


        self.verticalLayout_4.addWidget(self.widget_categories)

        self.widget_purity = QWidget(wallhaven)
        self.widget_purity.setObjectName(u"widget_purity")
        self.widget_purity.setMinimumSize(QSize(60, 0))
        self.horizontalLayout_4 = QHBoxLayout(self.widget_purity)
        self.horizontalLayout_4.setSpacing(10)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_purity = QLabel(self.widget_purity)
        self.label_purity.setObjectName(u"label_purity")

        self.horizontalLayout_4.addWidget(self.label_purity)

        self.checkBox_sfw = QCheckBox(self.widget_purity)
        self.checkBox_sfw.setObjectName(u"checkBox_sfw")
        self.checkBox_sfw.setMinimumSize(QSize(0, 40))
        self.checkBox_sfw.setChecked(True)

        self.horizontalLayout_4.addWidget(self.checkBox_sfw)

        self.checkBox_sketchy = QCheckBox(self.widget_purity)
        self.checkBox_sketchy.setObjectName(u"checkBox_sketchy")
        self.checkBox_sketchy.setMinimumSize(QSize(0, 40))
        self.checkBox_sketchy.setChecked(True)

        self.horizontalLayout_4.addWidget(self.checkBox_sketchy)

        self.checkBox_nsfw = QCheckBox(self.widget_purity)
        self.checkBox_nsfw.setObjectName(u"checkBox_nsfw")
        self.checkBox_nsfw.setMinimumSize(QSize(0, 40))
        self.checkBox_nsfw.setChecked(True)

        self.horizontalLayout_4.addWidget(self.checkBox_nsfw)


        self.verticalLayout_4.addWidget(self.widget_purity)


        self.horizontalLayout.addLayout(self.verticalLayout_4)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton_set = PrimaryPushButton(wallhaven)
        self.pushButton_set.setObjectName(u"pushButton_set")
        self.pushButton_set.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.pushButton_set, 2, 6, 1, 1)

        self.pushButton_add_like = PrimaryPushButton(wallhaven)
        self.pushButton_add_like.setObjectName(u"pushButton_add_like")
        self.pushButton_add_like.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.pushButton_add_like, 2, 1, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.lineEdit = SearchLineEdit(wallhaven)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_2.addWidget(self.lineEdit)

        self.pushButton_choice_all = PrimaryPushButton(wallhaven)
        self.pushButton_choice_all.setObjectName(u"pushButton_choice_all")
        self.pushButton_choice_all.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_2.addWidget(self.pushButton_choice_all)


        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.comboBox = QComboBox(wallhaven)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_8.addWidget(self.comboBox)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer)


        self.gridLayout.addLayout(self.horizontalLayout_8, 3, 0, 1, 1)

        self.pushButton_download_choice = PrimaryPushButton(wallhaven)
        self.pushButton_download_choice.setObjectName(u"pushButton_download_choice")
        self.pushButton_download_choice.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.pushButton_download_choice, 3, 1, 1, 1)

        self.pushButton_keep = PrimaryPushButton(wallhaven)
        self.pushButton_keep.setObjectName(u"pushButton_keep")
        self.pushButton_keep.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.pushButton_keep, 3, 6, 1, 1)


        self.horizontalLayout.addLayout(self.gridLayout)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")

        self.horizontalLayout_6.addLayout(self.horizontalLayout_7)


        self.horizontalLayout_5.addLayout(self.horizontalLayout_6)


        self.verticalLayout.addLayout(self.horizontalLayout_5)


        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(wallhaven)

        QMetaObject.connectSlotsByName(wallhaven)
    # setupUi

    def retranslateUi(self, wallhaven):
        wallhaven.setWindowTitle(QCoreApplication.translate("wallhaven", u"Form", None))
        self.label_categories.setText(QCoreApplication.translate("wallhaven", u"\u56fe\u50cf\u7c7b\u522b:", None))
        self.checkBox_general.setText(QCoreApplication.translate("wallhaven", u"\u5e38\u89c4", None))
        self.checkBox_anime.setText(QCoreApplication.translate("wallhaven", u"\u52a8\u6f2b", None))
        self.checkBox_people.setText(QCoreApplication.translate("wallhaven", u"\u4eba\u7269", None))
        self.label_purity.setText(QCoreApplication.translate("wallhaven", u"\u56fe\u50cf\u7b49\u7ea7:", None))
        self.checkBox_sfw.setText(QCoreApplication.translate("wallhaven", u"\u6b63\u5e38\u7ea7", None))
        self.checkBox_sketchy.setText(QCoreApplication.translate("wallhaven", u"\u7c97\u7565\u7ea7", None))
        self.checkBox_nsfw.setText(QCoreApplication.translate("wallhaven", u"\u9650\u5236\u7ea7", None))
        self.pushButton_set.setText(QCoreApplication.translate("wallhaven", u"\u8bbe\u7f6e", None))
        self.pushButton_add_like.setText(QCoreApplication.translate("wallhaven", u"\u6dfb\u52a0\u5230\u6536\u85cf\u5939", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("wallhaven", u"\u82f1\u6587\u5173\u952e\u8bcd", None))
        self.pushButton_choice_all.setText(QCoreApplication.translate("wallhaven", u"\u5168\u9009", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("wallhaven", u"\u65e5\u671f", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("wallhaven", u"\u9884\u89c8\u91cf", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("wallhaven", u"\u6536\u85cf\u91cf", None))
        self.comboBox.setItemText(3, QCoreApplication.translate("wallhaven", u"\u5173\u7cfb", None))

        self.pushButton_download_choice.setText(QCoreApplication.translate("wallhaven", u"\u4e0b\u8f7d\u6240\u9009\u9879", None))
        self.pushButton_keep.setText(QCoreApplication.translate("wallhaven", u"\u6536\u85cf\u5939", None))
    # retranslateUi

