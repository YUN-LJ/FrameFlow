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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QScrollArea, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from qfluentwidgets.components.widgets import (ComboBox, PrimaryPushButton, SpinBox)

class Ui_wallpaper(object):
    def setupUi(self, wallpaper):
        if not wallpaper.objectName():
            wallpaper.setObjectName(u"wallpaper")
        wallpaper.resize(800, 500)
        self.verticalLayout = QVBoxLayout(wallpaper)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 10)
        self.scrollArea_options = QScrollArea(wallpaper)
        self.scrollArea_options.setObjectName(u"scrollArea_options")
        self.scrollArea_options.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 798, 106))
        self.horizontalLayout_2 = QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton_play = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_play.setObjectName(u"pushButton_play")
        self.pushButton_play.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_2.addWidget(self.pushButton_play)

        self.pushButton_choice_all = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_choice_all.setObjectName(u"pushButton_choice_all")
        self.pushButton_choice_all.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_2.addWidget(self.pushButton_choice_all)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.lineEdit_search = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_search.setObjectName(u"lineEdit_search")
        self.lineEdit_search.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.lineEdit_search, 0, 2, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 0, 1, 1)

        self.label = QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName(u"label")
        self.label.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label, 2, 4, 1, 1)

        self.spinBox_time = SpinBox(self.scrollAreaWidgetContents)
        self.spinBox_time.setObjectName(u"spinBox_time")
        self.spinBox_time.setMinimumSize(QSize(0, 40))
        self.spinBox_time.setMinimum(1)
        self.spinBox_time.setMaximum(600)

        self.gridLayout.addWidget(self.spinBox_time, 2, 5, 1, 1)

        self.comboBox = ComboBox(self.scrollAreaWidgetContents)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.comboBox, 0, 5, 1, 1)

        self.label_order = QLabel(self.scrollAreaWidgetContents)
        self.label_order.setObjectName(u"label_order")
        self.label_order.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_order, 0, 4, 1, 1)

        self.label_mode = QLabel(self.scrollAreaWidgetContents)
        self.label_mode.setObjectName(u"label_mode")
        self.label_mode.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_mode, 2, 1, 1, 1)

        self.comboBox_mode = ComboBox(self.scrollAreaWidgetContents)
        self.comboBox_mode.addItem("")
        self.comboBox_mode.addItem("")
        self.comboBox_mode.addItem("")
        self.comboBox_mode.setObjectName(u"comboBox_mode")
        self.comboBox_mode.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.comboBox_mode, 2, 2, 1, 1)


        self.horizontalLayout_2.addLayout(self.gridLayout)

        self.pushButton_set = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_set.setObjectName(u"pushButton_set")
        self.pushButton_set.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_2.addWidget(self.pushButton_set)

        self.scrollArea_options.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea_options)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(wallpaper)

        QMetaObject.connectSlotsByName(wallpaper)
    # setupUi

    def retranslateUi(self, wallpaper):
        wallpaper.setWindowTitle(QCoreApplication.translate("wallpaper", u"wallpaper", None))
        self.pushButton_play.setText(QCoreApplication.translate("wallpaper", u"\u64ad\u653e", None))
        self.pushButton_choice_all.setText(QCoreApplication.translate("wallpaper", u"\u5168\u9009", None))
        self.label.setText(QCoreApplication.translate("wallpaper", u"\u64ad\u653e\u95f4\u9694:", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("wallpaper", u"\u65e5\u671f", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("wallpaper", u"\u968f\u673a", None))

        self.label_order.setText(QCoreApplication.translate("wallpaper", u"\u64ad\u653e\u987a\u5e8f", None))
        self.label_mode.setText(QCoreApplication.translate("wallpaper", u"\u64ad\u653e\u6a21\u5f0f:", None))
        self.comboBox_mode.setItemText(0, QCoreApplication.translate("wallpaper", u"\u7528\u6237\u6a21\u5f0f", None))
        self.comboBox_mode.setItemText(1, QCoreApplication.translate("wallpaper", u"\u6536\u85cf\u5939\u6a21\u5f0f", None))
        self.comboBox_mode.setItemText(2, QCoreApplication.translate("wallpaper", u"\u89c6\u9891\u6a21\u5f0f", None))

        self.pushButton_set.setText(QCoreApplication.translate("wallpaper", u"\u8bbe\u7f6e", None))
    # retranslateUi

