# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'home.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QScrollArea, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

from qfluentwidgets.components.widgets import SpinBox

class Ui_home(object):
    def setupUi(self, home):
        if not home.objectName():
            home.setObjectName(u"home")
        home.resize(876, 400)
        self.verticalLayout_2 = QVBoxLayout(home)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(home)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 862, 498))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, 10, -1, -1)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_ram_load = QLabel(self.scrollAreaWidgetContents)
        self.label_ram_load.setObjectName(u"label_ram_load")
        self.label_ram_load.setStyleSheet(u"font: 16pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_ram_load, 1, 2, 1, 1)

        self.label_gpu_load = QLabel(self.scrollAreaWidgetContents)
        self.label_gpu_load.setObjectName(u"label_gpu_load")
        self.label_gpu_load.setStyleSheet(u"font: 16pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_gpu_load, 1, 1, 1, 1)

        self.label_cpu_temp = QLabel(self.scrollAreaWidgetContents)
        self.label_cpu_temp.setObjectName(u"label_cpu_temp")
        self.label_cpu_temp.setStyleSheet(u"font: 16pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_cpu_temp, 0, 0, 1, 1)

        self.label = QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 4, 1, 1)

        self.label_hdd_temp = QLabel(self.scrollAreaWidgetContents)
        self.label_hdd_temp.setObjectName(u"label_hdd_temp")
        self.label_hdd_temp.setStyleSheet(u"font: 16pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_hdd_temp, 0, 2, 1, 1)

        self.label_gpu_temp = QLabel(self.scrollAreaWidgetContents)
        self.label_gpu_temp.setObjectName(u"label_gpu_temp")
        self.label_gpu_temp.setStyleSheet(u"font: 16pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_gpu_temp, 0, 1, 1, 1)

        self.label_cpu_load = QLabel(self.scrollAreaWidgetContents)
        self.label_cpu_load.setObjectName(u"label_cpu_load")
        self.label_cpu_load.setStyleSheet(u"font: 16pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_cpu_load, 1, 0, 1, 1)

        self.spinBox = SpinBox(self.scrollAreaWidgetContents)
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(30)

        self.gridLayout.addWidget(self.spinBox, 0, 5, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 3, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, -1, -1, -1)
        self.widget = QWidget(self.scrollAreaWidgetContents)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(0, 400))
        self.horizontalLayout_2 = QHBoxLayout(self.widget)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")

        self.horizontalLayout_2.addLayout(self.verticalLayout_4)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")

        self.horizontalLayout_2.addLayout(self.verticalLayout_5)


        self.horizontalLayout.addWidget(self.widget)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayout.setStretch(0, 3)
        self.verticalLayout.setStretch(1, 5)

        self.verticalLayout_3.addLayout(self.verticalLayout)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)


        self.retranslateUi(home)

        QMetaObject.connectSlotsByName(home)
    # setupUi

    def retranslateUi(self, home):
        home.setWindowTitle(QCoreApplication.translate("home", u"Form", None))
        self.label_ram_load.setText(QCoreApplication.translate("home", u"RAM\u4f7f\u7528\u7387:xx%", None))
        self.label_gpu_load.setText(QCoreApplication.translate("home", u"GPU\u4f7f\u7528\u7387:xx%", None))
        self.label_cpu_temp.setText(QCoreApplication.translate("home", u"CPU\u6e29\u5ea6:xx\u2103", None))
        self.label.setText(QCoreApplication.translate("home", u"\u66f4\u65b0\u65f6\u95f4", None))
        self.label_hdd_temp.setText(QCoreApplication.translate("home", u"HDD\u6e29\u5ea6:xx\u2103", None))
        self.label_gpu_temp.setText(QCoreApplication.translate("home", u"GPU\u6e29\u5ea6:xx\u2103", None))
        self.label_cpu_load.setText(QCoreApplication.translate("home", u"CPU\u4f7f\u7528\u7387:xx%", None))
    # retranslateUi

