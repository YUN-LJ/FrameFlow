# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'set.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

from qfluentwidgets.components.widgets import SpinBox

class Ui_set(object):
    def setupUi(self, set):
        if not set.objectName():
            set.setObjectName(u"set")
        set.resize(400, 400)
        set.setMinimumSize(QSize(400, 400))
        set.setMaximumSize(QSize(400, 400))
        self.verticalLayout = QVBoxLayout(set)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setVerticalSpacing(5)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 1, 1, 1)

        self.label_paly_time = QLabel(set)
        self.label_paly_time.setObjectName(u"label_paly_time")
        self.label_paly_time.setStyleSheet(u"font: 16pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_paly_time, 0, 0, 1, 1)

        self.spinBox_paly_time = SpinBox(set)
        self.spinBox_paly_time.setObjectName(u"spinBox_paly_time")
        self.spinBox_paly_time.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.spinBox_paly_time, 0, 2, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 2, 2, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 2, 0, 1, 1)

        self.line = QFrame(set)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line, 1, 0, 1, 1)

        self.line_2 = QFrame(set)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_2, 1, 1, 1, 1)

        self.line_3 = QFrame(set)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_3, 1, 2, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)


        self.retranslateUi(set)

        QMetaObject.connectSlotsByName(set)
    # setupUi

    def retranslateUi(self, set):
        set.setWindowTitle(QCoreApplication.translate("set", u"\u58c1\u7eb8\u64ad\u653e\u8bbe\u7f6e", None))
        self.label_paly_time.setText(QCoreApplication.translate("set", u"\u64ad\u653e\u65f6\u95f4\uff1a", None))
    # retranslateUi

