# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'BaseSet.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtWidgets import (QVBoxLayout)

from qfluentwidgets import HeaderCardWidget


class Ui_base_set_win(object):
    def setupUi(self, base_set_win):
        if not base_set_win.objectName():
            base_set_win.setObjectName(u"base_set_win")
        base_set_win.resize(400, 300)
        self.verticalLayout_2 = QVBoxLayout(base_set_win)
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_set_other = QVBoxLayout()
        self.verticalLayout_set_other.setObjectName(u"verticalLayout_set_other")

        self.verticalLayout_2.addLayout(self.verticalLayout_set_other)

        self.groupBox = HeaderCardWidget(base_set_win)
        self.groupBox.setObjectName(u"groupBox")

        self.verticalLayout_2.addWidget(self.groupBox)

        self.verticalLayout_2.setStretch(1, 1)

        Ui_base_set_win.retranslateUi(self, base_set_win)

        QMetaObject.connectSlotsByName(base_set_win)

    # setupUi

    def retranslateUi(self, base_set_win):
        base_set_win.setWindowTitle(QCoreApplication.translate("base_set_win", u"\u8bbe\u7f6e\u6a21\u5757", None))
        self.groupBox.setTitle(QCoreApplication.translate("base_set_win", u"\u547d\u4ee4\u884c", None))
    # retranslateUi
