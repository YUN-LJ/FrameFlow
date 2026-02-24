# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LeftWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QSizePolicy,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_leftwidget(object):
    def setupUi(self, leftwidget):
        if not leftwidget.objectName():
            leftwidget.setObjectName(u"leftwidget")
        leftwidget.resize(400, 300)
        self.verticalLayout = QVBoxLayout(leftwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tableWidget_userDir = QTableWidget(leftwidget)
        self.tableWidget_userDir.setObjectName(u"tableWidget_userDir")

        self.horizontalLayout.addWidget(self.tableWidget_userDir)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(leftwidget)

        QMetaObject.connectSlotsByName(leftwidget)
    # setupUi

    def retranslateUi(self, leftwidget):
        leftwidget.setWindowTitle(QCoreApplication.translate("leftwidget", u"Form", None))
    # retranslateUi

