# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ImageDisplay.ui'
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

from Fun.QtWidget import ImageWidget
from qfluentwidgets.components.widgets import (PrimaryToolButton, SwitchButton)


class Ui_image_display(object):
    def setupUi(self, image_display):
        if not image_display.objectName():
            image_display.setObjectName(u"image_display")
        image_display.resize(572, 404)
        self.verticalLayout = QVBoxLayout(image_display)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 10, 0, 0)
        self.image_widget_options = QWidget(image_display)
        self.image_widget_options.setObjectName(u"image_widget_options")
        self.horizontalLayout_2 = QHBoxLayout(self.image_widget_options)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.checkBox = SwitchButton(self.image_widget_options)
        self.checkBox.setObjectName(u"checkBox")

        self.horizontalLayout_2.addWidget(self.checkBox)

        self.checkBox_zoom = SwitchButton(self.image_widget_options)
        self.checkBox_zoom.setObjectName(u"checkBox_zoom")

        self.horizontalLayout_2.addWidget(self.checkBox_zoom)

        self.pushButton_copy = PrimaryToolButton(self.image_widget_options)
        self.pushButton_copy.setObjectName(u"pushButton_copy")
        self.pushButton_copy.setMinimumSize(QSize(30, 30))
        self.pushButton_copy.setMaximumSize(QSize(30, 30))

        self.horizontalLayout_2.addWidget(self.pushButton_copy)

        self.pushButton_open = PrimaryToolButton(self.image_widget_options)
        self.pushButton_open.setObjectName(u"pushButton_open")
        self.pushButton_open.setMinimumSize(QSize(30, 30))
        self.pushButton_open.setMaximumSize(QSize(30, 30))

        self.horizontalLayout_2.addWidget(self.pushButton_open)

        self.pushButton_full = PrimaryToolButton(self.image_widget_options)
        self.pushButton_full.setObjectName(u"pushButton_full")
        self.pushButton_full.setMinimumSize(QSize(30, 30))
        self.pushButton_full.setMaximumSize(QSize(30, 30))

        self.horizontalLayout_2.addWidget(self.pushButton_full)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.verticalLayout.addWidget(self.image_widget_options)

        self.image_widget = ImageWidget(parent=image_display)
        self.image_widget.setObjectName(u"image_widget")

        self.verticalLayout.addWidget(self.image_widget)

        self.verticalLayout.setStretch(1, 1)

        Ui_image_display.retranslateUi(self, image_display)

        QMetaObject.connectSlotsByName(image_display)

    # setupUi

    def retranslateUi(self, image_display):
        image_display.setWindowTitle(QCoreApplication.translate("image_display", u"Form", None))
        self.checkBox.setText(
            QCoreApplication.translate("image_display", u"\u5173\u95ed\u81ea\u52a8\u6682\u505c", None))
        self.checkBox_zoom.setText(QCoreApplication.translate("image_display", u"\u542f\u7528\u7f29\u653e", None))
        self.pushButton_copy.setText("")
        self.pushButton_open.setText("")
        self.pushButton_full.setText("")
    # retranslateUi
