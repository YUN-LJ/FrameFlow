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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QLabel,
    QScrollArea, QSizePolicy, QSpacerItem, QSpinBox,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from qfluentwidgets.components.widgets import PrimaryPushButton

class Ui_ImageTable(object):
    def setupUi(self, ImageTable):
        if not ImageTable.objectName():
            ImageTable.setObjectName(u"ImageTable")
        ImageTable.resize(507, 220)
        self.verticalLayout_2 = QVBoxLayout(ImageTable)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(ImageTable)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 505, 218))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, 5, -1, 5)
        self.tableWidget_image = QTableWidget(self.scrollAreaWidgetContents)
        self.tableWidget_image.setObjectName(u"tableWidget_image")
        self.tableWidget_image.setMinimumSize(QSize(500, 150))

        self.verticalLayout.addWidget(self.tableWidget_image)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, -1, 5, -1)
        self.label_state = QLabel(self.scrollAreaWidgetContents)
        self.label_state.setObjectName(u"label_state")
        self.label_state.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.label_state)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.label_total = QLabel(self.scrollAreaWidgetContents)
        self.label_total.setObjectName(u"label_total")

        self.horizontalLayout.addWidget(self.label_total)

        self.pushButton_previous_page = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_previous_page.setObjectName(u"pushButton_previous_page")
        self.pushButton_previous_page.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_previous_page)

        self.spinBox = QSpinBox(self.scrollAreaWidgetContents)
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setMinimumSize(QSize(0, 40))
        self.spinBox.setMinimum(1)

        self.horizontalLayout.addWidget(self.spinBox)

        self.pushButton_next_page = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_next_page.setObjectName(u"pushButton_next_page")
        self.pushButton_next_page.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_next_page)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.verticalLayout_3.addLayout(self.verticalLayout)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)


        self.retranslateUi(ImageTable)

        QMetaObject.connectSlotsByName(ImageTable)
    # setupUi

    def retranslateUi(self, ImageTable):
        ImageTable.setWindowTitle(QCoreApplication.translate("ImageTable", u"ImageTable", None))
        self.label_state.setText(QCoreApplication.translate("ImageTable", u"\u5f53\u524d\u72b6\u6001:", None))
        self.label_total.setText(QCoreApplication.translate("ImageTable", u"\u5171xxx\u9875,\u603b\u8ba1xxx\u5f20", None))
        self.pushButton_previous_page.setText(QCoreApplication.translate("ImageTable", u"\u4e0a\u4e00\u9875", None))
        self.pushButton_next_page.setText(QCoreApplication.translate("ImageTable", u"\u4e0b\u4e00\u9875", None))
    # retranslateUi

