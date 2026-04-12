# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'RightWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QScrollArea, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from qfluentwidgets.components.widgets import (PrimaryToolButton, SwitchButton)

class Ui_rightwidget(object):
    def setupUi(self, rightwidget):
        if not rightwidget.objectName():
            rightwidget.setObjectName(u"rightwidget")
        rightwidget.resize(572, 404)
        self.verticalLayout = QVBoxLayout(rightwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(rightwidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 570, 402))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.groupBox_image = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_image.setObjectName(u"groupBox_image")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_image)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.checkBox = SwitchButton(self.groupBox_image)
        self.checkBox.setObjectName(u"checkBox")

        self.horizontalLayout_2.addWidget(self.checkBox)

        self.checkBox_zoom = SwitchButton(self.groupBox_image)
        self.checkBox_zoom.setObjectName(u"checkBox_zoom")

        self.horizontalLayout_2.addWidget(self.checkBox_zoom)

        self.pushButton_copy = PrimaryToolButton(self.groupBox_image)
        self.pushButton_copy.setObjectName(u"pushButton_copy")
        self.pushButton_copy.setMinimumSize(QSize(30, 30))
        self.pushButton_copy.setMaximumSize(QSize(30, 30))

        self.horizontalLayout_2.addWidget(self.pushButton_copy)

        self.pushButton_open = PrimaryToolButton(self.groupBox_image)
        self.pushButton_open.setObjectName(u"pushButton_open")
        self.pushButton_open.setMinimumSize(QSize(30, 30))
        self.pushButton_open.setMaximumSize(QSize(30, 30))

        self.horizontalLayout_2.addWidget(self.pushButton_open)

        self.pushButton_full = PrimaryToolButton(self.groupBox_image)
        self.pushButton_full.setObjectName(u"pushButton_full")
        self.pushButton_full.setMinimumSize(QSize(30, 30))
        self.pushButton_full.setMaximumSize(QSize(30, 30))

        self.horizontalLayout_2.addWidget(self.pushButton_full)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout_4.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.verticalLayout_4.setStretch(1, 3)

        self.verticalLayout_2.addWidget(self.groupBox_image)

        self.groupBox_info = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_info.setObjectName(u"groupBox_info")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_info)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.gridLayout_info = QGridLayout()
        self.gridLayout_info.setObjectName(u"gridLayout_info")
        self.label_local_path_value = QLabel(self.groupBox_info)
        self.label_local_path_value.setObjectName(u"label_local_path_value")
        self.label_local_path_value.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")
        self.label_local_path_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_info.addWidget(self.label_local_path_value, 5, 1, 1, 1)

        self.label_purity_value = QLabel(self.groupBox_info)
        self.label_purity_value.setObjectName(u"label_purity_value")
        self.label_purity_value.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")
        self.label_purity_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_info.addWidget(self.label_purity_value, 2, 1, 1, 1)

        self.label_category_value = QLabel(self.groupBox_info)
        self.label_category_value.setObjectName(u"label_category_value")
        self.label_category_value.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")
        self.label_category_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_info.addWidget(self.label_category_value, 1, 1, 1, 1)

        self.label_file_size_value = QLabel(self.groupBox_info)
        self.label_file_size_value.setObjectName(u"label_file_size_value")
        self.label_file_size_value.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")
        self.label_file_size_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_info.addWidget(self.label_file_size_value, 4, 1, 1, 1)

        self.label_id_value = QLabel(self.groupBox_info)
        self.label_id_value.setObjectName(u"label_id_value")
        self.label_id_value.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")
        self.label_id_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_info.addWidget(self.label_id_value, 0, 1, 1, 1)

        self.label_local_path = QLabel(self.groupBox_info)
        self.label_local_path.setObjectName(u"label_local_path")
        self.label_local_path.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout_info.addWidget(self.label_local_path, 5, 0, 1, 1)

        self.label_remote_path_value = QLabel(self.groupBox_info)
        self.label_remote_path_value.setObjectName(u"label_remote_path_value")
        self.label_remote_path_value.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")
        self.label_remote_path_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_info.addWidget(self.label_remote_path_value, 6, 1, 1, 1)

        self.label_category = QLabel(self.groupBox_info)
        self.label_category.setObjectName(u"label_category")
        self.label_category.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout_info.addWidget(self.label_category, 1, 0, 1, 1)

        self.label_data_value = QLabel(self.groupBox_info)
        self.label_data_value.setObjectName(u"label_data_value")
        self.label_data_value.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")
        self.label_data_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_info.addWidget(self.label_data_value, 3, 1, 1, 1)

        self.label_file_size = QLabel(self.groupBox_info)
        self.label_file_size.setObjectName(u"label_file_size")
        self.label_file_size.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout_info.addWidget(self.label_file_size, 4, 0, 1, 1)

        self.label_id = QLabel(self.groupBox_info)
        self.label_id.setObjectName(u"label_id")
        self.label_id.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout_info.addWidget(self.label_id, 0, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_info.addItem(self.horizontalSpacer_2, 0, 2, 1, 1)

        self.label_remote_path = QLabel(self.groupBox_info)
        self.label_remote_path.setObjectName(u"label_remote_path")
        self.label_remote_path.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout_info.addWidget(self.label_remote_path, 6, 0, 1, 1)

        self.label_data = QLabel(self.groupBox_info)
        self.label_data.setObjectName(u"label_data")
        self.label_data.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout_info.addWidget(self.label_data, 3, 0, 1, 1)

        self.label_purity = QLabel(self.groupBox_info)
        self.label_purity.setObjectName(u"label_purity")
        self.label_purity.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout_info.addWidget(self.label_purity, 2, 0, 1, 1)

        self.label_tags = QLabel(self.groupBox_info)
        self.label_tags.setObjectName(u"label_tags")
        self.label_tags.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout_info.addWidget(self.label_tags, 7, 0, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_info)

        self.gridLayout_tags = QGridLayout()
        self.gridLayout_tags.setObjectName(u"gridLayout_tags")

        self.verticalLayout_3.addLayout(self.gridLayout_tags)


        self.verticalLayout_2.addWidget(self.groupBox_info)

        self.verticalLayout_2.setStretch(0, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(rightwidget)

        QMetaObject.connectSlotsByName(rightwidget)
    # setupUi

    def retranslateUi(self, rightwidget):
        rightwidget.setWindowTitle(QCoreApplication.translate("rightwidget", u"Form", None))
        self.groupBox_image.setTitle(QCoreApplication.translate("rightwidget", u"\u56fe\u50cf\u9884\u89c8:", None))
        self.checkBox.setText(QCoreApplication.translate("rightwidget", u"\u81ea\u52a8\u6682\u505c", None))
        self.checkBox_zoom.setText(QCoreApplication.translate("rightwidget", u"\u542f\u7528\u7f29\u653e", None))
        self.pushButton_copy.setText("")
        self.pushButton_open.setText("")
        self.pushButton_full.setText("")
        self.groupBox_info.setTitle(QCoreApplication.translate("rightwidget", u"\u56fe\u50cf\u4fe1\u606f", None))
        self.label_local_path_value.setText("")
        self.label_purity_value.setText("")
        self.label_category_value.setText("")
        self.label_file_size_value.setText("")
        self.label_id_value.setText("")
        self.label_local_path.setText(QCoreApplication.translate("rightwidget", u"\u672c\u5730\u8def\u5f84\uff1a", None))
        self.label_remote_path_value.setText("")
        self.label_category.setText(QCoreApplication.translate("rightwidget", u"\u5206\u7c7b\uff1a", None))
        self.label_data_value.setText("")
        self.label_file_size.setText(QCoreApplication.translate("rightwidget", u"\u6587\u4ef6\u5927\u5c0f:", None))
        self.label_id.setText(QCoreApplication.translate("rightwidget", u"\u56fe\u50cfID\uff1a", None))
        self.label_remote_path.setText(QCoreApplication.translate("rightwidget", u"\u8fdc\u7a0b\u8def\u5f84\uff1a", None))
        self.label_data.setText(QCoreApplication.translate("rightwidget", u"\u65e5\u671f\uff1a", None))
        self.label_purity.setText(QCoreApplication.translate("rightwidget", u"\u5206\u7ea7\uff1a", None))
        self.label_tags.setText(QCoreApplication.translate("rightwidget", u"\u6807\u7b7e\u4fe1\u606f:", None))
    # retranslateUi

