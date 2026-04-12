# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'KeyWordPage.ui'
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
    QProgressBar, QScrollArea, QSizePolicy, QSpacerItem,
    QTableWidgetItem, QVBoxLayout, QWidget)

from SubWidget.Home.SlotFunc.KeyPageCtrl import Table
from qfluentwidgets.components.widgets import (PrimaryPushButton, SearchLineEdit)

class Ui_KeyWordWidget(object):
    def setupUi(self, KeyWordWidget):
        if not KeyWordWidget.objectName():
            KeyWordWidget.setObjectName(u"KeyWordWidget")
        KeyWordWidget.resize(570, 300)
        self.verticalLayout = QVBoxLayout(KeyWordWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(KeyWordWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 568, 298))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.lineEdit = SearchLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.lineEdit)

        self.pushButton_add = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_add.setObjectName(u"pushButton_add")
        self.pushButton_add.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_add)

        self.pushButton_delete = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_delete.setObjectName(u"pushButton_delete")
        self.pushButton_delete.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_delete)

        self.pushButton_select_all = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_select_all.setObjectName(u"pushButton_select_all")
        self.pushButton_select_all.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_select_all)

        self.pushButton_update = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_update.setObjectName(u"pushButton_update")
        self.pushButton_update.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_update)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.progress_label = QLabel(self.scrollAreaWidgetContents)
        self.progress_label.setObjectName(u"progress_label")

        self.horizontalLayout_2.addWidget(self.progress_label)

        self.progressBar = QProgressBar(self.scrollAreaWidgetContents)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setEnabled(True)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)

        self.horizontalLayout_2.addWidget(self.progressBar)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.tableWidget = Table(self.scrollAreaWidgetContents)
        self.tableWidget.setObjectName(u"tableWidget")

        self.verticalLayout_2.addWidget(self.tableWidget)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(KeyWordWidget)

        QMetaObject.connectSlotsByName(KeyWordWidget)
    # setupUi

    def retranslateUi(self, KeyWordWidget):
        KeyWordWidget.setWindowTitle(QCoreApplication.translate("KeyWordWidget", u"Form", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("KeyWordWidget", u"\u641c\u7d22\u5173\u952e\u8bcd\u6216\u6dfb\u52a0\u5173\u952e\u8bcd", None))
        self.pushButton_add.setText(QCoreApplication.translate("KeyWordWidget", u"\u65b0\u589e", None))
        self.pushButton_delete.setText(QCoreApplication.translate("KeyWordWidget", u"\u5220\u9664", None))
        self.pushButton_select_all.setText(QCoreApplication.translate("KeyWordWidget", u"\u5168\u9009", None))
        self.pushButton_update.setText(QCoreApplication.translate("KeyWordWidget", u"\u66f4\u65b0", None))
        self.progress_label.setText("")
    # retranslateUi

