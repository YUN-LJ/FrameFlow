# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SetPage.ui'
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

from qfluentwidgets import (LineEdit, SpinBox)
from qfluentwidgets.components.widgets import (CardWidget, ComboBox, PrimaryPushButton, StrongBodyLabel)

class Ui_set_page(object):
    def setupUi(self, set_page):
        if not set_page.objectName():
            set_page.setObjectName(u"set_page")
        set_page.resize(610, 418)
        self.verticalLayout = QVBoxLayout(set_page)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 10, 0, 0)
        self.widget = CardWidget(set_page)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_save_dir = StrongBodyLabel(self.widget)
        self.label_save_dir.setObjectName(u"label_save_dir")
        self.label_save_dir.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.horizontalLayout.addWidget(self.label_save_dir)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.lineEdit_save_dir = LineEdit(self.widget)
        self.lineEdit_save_dir.setObjectName(u"lineEdit_save_dir")
        self.lineEdit_save_dir.setMinimumSize(QSize(250, 40))

        self.horizontalLayout.addWidget(self.lineEdit_save_dir)

        self.pushButton_save_dir = PrimaryPushButton(self.widget)
        self.pushButton_save_dir.setObjectName(u"pushButton_save_dir")
        self.pushButton_save_dir.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.pushButton_save_dir)


        self.verticalLayout.addWidget(self.widget)

        self.widget_2 = CardWidget(set_page)
        self.widget_2.setObjectName(u"widget_2")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_proxy = StrongBodyLabel(self.widget_2)
        self.label_proxy.setObjectName(u"label_proxy")
        self.label_proxy.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.horizontalLayout_2.addWidget(self.label_proxy)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.lineEdit_proxy = LineEdit(self.widget_2)
        self.lineEdit_proxy.setObjectName(u"lineEdit_proxy")
        self.lineEdit_proxy.setMinimumSize(QSize(250, 40))

        self.horizontalLayout_2.addWidget(self.lineEdit_proxy)

        self.pushButton_proxy = PrimaryPushButton(self.widget_2)
        self.pushButton_proxy.setObjectName(u"pushButton_proxy")
        self.pushButton_proxy.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_2.addWidget(self.pushButton_proxy)


        self.verticalLayout.addWidget(self.widget_2)

        self.widget_3 = CardWidget(set_page)
        self.widget_3.setObjectName(u"widget_3")
        self.horizontalLayout_3 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_api = StrongBodyLabel(self.widget_3)
        self.label_api.setObjectName(u"label_api")
        self.label_api.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.horizontalLayout_3.addWidget(self.label_api)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_6)

        self.lineEdit_api = LineEdit(self.widget_3)
        self.lineEdit_api.setObjectName(u"lineEdit_api")
        self.lineEdit_api.setMinimumSize(QSize(250, 40))

        self.horizontalLayout_3.addWidget(self.lineEdit_api)

        self.pushButton_api = PrimaryPushButton(self.widget_3)
        self.pushButton_api.setObjectName(u"pushButton_api")
        self.pushButton_api.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_3.addWidget(self.pushButton_api)


        self.verticalLayout.addWidget(self.widget_3)

        self.widget_4 = CardWidget(set_page)
        self.widget_4.setObjectName(u"widget_4")
        self.horizontalLayout_4 = QHBoxLayout(self.widget_4)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_output = StrongBodyLabel(self.widget_4)
        self.label_output.setObjectName(u"label_output")
        self.label_output.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.horizontalLayout_4.addWidget(self.label_output)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.comboBox_output = ComboBox(self.widget_4)
        self.comboBox_output.addItem("")
        self.comboBox_output.addItem("")
        self.comboBox_output.setObjectName(u"comboBox_output")
        self.comboBox_output.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_4.addWidget(self.comboBox_output)

        self.pushButton_output = PrimaryPushButton(self.widget_4)
        self.pushButton_output.setObjectName(u"pushButton_output")
        self.pushButton_output.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_4.addWidget(self.pushButton_output)


        self.verticalLayout.addWidget(self.widget_4)

        self.widget_5 = CardWidget(set_page)
        self.widget_5.setObjectName(u"widget_5")
        self.horizontalLayout_5 = QHBoxLayout(self.widget_5)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_input = StrongBodyLabel(self.widget_5)
        self.label_input.setObjectName(u"label_input")
        self.label_input.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.horizontalLayout_5.addWidget(self.label_input)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_4)

        self.comboBox_input = ComboBox(self.widget_5)
        self.comboBox_input.addItem("")
        self.comboBox_input.addItem("")
        self.comboBox_input.setObjectName(u"comboBox_input")
        self.comboBox_input.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_5.addWidget(self.comboBox_input)

        self.pushButton_input = PrimaryPushButton(self.widget_5)
        self.pushButton_input.setObjectName(u"pushButton_input")
        self.pushButton_input.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_5.addWidget(self.pushButton_input)


        self.verticalLayout.addWidget(self.widget_5)

        self.widget_6 = CardWidget(set_page)
        self.widget_6.setObjectName(u"widget_6")
        self.horizontalLayout_6 = QHBoxLayout(self.widget_6)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_history = StrongBodyLabel(self.widget_6)
        self.label_history.setObjectName(u"label_history")
        self.label_history.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.horizontalLayout_6.addWidget(self.label_history)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_5)

        self.spinBox_history = SpinBox(self.widget_6)
        self.spinBox_history.setObjectName(u"spinBox_history")
        self.spinBox_history.setMinimumSize(QSize(0, 40))
        self.spinBox_history.setMinimum(5)
        self.spinBox_history.setMaximum(20)

        self.horizontalLayout_6.addWidget(self.spinBox_history)

        self.pushButton_history_num = PrimaryPushButton(self.widget_6)
        self.pushButton_history_num.setObjectName(u"pushButton_history_num")
        self.pushButton_history_num.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_6.addWidget(self.pushButton_history_num)


        self.verticalLayout.addWidget(self.widget_6)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(set_page)

        QMetaObject.connectSlotsByName(set_page)
    # setupUi

    def retranslateUi(self, set_page):
        set_page.setWindowTitle(QCoreApplication.translate("set_page", u"Form", None))
        self.label_save_dir.setText(QCoreApplication.translate("set_page", u"\u56fe\u50cf\u4fdd\u5b58\u8def\u5f84", None))
        self.lineEdit_save_dir.setPlaceholderText(QCoreApplication.translate("set_page", u"\u4fdd\u5b58\u8def\u5f84", None))
        self.pushButton_save_dir.setText(QCoreApplication.translate("set_page", u"\u9884\u89c8", None))
        self.label_proxy.setText(QCoreApplication.translate("set_page", u"\u4ee3\u7406\u8bbe\u7f6e      ", None))
        self.lineEdit_proxy.setPlaceholderText(QCoreApplication.translate("set_page", u"127.0.0.1:8080", None))
        self.pushButton_proxy.setText(QCoreApplication.translate("set_page", u"\u9a8c\u8bc1", None))
        self.label_api.setText(QCoreApplication.translate("set_page", u"WallhaveAPI", None))
        self.lineEdit_api.setPlaceholderText(QCoreApplication.translate("set_page", u"\u586b\u5199API", None))
        self.pushButton_api.setText(QCoreApplication.translate("set_page", u"\u9a8c\u8bc1", None))
        self.label_output.setText(QCoreApplication.translate("set_page", u"\u5bfc\u51fa\u6570\u636e", None))
        self.comboBox_output.setItemText(0, QCoreApplication.translate("set_page", u"\u56fe\u50cf\u4fe1\u606f", None))
        self.comboBox_output.setItemText(1, QCoreApplication.translate("set_page", u"\u6536\u85cf\u5939\u6570\u636e", None))

        self.pushButton_output.setText(QCoreApplication.translate("set_page", u"\u5bfc\u51fa", None))
        self.label_input.setText(QCoreApplication.translate("set_page", u"\u5bfc\u5165\u6570\u636e", None))
        self.comboBox_input.setItemText(0, QCoreApplication.translate("set_page", u"\u56fe\u50cf\u4fe1\u606f", None))
        self.comboBox_input.setItemText(1, QCoreApplication.translate("set_page", u"\u6536\u85cf\u5939\u6570\u636e", None))

        self.pushButton_input.setText(QCoreApplication.translate("set_page", u"\u5bfc\u5165", None))
        self.label_history.setText(QCoreApplication.translate("set_page", u"\u5386\u53f2\u8bb0\u5f55\u6570\u91cf", None))
        self.pushButton_history_num.setText(QCoreApplication.translate("set_page", u"\u786e\u5b9a", None))
    # retranslateUi

