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
    QLabel, QLineEdit, QScrollArea, QSizePolicy,
    QVBoxLayout, QWidget)

from qfluentwidgets.components.widgets import PrimaryPushButton

class Ui_rightwidget(object):
    def setupUi(self, rightwidget):
        if not rightwidget.objectName():
            rightwidget.setObjectName(u"rightwidget")
        rightwidget.resize(572, 404)
        self.verticalLayout = QVBoxLayout(rightwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_name = QLabel(rightwidget)
        self.label_name.setObjectName(u"label_name")
        self.label_name.setStyleSheet(u"font: 10pt \"Microsoft YaHei UI\";")

        self.horizontalLayout.addWidget(self.label_name)

        self.lineEdit_name = QLineEdit(rightwidget)
        self.lineEdit_name.setObjectName(u"lineEdit_name")
        self.lineEdit_name.setMinimumSize(QSize(0, 40))
        self.lineEdit_name.setReadOnly(False)

        self.horizontalLayout.addWidget(self.lineEdit_name)

        self.pushButton_open = PrimaryPushButton(rightwidget)
        self.pushButton_open.setObjectName(u"pushButton_open")
        self.pushButton_open.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_open)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.groupBox_info = QGroupBox(rightwidget)
        self.groupBox_info.setObjectName(u"groupBox_info")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_info)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(self.groupBox_info)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 568, 54))
        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)


        self.verticalLayout.addWidget(self.groupBox_info)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(rightwidget)

        QMetaObject.connectSlotsByName(rightwidget)
    # setupUi

    def retranslateUi(self, rightwidget):
        rightwidget.setWindowTitle(QCoreApplication.translate("rightwidget", u"Form", None))
        self.label_name.setText(QCoreApplication.translate("rightwidget", u"\u5f53\u524d\u6b63\u5728\u64ad\u653e:", None))
        self.pushButton_open.setText(QCoreApplication.translate("rightwidget", u"\u5728\u8d44\u6e90\u7ba1\u7406\u4e2d\u6253\u5f00", None))
        self.groupBox_info.setTitle(QCoreApplication.translate("rightwidget", u"\u56fe\u50cf\u4fe1\u606f:", None))
    # retranslateUi

