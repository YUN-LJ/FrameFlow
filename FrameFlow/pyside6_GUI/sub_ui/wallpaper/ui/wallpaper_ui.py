# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'wallpaper_ui.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect,
                            QSize, Qt)
from PySide6.QtWidgets import (QHBoxLayout, QScrollArea, QSizePolicy,
                               QSpacerItem, QVBoxLayout, QWidget)

from qfluentwidgets.components.widgets import PrimaryPushButton


class Ui_wallpaper(object):
    def setupUi(self, wallpaper):
        if not wallpaper.objectName():
            wallpaper.setObjectName(u"wallpaper")
        wallpaper.resize(800, 500)
        self.verticalLayout = QVBoxLayout(wallpaper)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, -1, -1, 0)
        self.scrollArea_options = QScrollArea(wallpaper)
        self.scrollArea_options.setObjectName(u"scrollArea_options")
        self.scrollArea_options.setMinimumSize(QSize(0, 0))
        self.scrollArea_options.setMaximumSize(QSize(16777215, 60))
        self.scrollArea_options.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea_options.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 796, 58))
        self.horizontalLayout_3 = QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.pushButton_start = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_start.setObjectName(u"pushButton_start")
        self.pushButton_start.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_3.addWidget(self.pushButton_start)

        self.pushButton_add = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_add.setObjectName(u"pushButton_add")
        self.pushButton_add.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_3.addWidget(self.pushButton_add)

        self.pushButton_del = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_del.setObjectName(u"pushButton_del")
        self.pushButton_del.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_3.addWidget(self.pushButton_del)

        self.pushButton_set = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_set.setObjectName(u"pushButton_set")
        self.pushButton_set.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_3.addWidget(self.pushButton_set)

        self.pushButton_open_image = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_open_image.setObjectName(u"pushButton_open_image")
        self.pushButton_open_image.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_3.addWidget(self.pushButton_open_image)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.scrollArea_options.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea_options)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.verticalLayout.addLayout(self.verticalLayout_2)


        self.retranslateUi(wallpaper)

        QMetaObject.connectSlotsByName(wallpaper)
    # setupUi

    def retranslateUi(self, wallpaper):
        wallpaper.setWindowTitle(QCoreApplication.translate("wallpaper", u"wallpaper", None))
        self.pushButton_start.setText(QCoreApplication.translate("wallpaper", u"\u5f00\u59cb", None))
        self.pushButton_add.setText(QCoreApplication.translate("wallpaper", u"\u65b0\u589e\u76ee\u5f55", None))
        self.pushButton_del.setText(QCoreApplication.translate("wallpaper", u"\u5220\u9664\u76ee\u5f55", None))
        self.pushButton_set.setText(QCoreApplication.translate("wallpaper", u"\u8bbe\u7f6e", None))
        self.pushButton_open_image.setText(QCoreApplication.translate("wallpaper", u"\u6253\u5f00\u5f53\u524d\u56fe\u50cf", None))
    # retranslateUi

