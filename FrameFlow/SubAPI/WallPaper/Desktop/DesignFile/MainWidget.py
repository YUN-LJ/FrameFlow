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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from SubAPI.WallPaper.Desktop.ImageDisplay import ImageDisplay
from qfluentwidgets import (BodyLabel, CardWidget, ProgressBar)
from qfluentwidgets.components.widgets import PrimaryToolButton

class Ui_wallpaper(object):
    def setupUi(self, wallpaper):
        if not wallpaper.objectName():
            wallpaper.setObjectName(u"wallpaper")
        wallpaper.resize(798, 529)
        self.verticalLayout = QVBoxLayout(wallpaper)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget_options = CardWidget(wallpaper)
        self.widget_options.setObjectName(u"widget_options")
        self.horizontalLayout = QHBoxLayout(self.widget_options)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton_table_list = PrimaryToolButton(self.widget_options)
        self.pushButton_table_list.setObjectName(u"pushButton_table_list")
        self.pushButton_table_list.setMinimumSize(QSize(40, 40))
        self.pushButton_table_list.setMaximumSize(QSize(40, 40))

        self.horizontalLayout.addWidget(self.pushButton_table_list)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButton_back = PrimaryToolButton(self.widget_options)
        self.pushButton_back.setObjectName(u"pushButton_back")
        self.pushButton_back.setMinimumSize(QSize(40, 40))
        self.pushButton_back.setMaximumSize(QSize(40, 40))

        self.horizontalLayout.addWidget(self.pushButton_back)

        self.pushButton_play = PrimaryToolButton(self.widget_options)
        self.pushButton_play.setObjectName(u"pushButton_play")
        self.pushButton_play.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_play)

        self.pushButton_next = PrimaryToolButton(self.widget_options)
        self.pushButton_next.setObjectName(u"pushButton_next")
        self.pushButton_next.setMinimumSize(QSize(40, 40))
        self.pushButton_next.setMaximumSize(QSize(40, 40))

        self.horizontalLayout.addWidget(self.pushButton_next)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.pushButton_set = PrimaryToolButton(self.widget_options)
        self.pushButton_set.setObjectName(u"pushButton_set")
        self.pushButton_set.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_set)


        self.verticalLayout.addWidget(self.widget_options)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(10, -1, 10, -1)
        self.progressBar = ProgressBar(wallpaper)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)

        self.horizontalLayout_2.addWidget(self.progressBar)

        self.label_progress = BodyLabel(wallpaper)
        self.label_progress.setObjectName(u"label_progress")
        self.label_progress.setMinimumSize(QSize(0, 0))

        self.horizontalLayout_2.addWidget(self.label_progress)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.widget_image_display = ImageDisplay(wallpaper)
        self.widget_image_display.setObjectName(u"widget_image_display")

        self.verticalLayout.addWidget(self.widget_image_display)

        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(wallpaper)

        QMetaObject.connectSlotsByName(wallpaper)
    # setupUi

    def retranslateUi(self, wallpaper):
        wallpaper.setWindowTitle(QCoreApplication.translate("wallpaper", u"wallpaper", None))
        self.pushButton_table_list.setText("")
        self.pushButton_back.setText("")
        self.pushButton_play.setText("")
        self.pushButton_next.setText("")
        self.pushButton_set.setText("")
        self.label_progress.setText("")
    # retranslateUi

