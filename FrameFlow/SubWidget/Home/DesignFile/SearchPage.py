# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SearchPage.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QScrollArea, QSizePolicy, QSpacerItem,
    QSpinBox, QTableWidgetItem, QVBoxLayout, QWidget)

from SubWidget.Home.SlotFunc.SearchPageCtrl import Table
from qfluentwidgets.components.widgets import (CheckBox, PrimaryPushButton, SearchLineEdit, SwitchButton)

class Ui_SearchPage(object):
    def setupUi(self, SearchPage):
        if not SearchPage.objectName():
            SearchPage.setObjectName(u"SearchPage")
        SearchPage.resize(710, 459)
        self.verticalLayout_2 = QVBoxLayout(SearchPage)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(SearchPage)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 708, 457))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.checkBox_general = CheckBox(self.scrollAreaWidgetContents)
        self.checkBox_general.setObjectName(u"checkBox_general")

        self.gridLayout.addWidget(self.checkBox_general, 0, 0, 1, 1)

        self.checkBox_anime = CheckBox(self.scrollAreaWidgetContents)
        self.checkBox_anime.setObjectName(u"checkBox_anime")

        self.gridLayout.addWidget(self.checkBox_anime, 0, 1, 1, 1)

        self.checkBox_people = CheckBox(self.scrollAreaWidgetContents)
        self.checkBox_people.setObjectName(u"checkBox_people")

        self.gridLayout.addWidget(self.checkBox_people, 0, 2, 1, 1)

        self.checkBox_sfw = CheckBox(self.scrollAreaWidgetContents)
        self.checkBox_sfw.setObjectName(u"checkBox_sfw")
        self.checkBox_sfw.setStyleSheet(u"color: rgb(0, 255, 0);")

        self.gridLayout.addWidget(self.checkBox_sfw, 1, 0, 1, 1)

        self.checkBox_sketchy = CheckBox(self.scrollAreaWidgetContents)
        self.checkBox_sketchy.setObjectName(u"checkBox_sketchy")
        self.checkBox_sketchy.setStyleSheet(u"color: rgb(255, 255, 0);")

        self.gridLayout.addWidget(self.checkBox_sketchy, 1, 1, 1, 1)

        self.checkBox_nsfw = CheckBox(self.scrollAreaWidgetContents)
        self.checkBox_nsfw.setObjectName(u"checkBox_nsfw")
        self.checkBox_nsfw.setStyleSheet(u"color: rgb(170, 0, 0);")

        self.gridLayout.addWidget(self.checkBox_nsfw, 1, 2, 1, 1)


        self.horizontalLayout_2.addLayout(self.gridLayout)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.lineEdit = SearchLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setMinimumSize(QSize(0, 40))

        self.verticalLayout_4.addWidget(self.lineEdit)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButton_select_all = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_select_all.setObjectName(u"pushButton_select_all")
        self.pushButton_select_all.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_select_all)

        self.pushButton_delete = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_delete.setObjectName(u"pushButton_delete")
        self.pushButton_delete.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_delete)

        self.pushButton_download = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_download.setObjectName(u"pushButton_download")
        self.pushButton_download.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_download)


        self.verticalLayout_4.addLayout(self.horizontalLayout)


        self.horizontalLayout_2.addLayout(self.verticalLayout_4)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.checkBox_use_network = SwitchButton(self.scrollAreaWidgetContents)
        self.checkBox_use_network.setObjectName(u"checkBox_use_network")
        self.checkBox_use_network.setMinimumSize(QSize(0, 40))

        self.verticalLayout_6.addWidget(self.checkBox_use_network)

        self.checkBox_use_tags = SwitchButton(self.scrollAreaWidgetContents)
        self.checkBox_use_tags.setObjectName(u"checkBox_use_tags")
        self.checkBox_use_tags.setMinimumSize(QSize(0, 40))

        self.verticalLayout_6.addWidget(self.checkBox_use_tags)


        self.horizontalLayout_2.addLayout(self.verticalLayout_6)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.spinBox = QSpinBox(self.scrollAreaWidgetContents)
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setMinimumSize(QSize(0, 40))
        self.spinBox.setMinimum(1)

        self.verticalLayout_5.addWidget(self.spinBox)

        self.label_page_info = QLabel(self.scrollAreaWidgetContents)
        self.label_page_info.setObjectName(u"label_page_info")

        self.verticalLayout_5.addWidget(self.label_page_info)


        self.horizontalLayout_2.addLayout(self.verticalLayout_5)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.tableWidget_image = Table(self.scrollAreaWidgetContents)
        self.tableWidget_image.setObjectName(u"tableWidget_image")
        self.tableWidget_image.setMinimumSize(QSize(500, 150))

        self.verticalLayout.addWidget(self.tableWidget_image)

        self.verticalLayout.setStretch(1, 1)

        self.verticalLayout_3.addLayout(self.verticalLayout)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)


        self.retranslateUi(SearchPage)

        QMetaObject.connectSlotsByName(SearchPage)
    # setupUi

    def retranslateUi(self, SearchPage):
        SearchPage.setWindowTitle(QCoreApplication.translate("SearchPage", u"ImageTable", None))
        self.checkBox_general.setText(QCoreApplication.translate("SearchPage", u"\u5e38\u89c4", None))
        self.checkBox_anime.setText(QCoreApplication.translate("SearchPage", u"\u52a8\u6f2b", None))
        self.checkBox_people.setText(QCoreApplication.translate("SearchPage", u"\u4eba\u7269", None))
        self.checkBox_sfw.setText(QCoreApplication.translate("SearchPage", u"\u6b63\u5e38\u7ea7", None))
        self.checkBox_sketchy.setText(QCoreApplication.translate("SearchPage", u"\u7c97\u7565\u7ea7", None))
        self.checkBox_nsfw.setText(QCoreApplication.translate("SearchPage", u"\u9650\u5236\u7ea7", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("SearchPage", u"\u8f93\u5165\u82f1\u6587\u5173\u952e\u8bcd,\u53f3\u952e\u663e\u793a\u641c\u7d22\u5386\u53f2", None))
        self.pushButton_select_all.setText(QCoreApplication.translate("SearchPage", u"\u5168\u9009", None))
        self.pushButton_delete.setText(QCoreApplication.translate("SearchPage", u"\u5220\u9664", None))
        self.pushButton_download.setText(QCoreApplication.translate("SearchPage", u"\u4e0b\u8f7d", None))
        self.checkBox_use_network.setText(QCoreApplication.translate("SearchPage", u"\u8054\u7f51\u641c\u7d22", None))
        self.checkBox_use_tags.setText(QCoreApplication.translate("SearchPage", u"\u641c\u7d22\u6807\u7b7e", None))
        self.label_page_info.setText("")
    # retranslateUi

