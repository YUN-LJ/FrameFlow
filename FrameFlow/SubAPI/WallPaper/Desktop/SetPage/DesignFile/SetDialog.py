# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SetDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

from qfluentwidgets.components.widgets import (CheckBox, ComboBox, SubtitleLabel, SwitchButton)

class Ui_Sets(object):
    def setupUi(self, Sets):
        if not Sets.objectName():
            Sets.setObjectName(u"Sets")
        Sets.resize(400, 300)
        self.verticalLayout = QVBoxLayout(Sets)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(10)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.checkBox_general = CheckBox(Sets)
        self.checkBox_general.setObjectName(u"checkBox_general")

        self.horizontalLayout.addWidget(self.checkBox_general)

        self.checkBox_anime = CheckBox(Sets)
        self.checkBox_anime.setObjectName(u"checkBox_anime")

        self.horizontalLayout.addWidget(self.checkBox_anime)

        self.checkBox_people = CheckBox(Sets)
        self.checkBox_people.setObjectName(u"checkBox_people")

        self.horizontalLayout.addWidget(self.checkBox_people)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 1, 1)

        self.label = SubtitleLabel(Sets)
        self.label.setObjectName(u"label")
        self.label.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.comboBox = ComboBox(Sets)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.comboBox, 3, 1, 1, 1)

        self.label_2 = SubtitleLabel(Sets)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.label_order = SubtitleLabel(Sets)
        self.label_order.setObjectName(u"label_order")
        self.label_order.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_order, 3, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.comboBox_mode = ComboBox(Sets)
        self.comboBox_mode.addItem("")
        self.comboBox_mode.addItem("")
        self.comboBox_mode.addItem("")
        self.comboBox_mode.setObjectName(u"comboBox_mode")
        self.comboBox_mode.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.comboBox_mode, 2, 1, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.checkBox_sfw = CheckBox(Sets)
        self.checkBox_sfw.setObjectName(u"checkBox_sfw")

        self.horizontalLayout_2.addWidget(self.checkBox_sfw)

        self.checkBox_sketchy = CheckBox(Sets)
        self.checkBox_sketchy.setObjectName(u"checkBox_sketchy")

        self.horizontalLayout_2.addWidget(self.checkBox_sketchy)

        self.checkBox_nsfw = CheckBox(Sets)
        self.checkBox_nsfw.setObjectName(u"checkBox_nsfw")

        self.horizontalLayout_2.addWidget(self.checkBox_nsfw)


        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 1, 1, 1)

        self.label_mode = SubtitleLabel(Sets)
        self.label_mode.setObjectName(u"label_mode")
        self.label_mode.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_mode, 2, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 5, 0, 1, 1)

        self.checkBox_use_tag = SwitchButton(Sets)
        self.checkBox_use_tag.setObjectName(u"checkBox_use_tag")

        self.gridLayout.addWidget(self.checkBox_use_tag, 4, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter)


        self.verticalLayout.addLayout(self.gridLayout)


        self.retranslateUi(Sets)

        QMetaObject.connectSlotsByName(Sets)
    # setupUi

    def retranslateUi(self, Sets):
        Sets.setWindowTitle(QCoreApplication.translate("Sets", u"Form", None))
        self.checkBox_general.setText(QCoreApplication.translate("Sets", u"\u5e38\u89c4", None))
        self.checkBox_anime.setText(QCoreApplication.translate("Sets", u"\u52a8\u6f2b", None))
        self.checkBox_people.setText(QCoreApplication.translate("Sets", u"\u4eba\u7269", None))
        self.label.setText(QCoreApplication.translate("Sets", u"\u7c7b\u522b\u9009\u62e9", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("Sets", u"\u65e5\u671f", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("Sets", u"\u968f\u673a", None))

        self.label_2.setText(QCoreApplication.translate("Sets", u"\u5206\u7ea7\u9009\u62e9", None))
        self.label_order.setText(QCoreApplication.translate("Sets", u"\u64ad\u653e\u987a\u5e8f", None))
        self.comboBox_mode.setItemText(0, QCoreApplication.translate("Sets", u"\u7528\u6237\u6a21\u5f0f", None))
        self.comboBox_mode.setItemText(1, QCoreApplication.translate("Sets", u"\u6536\u85cf\u5939\u6a21\u5f0f", None))
        self.comboBox_mode.setItemText(2, QCoreApplication.translate("Sets", u"\u89c6\u9891\u6a21\u5f0f", None))

        self.checkBox_sfw.setText(QCoreApplication.translate("Sets", u"\u6b63\u5e38\u7ea7", None))
        self.checkBox_sketchy.setText(QCoreApplication.translate("Sets", u"\u7c97\u7565\u7ea7", None))
        self.checkBox_nsfw.setText(QCoreApplication.translate("Sets", u"\u9650\u5236\u7ea7", None))
        self.label_mode.setText(QCoreApplication.translate("Sets", u"\u64ad\u653e\u6a21\u5f0f", None))
        self.checkBox_use_tag.setText(QCoreApplication.translate("Sets", u"\u4f7f\u7528\u5173\u952e\u8bcd", None))
    # retranslateUi

