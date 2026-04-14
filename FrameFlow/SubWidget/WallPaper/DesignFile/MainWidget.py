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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QSizePolicy, QVBoxLayout,
    QWidget)

from qfluentwidgets.components.widgets import (BodyLabel, PrimaryPushButton, PrimaryToolButton, SearchLineEdit,
    SmoothScrollArea, SpinBox)

class Ui_wallpaper(object):
    def setupUi(self, wallpaper):
        if not wallpaper.objectName():
            wallpaper.setObjectName(u"wallpaper")
        wallpaper.resize(798, 529)
        self.verticalLayout = QVBoxLayout(wallpaper)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 10)
        self.scrollArea_options = SmoothScrollArea(wallpaper)
        self.scrollArea_options.setObjectName(u"scrollArea_options")
        self.scrollArea_options.setMinimumSize(QSize(0, 0))
        self.scrollArea_options.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 796, 58))
        self.horizontalLayout_2 = QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton_play = PrimaryToolButton(self.scrollAreaWidgetContents)
        self.pushButton_play.setObjectName(u"pushButton_play")
        self.pushButton_play.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_2.addWidget(self.pushButton_play)

        self.pushButton_set = PrimaryToolButton(self.scrollAreaWidgetContents)
        self.pushButton_set.setObjectName(u"pushButton_set")
        self.pushButton_set.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_2.addWidget(self.pushButton_set)

        self.label_progress = BodyLabel(self.scrollAreaWidgetContents)
        self.label_progress.setObjectName(u"label_progress")
        self.label_progress.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.horizontalLayout_2.addWidget(self.label_progress)

        self.lineEdit_search = SearchLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_search.setObjectName(u"lineEdit_search")
        self.lineEdit_search.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_2.addWidget(self.lineEdit_search)

        self.pushButton_select = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_select.setObjectName(u"pushButton_select")
        self.pushButton_select.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_2.addWidget(self.pushButton_select)

        self.pushButton_cancel_select = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_cancel_select.setObjectName(u"pushButton_cancel_select")
        self.pushButton_cancel_select.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_2.addWidget(self.pushButton_cancel_select)

        self.label_3 = BodyLabel(self.scrollAreaWidgetContents)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.horizontalLayout_2.addWidget(self.label_3)

        self.spinBox_time = SpinBox(self.scrollAreaWidgetContents)
        self.spinBox_time.setObjectName(u"spinBox_time")
        self.spinBox_time.setMinimumSize(QSize(0, 40))
        self.spinBox_time.setMinimum(1)
        self.spinBox_time.setMaximum(600)

        self.horizontalLayout_2.addWidget(self.spinBox_time)

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
        self.pushButton_play.setText("")
        self.pushButton_set.setText("")
        self.label_progress.setText("")
        self.lineEdit_search.setPlaceholderText(QCoreApplication.translate("wallpaper", u"\u8f93\u5165\u5173\u952e\u8bcd\u6216\u9996\u5b57\u6bcd\u53ef\u8fdb\u884c\u5b9a\u4f4d/\u9009\u62e9\u6761\u4ef6", None))
        self.pushButton_select.setText(QCoreApplication.translate("wallpaper", u"\u9009\u62e9", None))
        self.pushButton_cancel_select.setText(QCoreApplication.translate("wallpaper", u"\u53d6\u6d88", None))
        self.label_3.setText(QCoreApplication.translate("wallpaper", u"\u64ad\u653e\u95f4\u9694:", None))
    # retranslateUi

