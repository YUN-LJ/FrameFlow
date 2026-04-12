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
    QScrollArea, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

from qfluentwidgets.components.widgets import (ComboBox, PrimaryPushButton, SearchLineEdit, SpinBox,
    SwitchButton)

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
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 798, 110))
        self.horizontalLayout_2 = QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_mode = QLabel(self.scrollAreaWidgetContents)
        self.label_mode.setObjectName(u"label_mode")
        self.label_mode.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.horizontalLayout_4.addWidget(self.label_mode)

        self.comboBox_mode = ComboBox(self.scrollAreaWidgetContents)
        self.comboBox_mode.addItem("")
        self.comboBox_mode.addItem("")
        self.comboBox_mode.addItem("")
        self.comboBox_mode.setObjectName(u"comboBox_mode")
        self.comboBox_mode.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_4.addWidget(self.comboBox_mode)

        self.checkBox_use_tag = SwitchButton(self.scrollAreaWidgetContents)
        self.checkBox_use_tag.setObjectName(u"checkBox_use_tag")

        self.horizontalLayout_4.addWidget(self.checkBox_use_tag)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.label_order = QLabel(self.scrollAreaWidgetContents)
        self.label_order.setObjectName(u"label_order")
        self.label_order.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.horizontalLayout_4.addWidget(self.label_order)

        self.comboBox = ComboBox(self.scrollAreaWidgetContents)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_4.addWidget(self.comboBox)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)

        self.label = QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName(u"label")
        self.label.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.horizontalLayout_4.addWidget(self.label)

        self.spinBox_time = SpinBox(self.scrollAreaWidgetContents)
        self.spinBox_time.setObjectName(u"spinBox_time")
        self.spinBox_time.setMinimumSize(QSize(0, 40))
        self.spinBox_time.setMinimum(1)
        self.spinBox_time.setMaximum(600)

        self.horizontalLayout_4.addWidget(self.spinBox_time)


        self.gridLayout.addLayout(self.horizontalLayout_4, 3, 1, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_progress = QLabel(self.scrollAreaWidgetContents)
        self.label_progress.setObjectName(u"label_progress")
        self.label_progress.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.horizontalLayout_3.addWidget(self.label_progress)

        self.lineEdit_search = SearchLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_search.setObjectName(u"lineEdit_search")
        self.lineEdit_search.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_3.addWidget(self.lineEdit_search)

        self.pushButton_select = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_select.setObjectName(u"pushButton_select")
        self.pushButton_select.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_3.addWidget(self.pushButton_select)

        self.pushButton_cancel_select = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_cancel_select.setObjectName(u"pushButton_cancel_select")
        self.pushButton_cancel_select.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_3.addWidget(self.pushButton_cancel_select)


        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 1, 1, 1)

        self.pushButton_play = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_play.setObjectName(u"pushButton_play")
        self.pushButton_play.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.pushButton_play, 1, 0, 1, 1)

        self.pushButton_set = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_set.setObjectName(u"pushButton_set")
        self.pushButton_set.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.pushButton_set, 3, 0, 1, 1)


        self.horizontalLayout_2.addLayout(self.gridLayout)

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
        self.label_mode.setText(QCoreApplication.translate("wallpaper", u"\u64ad\u653e\u6a21\u5f0f:", None))
        self.comboBox_mode.setItemText(0, QCoreApplication.translate("wallpaper", u"\u7528\u6237\u6a21\u5f0f", None))
        self.comboBox_mode.setItemText(1, QCoreApplication.translate("wallpaper", u"\u6536\u85cf\u5939\u6a21\u5f0f", None))
        self.comboBox_mode.setItemText(2, QCoreApplication.translate("wallpaper", u"\u89c6\u9891\u6a21\u5f0f", None))

        self.checkBox_use_tag.setText(QCoreApplication.translate("wallpaper", u"\u4f7f\u7528\u5173\u952e\u8bcd", None))
        self.label_order.setText(QCoreApplication.translate("wallpaper", u"\u64ad\u653e\u987a\u5e8f:", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("wallpaper", u"\u65e5\u671f", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("wallpaper", u"\u968f\u673a", None))

        self.label.setText(QCoreApplication.translate("wallpaper", u"\u64ad\u653e\u95f4\u9694:", None))
        self.label_progress.setText("")
        self.lineEdit_search.setPlaceholderText(QCoreApplication.translate("wallpaper", u"\u8f93\u5165\u5173\u952e\u8bcd\u6216\u9996\u5b57\u6bcd\u53ef\u8fdb\u884c\u5b9a\u4f4d/\u9009\u62e9\u6761\u4ef6", None))
        self.pushButton_select.setText(QCoreApplication.translate("wallpaper", u"\u6761\u4ef6\u9009\u62e9", None))
        self.pushButton_cancel_select.setText(QCoreApplication.translate("wallpaper", u"\u53d6\u6d88\u9009\u62e9", None))
        self.pushButton_play.setText(QCoreApplication.translate("wallpaper", u"\u64ad\u653e", None))
        self.pushButton_set.setText(QCoreApplication.translate("wallpaper", u"\u8bbe\u7f6e", None))
    # retranslateUi

