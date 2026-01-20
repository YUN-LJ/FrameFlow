# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ImageDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QScrollArea,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

from qfluentwidgets.components.widgets import (PrimaryPushButton, ProgressBar)

class Ui_Image(object):
    def setupUi(self, Image):
        if not Image.objectName():
            Image.setObjectName(u"Image")
        Image.resize(600, 500)
        self.verticalLayout = QVBoxLayout(Image)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.pushButton_full = PrimaryPushButton(Image)
        self.pushButton_full.setObjectName(u"pushButton_full")
        self.pushButton_full.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_3.addWidget(self.pushButton_full)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.progressBar = ProgressBar(Image)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)

        self.verticalLayout.addWidget(self.progressBar)

        self.scrollArea = QScrollArea(Image)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setMinimumSize(QSize(0, 80))
        self.scrollArea.setMaximumSize(QSize(16777215, 80))
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 598, 78))
        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.verticalLayout.setStretch(0, 1)

        self.retranslateUi(Image)

        QMetaObject.connectSlotsByName(Image)
    # setupUi

    def retranslateUi(self, Image):
        Image.setWindowTitle(QCoreApplication.translate("Image", u"\u56fe\u7247\u8be6\u7ec6", None))
        self.pushButton_full.setText(QCoreApplication.translate("Image", u"\u5168\u5c4f", None))
    # retranslateUi

