# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DownloadPage.ui'
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
    QSpacerItem, QTableWidgetItem, QVBoxLayout, QWidget)

from SubWidget.Home.SlotFunc.DownloadPageCtrl import Table
from qfluentwidgets.components.widgets import (BodyLabel, PrimaryPushButton, SmoothScrollArea, TransparentPushButton)

class Ui_DownloadWidget(object):
    def setupUi(self, DownloadWidget):
        if not DownloadWidget.objectName():
            DownloadWidget.setObjectName(u"DownloadWidget")
        DownloadWidget.resize(557, 339)
        self.verticalLayout = QVBoxLayout(DownloadWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = SmoothScrollArea(DownloadWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 555, 337))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(5)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_save_path = BodyLabel(self.scrollAreaWidgetContents)
        self.label_save_path.setObjectName(u"label_save_path")
        self.label_save_path.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.horizontalLayout.addWidget(self.label_save_path)

        self.label_save_path_value = TransparentPushButton(self.scrollAreaWidgetContents)
        self.label_save_path_value.setObjectName(u"label_save_path_value")
        self.label_save_path_value.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.label_save_path_value)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButton_set_save_path = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_set_save_path.setObjectName(u"pushButton_set_save_path")
        self.pushButton_set_save_path.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_set_save_path)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.pushButton_select_all = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_select_all.setObjectName(u"pushButton_select_all")
        self.pushButton_select_all.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_2.addWidget(self.pushButton_select_all)

        self.pushButton_start = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_start.setObjectName(u"pushButton_start")
        self.pushButton_start.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_2.addWidget(self.pushButton_start)

        self.pushButton_delete = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_delete.setObjectName(u"pushButton_delete")
        self.pushButton_delete.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_2.addWidget(self.pushButton_delete)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.tableWidget_download = Table(self.scrollAreaWidgetContents)
        self.tableWidget_download.setObjectName(u"tableWidget_download")

        self.verticalLayout_2.addWidget(self.tableWidget_download)


        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(DownloadWidget)

        QMetaObject.connectSlotsByName(DownloadWidget)
    # setupUi

    def retranslateUi(self, DownloadWidget):
        DownloadWidget.setWindowTitle(QCoreApplication.translate("DownloadWidget", u"RigetWidget", None))
        self.label_save_path.setText(QCoreApplication.translate("DownloadWidget", u"\u5f53\u524d\u4fdd\u5b58\u8def\u5f84:", None))
        self.label_save_path_value.setText("")
        self.pushButton_set_save_path.setText(QCoreApplication.translate("DownloadWidget", u"\u8bbe\u7f6e\u4fdd\u5b58\u8def\u5f84", None))
        self.pushButton_select_all.setText(QCoreApplication.translate("DownloadWidget", u"\u5168\u9009", None))
        self.pushButton_start.setText(QCoreApplication.translate("DownloadWidget", u"\u5f00\u59cb", None))
        self.pushButton_delete.setText(QCoreApplication.translate("DownloadWidget", u"\u5220\u9664", None))
    # retranslateUi

