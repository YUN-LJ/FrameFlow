# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ImageInfo.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QSizePolicy, QSpacerItem,
                               QVBoxLayout, QWidget)

from qfluentwidgets.components.widgets import BodyLabel


class Ui_Image_info(object):
    def setupUi(self, Image_info):
        if not Image_info.objectName():
            Image_info.setObjectName(u"Image_info")
        Image_info.resize(400, 300)
        self.verticalLayout = QVBoxLayout(Image_info)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_info = QGridLayout()
        self.gridLayout_info.setObjectName(u"gridLayout_info")
        self.label_local_path_value = BodyLabel(Image_info)
        self.label_local_path_value.setObjectName(u"label_local_path_value")
        self.label_local_path_value.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")
        self.label_local_path_value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByKeyboard | Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_info.addWidget(self.label_local_path_value, 5, 1, 1, 1)

        self.label_purity_value = BodyLabel(Image_info)
        self.label_purity_value.setObjectName(u"label_purity_value")
        self.label_purity_value.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")
        self.label_purity_value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByKeyboard | Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_info.addWidget(self.label_purity_value, 2, 1, 1, 1)

        self.label_category_value = BodyLabel(Image_info)
        self.label_category_value.setObjectName(u"label_category_value")
        self.label_category_value.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")
        self.label_category_value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByKeyboard | Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_info.addWidget(self.label_category_value, 1, 1, 1, 1)

        self.label_file_size_value = BodyLabel(Image_info)
        self.label_file_size_value.setObjectName(u"label_file_size_value")
        self.label_file_size_value.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")
        self.label_file_size_value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByKeyboard | Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_info.addWidget(self.label_file_size_value, 4, 1, 1, 1)

        self.label_id_value = BodyLabel(Image_info)
        self.label_id_value.setObjectName(u"label_id_value")
        self.label_id_value.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")
        self.label_id_value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByKeyboard | Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_info.addWidget(self.label_id_value, 0, 1, 1, 1)

        self.label_local_path = BodyLabel(Image_info)
        self.label_local_path.setObjectName(u"label_local_path")
        self.label_local_path.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout_info.addWidget(self.label_local_path, 5, 0, 1, 1)

        self.label_remote_path_value = BodyLabel(Image_info)
        self.label_remote_path_value.setObjectName(u"label_remote_path_value")
        self.label_remote_path_value.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")
        self.label_remote_path_value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByKeyboard | Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_info.addWidget(self.label_remote_path_value, 6, 1, 1, 1)

        self.label_category = BodyLabel(Image_info)
        self.label_category.setObjectName(u"label_category")
        self.label_category.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout_info.addWidget(self.label_category, 1, 0, 1, 1)

        self.label_data_value = BodyLabel(Image_info)
        self.label_data_value.setObjectName(u"label_data_value")
        self.label_data_value.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")
        self.label_data_value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByKeyboard | Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_info.addWidget(self.label_data_value, 3, 1, 1, 1)

        self.label_file_size = BodyLabel(Image_info)
        self.label_file_size.setObjectName(u"label_file_size")
        self.label_file_size.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout_info.addWidget(self.label_file_size, 4, 0, 1, 1)

        self.label_id = BodyLabel(Image_info)
        self.label_id.setObjectName(u"label_id")
        self.label_id.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout_info.addWidget(self.label_id, 0, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_info.addItem(self.horizontalSpacer_2, 0, 2, 1, 1)

        self.label_remote_path = BodyLabel(Image_info)
        self.label_remote_path.setObjectName(u"label_remote_path")
        self.label_remote_path.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout_info.addWidget(self.label_remote_path, 6, 0, 1, 1)

        self.label_data = BodyLabel(Image_info)
        self.label_data.setObjectName(u"label_data")
        self.label_data.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout_info.addWidget(self.label_data, 3, 0, 1, 1)

        self.label_purity = BodyLabel(Image_info)
        self.label_purity.setObjectName(u"label_purity")
        self.label_purity.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout_info.addWidget(self.label_purity, 2, 0, 1, 1)

        self.label_tags = BodyLabel(Image_info)
        self.label_tags.setObjectName(u"label_tags")
        self.label_tags.setStyleSheet(u"font: 12pt \"Microsoft YaHei UI\";")

        self.gridLayout_info.addWidget(self.label_tags, 7, 0, 1, 1)

        self.verticalLayout.addLayout(self.gridLayout_info)

        self.gridLayout_tags = QGridLayout()
        self.gridLayout_tags.setObjectName(u"gridLayout_tags")

        self.verticalLayout.addLayout(self.gridLayout_tags)

        self.verticalLayout.setStretch(0, 1)

        Ui_Image_info.retranslateUi(self, Image_info)

        QMetaObject.connectSlotsByName(Image_info)

    # setupUi

    def retranslateUi(self, Image_info):
        Image_info.setWindowTitle(QCoreApplication.translate("Image_info", u"Form", None))
        self.label_local_path_value.setText("")
        self.label_purity_value.setText("")
        self.label_category_value.setText("")
        self.label_file_size_value.setText("")
        self.label_id_value.setText("")
        self.label_local_path.setText(QCoreApplication.translate("Image_info", u"\u672c\u5730\u8def\u5f84\uff1a", None))
        self.label_remote_path_value.setText("")
        self.label_category.setText(QCoreApplication.translate("Image_info", u"\u5206\u7c7b\uff1a", None))
        self.label_data_value.setText("")
        self.label_file_size.setText(QCoreApplication.translate("Image_info", u"\u6587\u4ef6\u5927\u5c0f:", None))
        self.label_id.setText(QCoreApplication.translate("Image_info", u"\u56fe\u50cfID\uff1a", None))
        self.label_remote_path.setText(
            QCoreApplication.translate("Image_info", u"\u8fdc\u7a0b\u8def\u5f84\uff1a", None))
        self.label_data.setText(QCoreApplication.translate("Image_info", u"\u65e5\u671f\uff1a", None))
        self.label_purity.setText(QCoreApplication.translate("Image_info", u"\u5206\u7ea7\uff1a", None))
        self.label_tags.setText(QCoreApplication.translate("Image_info", u"\u6807\u7b7e\u4fe1\u606f:", None))
    # retranslateUi
