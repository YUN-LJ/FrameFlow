# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LikePage.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QProgressBar,
    QSizePolicy, QSpacerItem, QTableWidgetItem, QVBoxLayout,
    QWidget)

from SubAPI.WallHaven.Desktop.LikePage.LikeTable import LikeTable
from qfluentwidgets.components.widgets import (BodyLabel, PrimaryPushButton, SearchLineEdit, SmoothScrollArea)

class Ui_like_widget(object):
    def setupUi(self, like_widget):
        if not like_widget.objectName():
            like_widget.setObjectName(u"like_widget")
        like_widget.resize(570, 300)
        self.verticalLayout = QVBoxLayout(like_widget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = SmoothScrollArea(like_widget)
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

        self.pushButton_update = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_update.setObjectName(u"pushButton_update")
        self.pushButton_update.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_update)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.progress_label = BodyLabel(self.scrollAreaWidgetContents)
        self.progress_label.setObjectName(u"progress_label")

        self.horizontalLayout_2.addWidget(self.progress_label)

        self.progressBar = QProgressBar(self.scrollAreaWidgetContents)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setEnabled(True)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)

        self.horizontalLayout_2.addWidget(self.progressBar)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.tableWidget = LikeTable(self.scrollAreaWidgetContents)
        self.tableWidget.setObjectName(u"tableWidget")

        self.verticalLayout_2.addWidget(self.tableWidget)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(like_widget)

        QMetaObject.connectSlotsByName(like_widget)
    # setupUi

    def retranslateUi(self, like_widget):
        like_widget.setWindowTitle(QCoreApplication.translate("like_widget", u"\u6536\u85cf\u6a21\u5757", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("like_widget", u"\u641c\u7d22\u5173\u952e\u8bcd\u6216\u6dfb\u52a0\u5173\u952e\u8bcd", None))
        self.pushButton_add.setText(QCoreApplication.translate("like_widget", u"\u65b0\u589e", None))
        self.pushButton_delete.setText(QCoreApplication.translate("like_widget", u"\u5220\u9664", None))
        self.pushButton_update.setText(QCoreApplication.translate("like_widget", u"\u66f4\u65b0", None))
        self.progress_label.setText("")
    # retranslateUi

