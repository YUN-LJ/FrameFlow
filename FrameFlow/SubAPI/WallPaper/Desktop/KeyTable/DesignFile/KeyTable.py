# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'KeyTable.ui'
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
from PySide6.QtWidgets import (QApplication, QHeaderView, QSizePolicy, QStackedWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from SubAPI.WallPaper.Desktop.KeyTable.KeyWordModeCtrl import KeyWordTable

class Ui_table_widget(object):
    def setupUi(self, table_widget):
        if not table_widget.objectName():
            table_widget.setObjectName(u"table_widget")
        table_widget.resize(172, 300)
        table_widget.setMinimumSize(QSize(120, 0))
        self.verticalLayout = QVBoxLayout(table_widget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(table_widget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page_custom = QWidget()
        self.page_custom.setObjectName(u"page_custom")
        self.verticalLayout_2 = QVBoxLayout(self.page_custom)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.tableWidget_userDir = QTableWidget(self.page_custom)
        self.tableWidget_userDir.setObjectName(u"tableWidget_userDir")

        self.verticalLayout_2.addWidget(self.tableWidget_userDir)

        self.stackedWidget.addWidget(self.page_custom)
        self.page_key = QWidget()
        self.page_key.setObjectName(u"page_key")
        self.verticalLayout_3 = QVBoxLayout(self.page_key)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.tableWidget_key = KeyWordTable(self.page_key)
        self.tableWidget_key.setObjectName(u"tableWidget_key")

        self.verticalLayout_3.addWidget(self.tableWidget_key)

        self.stackedWidget.addWidget(self.page_key)
        self.page_video = QWidget()
        self.page_video.setObjectName(u"page_video")
        self.verticalLayout_4 = QVBoxLayout(self.page_video)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.tableWidget_video = QTableWidget(self.page_video)
        self.tableWidget_video.setObjectName(u"tableWidget_video")

        self.verticalLayout_4.addWidget(self.tableWidget_video)

        self.stackedWidget.addWidget(self.page_video)

        self.verticalLayout.addWidget(self.stackedWidget)


        self.retranslateUi(table_widget)

        QMetaObject.connectSlotsByName(table_widget)
    # setupUi

    def retranslateUi(self, table_widget):
        table_widget.setWindowTitle(QCoreApplication.translate("table_widget", u"Form", None))
    # retranslateUi

