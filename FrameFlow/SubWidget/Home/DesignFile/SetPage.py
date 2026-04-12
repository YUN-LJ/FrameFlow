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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QScrollArea, QSizePolicy, QSpacerItem,
    QSpinBox, QVBoxLayout, QWidget)

from qfluentwidgets.components.widgets import (ComboBox, PrimaryPushButton)

class Ui_set_page(object):
    def setupUi(self, set_page):
        if not set_page.objectName():
            set_page.setObjectName(u"set_page")
        set_page.resize(610, 333)
        self.verticalLayout = QVBoxLayout(set_page)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(set_page)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 608, 331))
        self.horizontalLayout = QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(10)
        self.gridLayout.setObjectName(u"gridLayout")
        self.spinBox_thread_num = QSpinBox(self.scrollAreaWidgetContents)
        self.spinBox_thread_num.setObjectName(u"spinBox_thread_num")
        self.spinBox_thread_num.setMinimumSize(QSize(0, 40))
        self.spinBox_thread_num.setMinimum(1)
        self.spinBox_thread_num.setMaximum(10)

        self.gridLayout.addWidget(self.spinBox_thread_num, 0, 2, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.pushButton_thread_num = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_thread_num.setObjectName(u"pushButton_thread_num")
        self.pushButton_thread_num.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.pushButton_thread_num, 0, 3, 1, 1)

        self.comboBox_output = ComboBox(self.scrollAreaWidgetContents)
        self.comboBox_output.addItem("")
        self.comboBox_output.addItem("")
        self.comboBox_output.setObjectName(u"comboBox_output")
        self.comboBox_output.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.comboBox_output, 4, 2, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 10, 0, 1, 1)

        self.spinBox_history = QSpinBox(self.scrollAreaWidgetContents)
        self.spinBox_history.setObjectName(u"spinBox_history")
        self.spinBox_history.setMinimumSize(QSize(0, 40))
        self.spinBox_history.setMinimum(5)
        self.spinBox_history.setMaximum(20)

        self.gridLayout.addWidget(self.spinBox_history, 7, 2, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.lineEdit_proxy = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_proxy.setObjectName(u"lineEdit_proxy")
        self.lineEdit_proxy.setMinimumSize(QSize(250, 40))

        self.gridLayout.addWidget(self.lineEdit_proxy, 2, 2, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.pushButton_proxy = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_proxy.setObjectName(u"pushButton_proxy")
        self.pushButton_proxy.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.pushButton_proxy, 2, 3, 1, 1)

        self.label_api = QLabel(self.scrollAreaWidgetContents)
        self.label_api.setObjectName(u"label_api")
        self.label_api.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_api, 3, 0, 1, 1)

        self.lineEdit_api = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_api.setObjectName(u"lineEdit_api")
        self.lineEdit_api.setMinimumSize(QSize(250, 40))

        self.gridLayout.addWidget(self.lineEdit_api, 3, 2, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.label_proxy = QLabel(self.scrollAreaWidgetContents)
        self.label_proxy.setObjectName(u"label_proxy")
        self.label_proxy.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_proxy, 2, 0, 1, 1)

        self.pushButton_output = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_output.setObjectName(u"pushButton_output")
        self.pushButton_output.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.pushButton_output, 4, 3, 1, 1)

        self.pushButton_api = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_api.setObjectName(u"pushButton_api")
        self.pushButton_api.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.pushButton_api, 3, 3, 1, 1)

        self.pushButton_input = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_input.setObjectName(u"pushButton_input")
        self.pushButton_input.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.pushButton_input, 5, 3, 1, 1)

        self.label_history = QLabel(self.scrollAreaWidgetContents)
        self.label_history.setObjectName(u"label_history")
        self.label_history.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_history, 7, 0, 1, 1)

        self.label_thread_num = QLabel(self.scrollAreaWidgetContents)
        self.label_thread_num.setObjectName(u"label_thread_num")
        self.label_thread_num.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_thread_num, 0, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 1, 1, 1)

        self.comboBox_input = ComboBox(self.scrollAreaWidgetContents)
        self.comboBox_input.addItem("")
        self.comboBox_input.addItem("")
        self.comboBox_input.setObjectName(u"comboBox_input")
        self.comboBox_input.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.comboBox_input, 5, 2, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.label_output = QLabel(self.scrollAreaWidgetContents)
        self.label_output.setObjectName(u"label_output")
        self.label_output.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_output, 4, 0, 1, 1)

        self.label_input = QLabel(self.scrollAreaWidgetContents)
        self.label_input.setObjectName(u"label_input")
        self.label_input.setStyleSheet(u"font: 14pt \"Microsoft YaHei UI\";")

        self.gridLayout.addWidget(self.label_input, 5, 0, 1, 1)


        self.horizontalLayout.addLayout(self.gridLayout)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(set_page)

        QMetaObject.connectSlotsByName(set_page)
    # setupUi

    def retranslateUi(self, set_page):
        set_page.setWindowTitle(QCoreApplication.translate("set_page", u"Form", None))
        self.pushButton_thread_num.setText(QCoreApplication.translate("set_page", u"\u786e\u5b9a", None))
        self.comboBox_output.setItemText(0, QCoreApplication.translate("set_page", u"\u56fe\u50cf\u4fe1\u606f", None))
        self.comboBox_output.setItemText(1, QCoreApplication.translate("set_page", u"\u6536\u85cf\u5939\u6570\u636e", None))

        self.lineEdit_proxy.setPlaceholderText(QCoreApplication.translate("set_page", u"127.0.0.1:8080", None))
        self.pushButton_proxy.setText(QCoreApplication.translate("set_page", u"\u9a8c\u8bc1", None))
        self.label_api.setText(QCoreApplication.translate("set_page", u"WallhaveAPI", None))
        self.lineEdit_api.setPlaceholderText(QCoreApplication.translate("set_page", u"\u586b\u5199API", None))
        self.label_proxy.setText(QCoreApplication.translate("set_page", u"\u4ee3\u7406\u8bbe\u7f6e", None))
        self.pushButton_output.setText(QCoreApplication.translate("set_page", u"\u5bfc\u51fa", None))
        self.pushButton_api.setText(QCoreApplication.translate("set_page", u"\u9a8c\u8bc1", None))
        self.pushButton_input.setText(QCoreApplication.translate("set_page", u"\u5bfc\u5165", None))
        self.label_history.setText(QCoreApplication.translate("set_page", u"\u5386\u53f2\u8bb0\u5f55\u6570\u91cf", None))
        self.label_thread_num.setText(QCoreApplication.translate("set_page", u"\u7ebf\u7a0b\u6570\u91cf", None))
        self.comboBox_input.setItemText(0, QCoreApplication.translate("set_page", u"\u56fe\u50cf\u4fe1\u606f", None))
        self.comboBox_input.setItemText(1, QCoreApplication.translate("set_page", u"\u6536\u85cf\u5939\u6570\u636e", None))

        self.label_output.setText(QCoreApplication.translate("set_page", u"\u5bfc\u51fa\u6570\u636e", None))
        self.label_input.setText(QCoreApplication.translate("set_page", u"\u5bfc\u5165\u6570\u636e", None))
    # retranslateUi

