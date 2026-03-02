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

from qfluentwidgets.components.widgets import PrimaryToolButton

class Ui_rightwidget(object):
    def setupUi(self, rightwidget):
        if not rightwidget.objectName():
            rightwidget.setObjectName(u"rightwidget")
        rightwidget.resize(572, 404)
        self.verticalLayout = QVBoxLayout(rightwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBox_name = QGroupBox(rightwidget)
        self.groupBox_name.setObjectName(u"groupBox_name")
        self.horizontalLayout_4 = QHBoxLayout(self.groupBox_name)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(5, 0, 5, 0)
        self.lineEdit_name = QLineEdit(self.groupBox_name)
        self.lineEdit_name.setObjectName(u"lineEdit_name")
        self.lineEdit_name.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_4.addWidget(self.lineEdit_name)

        self.pushButton_open = PrimaryToolButton(self.groupBox_name)
        self.pushButton_open.setObjectName(u"pushButton_open")
        self.pushButton_open.setMinimumSize(QSize(30, 30))
        self.pushButton_open.setMaximumSize(QSize(30, 30))

        self.horizontalLayout_4.addWidget(self.pushButton_open)

        self.pushButton_full = PrimaryToolButton(self.groupBox_name)
        self.pushButton_full.setObjectName(u"pushButton_full")
        self.pushButton_full.setMinimumSize(QSize(30, 30))
        self.pushButton_full.setMaximumSize(QSize(30, 30))

        self.horizontalLayout_4.addWidget(self.pushButton_full)


        self.verticalLayout.addWidget(self.groupBox_name)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(-1, -1, 0, -1)
        self.groupBox_info = QGroupBox(rightwidget)
        self.groupBox_info.setObjectName(u"groupBox_info")
        self.horizontalLayout_5 = QHBoxLayout(self.groupBox_info)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(5, 5, 5, 5)
        self.scrollArea = QScrollArea(self.groupBox_info)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 221, 316))
        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout_5.addWidget(self.scrollArea)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")

        self.horizontalLayout_5.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_5.setStretch(0, 2)
        self.horizontalLayout_5.setStretch(1, 3)

        self.horizontalLayout_3.addWidget(self.groupBox_info)


        self.verticalLayout.addLayout(self.horizontalLayout_3)


        self.retranslateUi(rightwidget)

        QMetaObject.connectSlotsByName(rightwidget)
    # setupUi

    def retranslateUi(self, rightwidget):
        rightwidget.setWindowTitle(QCoreApplication.translate("rightwidget", u"Form", None))
        self.groupBox_name.setTitle(QCoreApplication.translate("rightwidget", u"\u6b63\u5728\u64ad\u653e:", None))
        self.pushButton_open.setText("")
        self.pushButton_full.setText("")
        self.groupBox_info.setTitle(QCoreApplication.translate("rightwidget", u"\u56fe\u50cf\u4fe1\u606f:", None))
    # retranslateUi

