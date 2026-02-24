# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'RightWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QGroupBox, QHBoxLayout,
    QLineEdit, QScrollArea, QSizePolicy, QVBoxLayout,
    QWidget)

from qfluentwidgets.components.widgets import PrimaryPushButton

class Ui_rightwidget(object):
    def setupUi(self, rightwidget):
        if not rightwidget.objectName():
            rightwidget.setObjectName(u"rightwidget")
        rightwidget.resize(572, 404)
        self.verticalLayout = QVBoxLayout(rightwidget)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBox_name = QGroupBox(rightwidget)
        self.groupBox_name.setObjectName(u"groupBox_name")
        self.horizontalLayout_4 = QHBoxLayout(self.groupBox_name)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.lineEdit_name = QLineEdit(self.groupBox_name)
        self.lineEdit_name.setObjectName(u"lineEdit_name")
        self.lineEdit_name.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_4.addWidget(self.lineEdit_name)


        self.horizontalLayout.addWidget(self.groupBox_name)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(10)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(-1, -1, 0, -1)
        self.groupBox_info = QGroupBox(rightwidget)
        self.groupBox_info.setObjectName(u"groupBox_info")
        self.groupBox_info.setMaximumSize(QSize(16777215, 100))
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_info)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(self.groupBox_info)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 475, 81))
        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)


        self.horizontalLayout_3.addWidget(self.groupBox_info)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.pushButton_full = PrimaryPushButton(rightwidget)
        self.pushButton_full.setObjectName(u"pushButton_full")
        self.pushButton_full.setMinimumSize(QSize(0, 40))

        self.verticalLayout_3.addWidget(self.pushButton_full)

        self.pushButton_open = PrimaryPushButton(rightwidget)
        self.pushButton_open.setObjectName(u"pushButton_open")
        self.pushButton_open.setMinimumSize(QSize(0, 40))

        self.verticalLayout_3.addWidget(self.pushButton_open)


        self.horizontalLayout_3.addLayout(self.verticalLayout_3)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(rightwidget)

        QMetaObject.connectSlotsByName(rightwidget)
    # setupUi

    def retranslateUi(self, rightwidget):
        rightwidget.setWindowTitle(QCoreApplication.translate("rightwidget", u"Form", None))
        self.groupBox_name.setTitle(QCoreApplication.translate("rightwidget", u"\u6b63\u5728\u64ad\u653e:", None))
        self.groupBox_info.setTitle(QCoreApplication.translate("rightwidget", u"\u56fe\u50cf\u4fe1\u606f:", None))
        self.pushButton_full.setText(QCoreApplication.translate("rightwidget", u"\u5168\u5c4f\u67e5\u770b", None))
        self.pushButton_open.setText(QCoreApplication.translate("rightwidget", u"\u672c\u5730\u67e5\u770b", None))
    # retranslateUi

