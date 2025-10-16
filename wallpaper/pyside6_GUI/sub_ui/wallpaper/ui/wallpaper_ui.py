# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'wallpaper_ui.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QScrollArea,
    QSizePolicy, QSpacerItem, QTableWidgetItem, QVBoxLayout,
    QWidget)

from qfluentwidgets.components.widgets import PrimaryPushButton
from qfluentwidgets.components.widgets.table_view import TableWidget


class Ui_wallpaper(object):
    def setupUi(self, wallpaper):
        if not wallpaper.objectName():
            wallpaper.setObjectName(u"wallpaper")
        wallpaper.resize(800, 500)
        self.verticalLayout = QVBoxLayout(wallpaper)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tableWidget_dirs_path = TableWidget(wallpaper)
        if (self.tableWidget_dirs_path.columnCount() < 3):
            self.tableWidget_dirs_path.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget_dirs_path.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget_dirs_path.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget_dirs_path.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.tableWidget_dirs_path.setObjectName(u"tableWidget_dirs_path")
        self.tableWidget_dirs_path.setStyleSheet(u"QTableWidget {\n"
"    gridline-color: #eee;\n"
"    selection-background-color: #e3f2fd;\n"
"    selection-color: #333; /* \u9009\u4e2d\u5355\u5143\u683c\u7684\u5b57\u4f53\u989c\u8272 */\n"
"    color: #555; /* \u9ed8\u8ba4\u5b57\u4f53\u989c\u8272\uff08\u672a\u9009\u4e2d\u72b6\u6001\uff09 */\n"
"    font-family: \"Microsoft YaHei\", sans-serif; /* \u53ef\u9009\uff1a\u8bbe\u7f6e\u5b57\u4f53 */\n"
"    font-size: 12px; /* \u53ef\u9009\uff1a\u8bbe\u7f6e\u5b57\u4f53\u5927\u5c0f */\n"
"}\n"
"QHeaderView::section {\n"
"	background-color: rgb(217, 217, 217);\n"
"	color: black;\n"
"	font-weight:bold;\n"
"	border: none;\n"
"	padding: 5px;\n"
"}")

        self.horizontalLayout.addWidget(self.tableWidget_dirs_path)

        self.scrollArea_options = QScrollArea(wallpaper)
        self.scrollArea_options.setObjectName(u"scrollArea_options")
        self.scrollArea_options.setMinimumSize(QSize(120, 0))
        self.scrollArea_options.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 118, 496))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.pushButton_add = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_add.setObjectName(u"pushButton_add")
        self.pushButton_add.setMinimumSize(QSize(0, 40))

        self.verticalLayout_2.addWidget(self.pushButton_add)

        self.pushButton_del = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_del.setObjectName(u"pushButton_del")
        self.pushButton_del.setMinimumSize(QSize(0, 40))

        self.verticalLayout_2.addWidget(self.pushButton_del)

        self.pushButton_pause = PrimaryPushButton(self.scrollAreaWidgetContents)
        self.pushButton_pause.setObjectName(u"pushButton_pause")
        self.pushButton_pause.setMinimumSize(QSize(0, 40))

        self.verticalLayout_2.addWidget(self.pushButton_pause)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.scrollArea_options.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout.addWidget(self.scrollArea_options)

        self.horizontalLayout.setStretch(0, 6)
        self.horizontalLayout.setStretch(1, 1)

        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(wallpaper)

        QMetaObject.connectSlotsByName(wallpaper)
    # setupUi

    def retranslateUi(self, wallpaper):
        wallpaper.setWindowTitle(QCoreApplication.translate("wallpaper", u"wallpaper", None))
        ___qtablewidgetitem = self.tableWidget_dirs_path.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("wallpaper", u"\u6587\u4ef6\u5939\u8def\u5f84", None));
        ___qtablewidgetitem1 = self.tableWidget_dirs_path.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("wallpaper", u"\u6dfb\u52a0\u65f6\u95f4", None));
        ___qtablewidgetitem2 = self.tableWidget_dirs_path.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("wallpaper", u"\u64cd\u4f5c", None));
        self.pushButton_add.setText(QCoreApplication.translate("wallpaper", u"\u65b0\u589e\u76ee\u5f55", None))
        self.pushButton_del.setText(QCoreApplication.translate("wallpaper", u"\u5220\u9664\u76ee\u5f55", None))
        self.pushButton_pause.setText(QCoreApplication.translate("wallpaper", u"\u6682\u505c\u64ad\u653e", None))
    # retranslateUi

