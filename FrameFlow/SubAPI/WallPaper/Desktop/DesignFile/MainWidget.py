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

from Fun.QtWidget import SidebarWidget
from SubAPI.WallPaper.Desktop.SetPage import SetWidget
from qfluentwidgets import CardWidget
from qfluentwidgets.components.widgets import (BodyLabel, PrimaryPushButton, PrimaryToolButton, SearchLineEdit,
    SpinBox)

class Ui_wallpaper(object):
    def setupUi(self, wallpaper):
        if not wallpaper.objectName():
            wallpaper.setObjectName(u"wallpaper")
        wallpaper.resize(798, 529)
        self.verticalLayout = QVBoxLayout(wallpaper)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget_sets = SidebarWidget(wallpaper)
        self.widget_sets.setObjectName(u"widget_sets")
        self.widget_sets.setMinimumSize(QSize(0, 100))
        self.verticalLayout_2 = QVBoxLayout(self.widget_sets)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.set_page = SetWidget(self.widget_sets)
        self.set_page.setObjectName(u"set_page")

        self.verticalLayout_2.addWidget(self.set_page)


        self.verticalLayout.addWidget(self.widget_sets)

        self.widget_options = CardWidget(wallpaper)
        self.widget_options.setObjectName(u"widget_options")
        self.horizontalLayout = QHBoxLayout(self.widget_options)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton_play = PrimaryToolButton(self.widget_options)
        self.pushButton_play.setObjectName(u"pushButton_play")
        self.pushButton_play.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_play)

        self.pushButton_set = PrimaryToolButton(self.widget_options)
        self.pushButton_set.setObjectName(u"pushButton_set")
        self.pushButton_set.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_set)

        self.label_progress = BodyLabel(self.widget_options)
        self.label_progress.setObjectName(u"label_progress")

        self.horizontalLayout.addWidget(self.label_progress)

        self.lineEdit_search = SearchLineEdit(self.widget_options)
        self.lineEdit_search.setObjectName(u"lineEdit_search")
        self.lineEdit_search.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.lineEdit_search)

        self.pushButton_select = PrimaryPushButton(self.widget_options)
        self.pushButton_select.setObjectName(u"pushButton_select")
        self.pushButton_select.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_select)

        self.pushButton_cancel_select = PrimaryPushButton(self.widget_options)
        self.pushButton_cancel_select.setObjectName(u"pushButton_cancel_select")
        self.pushButton_cancel_select.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_cancel_select)

        self.label_3 = BodyLabel(self.widget_options)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.horizontalLayout.addWidget(self.label_3)

        self.spinBox_time = SpinBox(self.widget_options)
        self.spinBox_time.setObjectName(u"spinBox_time")
        self.spinBox_time.setMinimumSize(QSize(0, 40))
        self.spinBox_time.setMinimum(1)
        self.spinBox_time.setMaximum(600)

        self.horizontalLayout.addWidget(self.spinBox_time)


        self.verticalLayout.addWidget(self.widget_options)

        self.widget_splitter = CardWidget(wallpaper)
        self.widget_splitter.setObjectName(u"widget_splitter")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_splitter)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")

        self.verticalLayout.addWidget(self.widget_splitter)

        self.verticalLayout.setStretch(2, 1)

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

