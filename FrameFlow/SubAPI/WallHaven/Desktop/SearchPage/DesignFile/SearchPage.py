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
    QLabel, QSizePolicy, QSpacerItem, QTableWidgetItem,
    QVBoxLayout, QWidget)

from Fun.QtWidget import SidebarWidget
from SubAPI.WallHaven.Desktop.SearchPage.SearchTable import SearchTable
from qfluentwidgets import (CardWidget, SpinBox)
from qfluentwidgets.components.widgets import (CheckBox, PrimaryToolButton, SearchLineEdit, SmoothScrollArea,
    SwitchButton)

class Ui_SearchPage(object):
    def setupUi(self, SearchPage):
        if not SearchPage.objectName():
            SearchPage.setObjectName(u"SearchPage")
        SearchPage.resize(719, 459)
        self.verticalLayout_2 = QVBoxLayout(SearchPage)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = SmoothScrollArea(SearchPage)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 717, 457))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget_search_params = SidebarWidget(self.scrollAreaWidgetContents)
        self.widget_search_params.setObjectName(u"widget_search_params")
        self.widget_search_params.setMinimumSize(QSize(0, 0))
        self.horizontalLayout_3 = QHBoxLayout(self.widget_search_params)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setVerticalSpacing(15)
        self.gridLayout.setContentsMargins(-1, 15, -1, -1)
        self.checkBox_general = CheckBox(self.widget_search_params)
        self.checkBox_general.setObjectName(u"checkBox_general")
        self.checkBox_general.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.checkBox_general, 0, 0, 1, 1)

        self.checkBox_sketchy = CheckBox(self.widget_search_params)
        self.checkBox_sketchy.setObjectName(u"checkBox_sketchy")
        self.checkBox_sketchy.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.checkBox_sketchy, 1, 1, 1, 1)

        self.checkBox_anime = CheckBox(self.widget_search_params)
        self.checkBox_anime.setObjectName(u"checkBox_anime")
        self.checkBox_anime.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.checkBox_anime, 0, 1, 1, 1)

        self.checkBox_sfw = CheckBox(self.widget_search_params)
        self.checkBox_sfw.setObjectName(u"checkBox_sfw")
        self.checkBox_sfw.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.checkBox_sfw, 1, 0, 1, 1)

        self.checkBox_nsfw = CheckBox(self.widget_search_params)
        self.checkBox_nsfw.setObjectName(u"checkBox_nsfw")
        self.checkBox_nsfw.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.checkBox_nsfw, 1, 2, 1, 1)

        self.checkBox_people = CheckBox(self.widget_search_params)
        self.checkBox_people.setObjectName(u"checkBox_people")
        self.checkBox_people.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.checkBox_people, 0, 2, 1, 1)


        self.horizontalLayout_3.addLayout(self.gridLayout)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.checkBox_use_network = SwitchButton(self.widget_search_params)
        self.checkBox_use_network.setObjectName(u"checkBox_use_network")
        self.checkBox_use_network.setMinimumSize(QSize(0, 40))

        self.verticalLayout_5.addWidget(self.checkBox_use_network)

        self.checkBox_use_tags = SwitchButton(self.widget_search_params)
        self.checkBox_use_tags.setObjectName(u"checkBox_use_tags")
        self.checkBox_use_tags.setMinimumSize(QSize(0, 40))

        self.verticalLayout_5.addWidget(self.checkBox_use_tags)


        self.horizontalLayout_3.addLayout(self.verticalLayout_5)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addWidget(self.widget_search_params)

        self.widget_title = CardWidget(self.scrollAreaWidgetContents)
        self.widget_title.setObjectName(u"widget_title")
        self.widget_title.setMinimumSize(QSize(0, 0))
        self.verticalLayout_4 = QVBoxLayout(self.widget_title)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton_expand = PrimaryToolButton(self.widget_title)
        self.pushButton_expand.setObjectName(u"pushButton_expand")
        self.pushButton_expand.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_expand)

        self.lineEdit = SearchLineEdit(self.widget_title)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.lineEdit)

        self.spinBox = SpinBox(self.widget_title)
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setMinimumSize(QSize(0, 40))
        self.spinBox.setMinimum(1)

        self.horizontalLayout.addWidget(self.spinBox)

        self.label_page_info = QLabel(self.widget_title)
        self.label_page_info.setObjectName(u"label_page_info")

        self.horizontalLayout.addWidget(self.label_page_info)


        self.verticalLayout_4.addLayout(self.horizontalLayout)


        self.verticalLayout.addWidget(self.widget_title)

        self.widget_content = QWidget(self.scrollAreaWidgetContents)
        self.widget_content.setObjectName(u"widget_content")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_content)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.tableWidget_image = SearchTable(self.widget_content)
        self.tableWidget_image.setObjectName(u"tableWidget_image")
        self.tableWidget_image.setMinimumSize(QSize(200, 200))

        self.horizontalLayout_2.addWidget(self.tableWidget_image)


        self.verticalLayout.addWidget(self.widget_content)

        self.verticalLayout.setStretch(2, 1)

        self.verticalLayout_3.addLayout(self.verticalLayout)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)


        self.retranslateUi(SearchPage)

        QMetaObject.connectSlotsByName(SearchPage)
    # setupUi

    def retranslateUi(self, SearchPage):
        SearchPage.setWindowTitle(QCoreApplication.translate("SearchPage", u"\u641c\u7d22\u6a21\u5757", None))
        self.checkBox_general.setText(QCoreApplication.translate("SearchPage", u"\u5e38\u89c4", None))
        self.checkBox_sketchy.setText(QCoreApplication.translate("SearchPage", u"\u7c97\u7565\u7ea7", None))
        self.checkBox_anime.setText(QCoreApplication.translate("SearchPage", u"\u52a8\u6f2b", None))
        self.checkBox_sfw.setText(QCoreApplication.translate("SearchPage", u"\u6b63\u5e38\u7ea7", None))
        self.checkBox_nsfw.setText(QCoreApplication.translate("SearchPage", u"\u9650\u5236\u7ea7", None))
        self.checkBox_people.setText(QCoreApplication.translate("SearchPage", u"\u4eba\u7269", None))
        self.checkBox_use_network.setText(QCoreApplication.translate("SearchPage", u"\u8054\u7f51\u641c\u7d22", None))
        self.checkBox_use_tags.setText(QCoreApplication.translate("SearchPage", u"\u641c\u7d22\u6807\u7b7e", None))
        self.pushButton_expand.setText("")
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("SearchPage", u"\u8f93\u5165\u82f1\u6587\u5173\u952e\u8bcd,\u53f3\u952e\u663e\u793a\u641c\u7d22\u5386\u53f2", None))
        self.label_page_info.setText("")
    # retranslateUi

