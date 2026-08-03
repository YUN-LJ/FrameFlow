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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QSizePolicy,
    QTableWidgetItem, QVBoxLayout, QWidget)

from SubAPI.WallHaven.Desktop.SearchPage.SearchTable import SearchTable
from qfluentwidgets import (BodyLabel, CardWidget, SpinBox)
from qfluentwidgets.components.widgets import (PrimaryToolButton, SearchLineEdit, SmoothScrollArea)

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

        self.label_page_info = BodyLabel(self.widget_title)
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

        self.verticalLayout.setStretch(1, 1)

        self.verticalLayout_3.addLayout(self.verticalLayout)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)


        self.retranslateUi(SearchPage)

        QMetaObject.connectSlotsByName(SearchPage)
    # setupUi

    def retranslateUi(self, SearchPage):
        SearchPage.setWindowTitle(QCoreApplication.translate("SearchPage", u"\u641c\u7d22\u6a21\u5757", None))
        self.pushButton_expand.setText("")
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("SearchPage", u"\u8f93\u5165\u82f1\u6587\u5173\u952e\u8bcd,\u53f3\u952e\u663e\u793a\u641c\u7d22\u5386\u53f2", None))
        self.label_page_info.setText("")
    # retranslateUi

