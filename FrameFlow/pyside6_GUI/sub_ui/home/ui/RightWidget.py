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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QStackedWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_RightWidget(object):
    def setupUi(self, RightWidget):
        if not RightWidget.objectName():
            RightWidget.setObjectName(u"RightWidget")
        RightWidget.resize(517, 300)
        self.horizontalLayout = QHBoxLayout(RightWidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(RightWidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.download_page = QWidget()
        self.download_page.setObjectName(u"download_page")
        self.horizontalLayout_2 = QHBoxLayout(self.download_page)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(self.download_page)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 515, 298))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_2)

        self.pushButton_choice_all_1 = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_choice_all_1.setObjectName(u"pushButton_choice_all_1")
        self.pushButton_choice_all_1.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_5.addWidget(self.pushButton_choice_all_1)

        self.pushButton_del = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_del.setObjectName(u"pushButton_del")
        self.pushButton_del.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_5.addWidget(self.pushButton_del)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.tableWidget_download = QTableWidget(self.scrollAreaWidgetContents)
        if (self.tableWidget_download.columnCount() < 3):
            self.tableWidget_download.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget_download.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget_download.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget_download.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.tableWidget_download.setObjectName(u"tableWidget_download")

        self.verticalLayout.addWidget(self.tableWidget_download)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout_2.addWidget(self.scrollArea)

        self.stackedWidget.addWidget(self.download_page)
        self.like_page = QWidget()
        self.like_page.setObjectName(u"like_page")
        self.horizontalLayout_3 = QHBoxLayout(self.like_page)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_2 = QScrollArea(self.like_page)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 172, 98))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.pushButton_choice_all_2 = QPushButton(self.scrollAreaWidgetContents_2)
        self.pushButton_choice_all_2.setObjectName(u"pushButton_choice_all_2")
        self.pushButton_choice_all_2.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_4.addWidget(self.pushButton_choice_all_2)

        self.pushButton_updata = QPushButton(self.scrollAreaWidgetContents_2)
        self.pushButton_updata.setObjectName(u"pushButton_updata")
        self.pushButton_updata.setMinimumSize(QSize(0, 40))

        self.horizontalLayout_4.addWidget(self.pushButton_updata)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.tableWidget_like = QTableWidget(self.scrollAreaWidgetContents_2)
        if (self.tableWidget_like.columnCount() < 6):
            self.tableWidget_like.setColumnCount(6)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget_like.setHorizontalHeaderItem(0, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget_like.setHorizontalHeaderItem(1, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableWidget_like.setHorizontalHeaderItem(2, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableWidget_like.setHorizontalHeaderItem(3, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableWidget_like.setHorizontalHeaderItem(4, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableWidget_like.setHorizontalHeaderItem(5, __qtablewidgetitem8)
        self.tableWidget_like.setObjectName(u"tableWidget_like")

        self.verticalLayout_2.addWidget(self.tableWidget_like)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)

        self.horizontalLayout_3.addWidget(self.scrollArea_2)

        self.stackedWidget.addWidget(self.like_page)

        self.horizontalLayout.addWidget(self.stackedWidget)


        self.retranslateUi(RightWidget)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(RightWidget)
    # setupUi

    def retranslateUi(self, RightWidget):
        RightWidget.setWindowTitle(QCoreApplication.translate("RightWidget", u"RigetWidget", None))
        self.pushButton_choice_all_1.setText(QCoreApplication.translate("RightWidget", u"\u5168\u9009", None))
        self.pushButton_del.setText(QCoreApplication.translate("RightWidget", u"\u5220\u9664\u6240\u9009\u9879", None))
        ___qtablewidgetitem = self.tableWidget_download.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("RightWidget", u"\u56fe\u50cfID", None));
        ___qtablewidgetitem1 = self.tableWidget_download.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("RightWidget", u"\u4e0b\u8f7d\u8fdb\u5ea6", None));
        ___qtablewidgetitem2 = self.tableWidget_download.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("RightWidget", u"\u64cd\u4f5c", None));
        self.pushButton_choice_all_2.setText(QCoreApplication.translate("RightWidget", u"\u5168\u9009", None))
        self.pushButton_updata.setText(QCoreApplication.translate("RightWidget", u"\u66f4\u65b0\u6240\u9009\u9879", None))
        ___qtablewidgetitem3 = self.tableWidget_like.horizontalHeaderItem(0)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("RightWidget", u"\u5173\u952e\u8bcd", None));
        ___qtablewidgetitem4 = self.tableWidget_like.horizontalHeaderItem(1)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("RightWidget", u"\u8fdb\u5ea6", None));
        ___qtablewidgetitem5 = self.tableWidget_like.horizontalHeaderItem(2)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("RightWidget", u"\u603b\u9875\u6570", None));
        ___qtablewidgetitem6 = self.tableWidget_like.horizontalHeaderItem(3)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("RightWidget", u"\u603b\u6570", None));
        ___qtablewidgetitem7 = self.tableWidget_like.horizontalHeaderItem(4)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("RightWidget", u"\u6700\u65b0\u65e5\u671f", None));
        ___qtablewidgetitem8 = self.tableWidget_like.horizontalHeaderItem(5)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("RightWidget", u"\u4e0a\u6b21\u66f4\u65b0", None));
    # retranslateUi

