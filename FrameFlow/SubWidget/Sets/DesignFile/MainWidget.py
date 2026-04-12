# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget)

from Fun.QtWidget.FWidget import TerminalWidget
from qfluentwidgets.components.widgets import SwitchButton

class Ui_sets(object):
    def setupUi(self, sets):
        if not sets.objectName():
            sets.setObjectName(u"sets")
        sets.resize(800, 500)
        self.verticalLayout = QVBoxLayout(sets)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(sets)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 798, 498))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setVerticalSpacing(20)
        self.gridLayout.setContentsMargins(80, 20, 80, -1)
        self.label_2 = QLabel(self.scrollAreaWidgetContents)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setStyleSheet(u"font: 14pt;")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.checkBox_2 = SwitchButton(self.scrollAreaWidgetContents)
        self.checkBox_2.setObjectName(u"checkBox_2")
        self.checkBox_2.setMinimumSize(QSize(80, 40))
        self.checkBox_2.setMaximumSize(QSize(80, 40))

        self.gridLayout.addWidget(self.checkBox_2, 1, 1, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.label = QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName(u"label")
        self.label.setStyleSheet(u"font: 14pt;")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.checkBox = SwitchButton(self.scrollAreaWidgetContents)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setMinimumSize(QSize(80, 40))
        self.checkBox.setMaximumSize(QSize(80, 40))
        self.checkBox.setStyleSheet(u"")

        self.gridLayout.addWidget(self.checkBox, 0, 1, 1, 1, Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTop)


        self.verticalLayout_2.addLayout(self.gridLayout)

        self.widget = TerminalWidget(self.scrollAreaWidgetContents)
        self.widget.setObjectName(u"widget")

        self.verticalLayout_2.addWidget(self.widget)

        self.verticalLayout_2.setStretch(1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(sets)

        QMetaObject.connectSlotsByName(sets)
    # setupUi

    def retranslateUi(self, sets):
        sets.setWindowTitle(QCoreApplication.translate("sets", u"\u8bbe\u7f6e", None))
        self.label_2.setText(QCoreApplication.translate("sets", u"\u4e3b\u9898", None))
        self.checkBox_2.setText(QCoreApplication.translate("sets", u"\u6d45\u8272", None))
        self.label.setText(QCoreApplication.translate("sets", u"\u5f00\u673a\u81ea\u542f\u52a8", None))
        self.checkBox.setText(QCoreApplication.translate("sets", u"\u542f\u7528", None))
    # retranslateUi

