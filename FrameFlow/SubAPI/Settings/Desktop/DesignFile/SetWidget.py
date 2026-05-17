# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SetWidget.ui'
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

from qfluentwidgets.components.widgets import (CardWidget, StrongBodyLabel, SwitchButton)


class Ui_base_sets(object):
    def setupUi(self, base_sets):
        if not base_sets.objectName():
            base_sets.setObjectName(u"base_sets")
        base_sets.resize(431, 194)
        self.verticalLayout = QVBoxLayout(base_sets)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget_start = CardWidget(base_sets)
        self.widget_start.setObjectName(u"widget_start")
        self.horizontalLayout = QHBoxLayout(self.widget_start)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_start = StrongBodyLabel(self.widget_start)
        self.label_start.setObjectName(u"label_start")
        self.label_start.setStyleSheet(u"font: 14pt;")

        self.horizontalLayout.addWidget(self.label_start)

        self.horizontalSpacer = QSpacerItem(158, 37, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.checkBox_start = SwitchButton(self.widget_start)
        self.checkBox_start.setObjectName(u"checkBox_start")
        self.checkBox_start.setMinimumSize(QSize(80, 40))
        self.checkBox_start.setMaximumSize(QSize(80, 40))
        self.checkBox_start.setStyleSheet(u"")

        self.horizontalLayout.addWidget(self.checkBox_start)

        self.verticalLayout.addWidget(self.widget_start)

        self.widget_theme = CardWidget(base_sets)
        self.widget_theme.setObjectName(u"widget_theme")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_theme)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_theme = StrongBodyLabel(self.widget_theme)
        self.label_theme.setObjectName(u"label_theme")
        self.label_theme.setStyleSheet(u"font: 14pt;")

        self.horizontalLayout_2.addWidget(self.label_theme)

        self.horizontalSpacer_2 = QSpacerItem(215, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.checkBox_theme = SwitchButton(self.widget_theme)
        self.checkBox_theme.setObjectName(u"checkBox_theme")
        self.checkBox_theme.setMinimumSize(QSize(80, 40))
        self.checkBox_theme.setMaximumSize(QSize(80, 40))

        self.horizontalLayout_2.addWidget(self.checkBox_theme)

        self.verticalLayout.addWidget(self.widget_theme)

        self.widget_terminal = CardWidget(base_sets)
        self.widget_terminal.setObjectName(u"widget_terminal")
        self.horizontalLayout_3 = QHBoxLayout(self.widget_terminal)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_terminal = StrongBodyLabel(self.widget_terminal)
        self.label_terminal.setObjectName(u"label_terminal")
        self.label_terminal.setStyleSheet(u"font: 14pt;")

        self.horizontalLayout_3.addWidget(self.label_terminal)

        self.horizontalSpacer_3 = QSpacerItem(158, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.checkBox_terminal = SwitchButton(self.widget_terminal)
        self.checkBox_terminal.setObjectName(u"checkBox_terminal")
        self.checkBox_terminal.setMinimumSize(QSize(80, 40))
        self.checkBox_terminal.setMaximumSize(QSize(80, 40))

        self.horizontalLayout_3.addWidget(self.checkBox_terminal)

        self.verticalLayout.addWidget(self.widget_terminal)

        Ui_base_sets.retranslateUi(self, base_sets)

        QMetaObject.connectSlotsByName(base_sets)

    # setupUi

    def retranslateUi(self, base_sets):
        base_sets.setWindowTitle(QCoreApplication.translate("base_sets", u"\u8bbe\u7f6e", None))
        self.label_start.setText(QCoreApplication.translate("base_sets", u"\u5f00\u673a\u81ea\u542f\u52a8", None))
        self.checkBox_start.setText(QCoreApplication.translate("base_sets", u"\u542f\u7528", None))
        self.label_theme.setText(QCoreApplication.translate("base_sets", u"\u4e3b\u9898", None))
        self.checkBox_theme.setText(QCoreApplication.translate("base_sets", u"\u6d45\u8272", None))
        self.label_terminal.setText(QCoreApplication.translate("base_sets", u"\u663e\u793a\u63a7\u5236\u53f0", None))
        self.checkBox_terminal.setText(QCoreApplication.translate("base_sets", u"\u5173\u95ed", None))
    # retranslateUi
