# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'table.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QSize)
from PySide6.QtWidgets import (QTableWidgetItem,
                               QVBoxLayout)

from qfluentwidgets.components.widgets.table_view import TableWidget

class Ui_widget_table(object):
    def setupUi(self, widget_table):
        if not widget_table.objectName():
            widget_table.setObjectName(u"widget_table")
        widget_table.resize(400, 300)
        self.verticalLayout = QVBoxLayout(widget_table)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.tableWidget_dirs_path = TableWidget(widget_table)
        if (self.tableWidget_dirs_path.columnCount() < 3):
            self.tableWidget_dirs_path.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget_dirs_path.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget_dirs_path.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget_dirs_path.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.tableWidget_dirs_path.setObjectName(u"tableWidget_dirs_path")
        self.tableWidget_dirs_path.setMinimumSize(QSize(400, 80))
        self.tableWidget_dirs_path.setStyleSheet(u"QTableWidget {\n"
"    gridline-color: #eee;\n"
"    selection-background-color: #e3f2fd;\n"
"    selection-color: #333; /* \u9009\u4e2d\u5355\u5143\u683c\u7684\u5b57\u4f53\u989c\u8272 */\n"
"    color: #555; /* \u9ed8\u8ba4\u5b57\u4f53\u989c\u8272\uff08\u672a\u9009\u4e2d\u72b6\u6001\uff09 */\n"
"    font-family: \"Microsoft YaHei\", sans-serif; /* \u53ef\u9009\uff1a\u8bbe\u7f6e\u5b57\u4f53 */\n"
"    font-size: 12px; /* \u53ef\u9009\uff1a\u8bbe\u7f6e\u5b57\u4f53\u5927\u5c0f */\n"
"}\n"
"QHeaderView::section {\n"
"	background-color: rgb(250,248,252);\n"
"	color: black;\n"
"	font-weight:bold;\n"
"	border: none;\n"
"	padding: 5px;\n"
"}")

        self.verticalLayout.addWidget(self.tableWidget_dirs_path)


        self.retranslateUi(widget_table)

        QMetaObject.connectSlotsByName(widget_table)
    # setupUi

    def retranslateUi(self, widget_table):
        widget_table.setWindowTitle(QCoreApplication.translate("widget_table", u"Form", None))
        ___qtablewidgetitem = self.tableWidget_dirs_path.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("widget_table", u"\u6587\u4ef6\u5939\u8def\u5f84", None));
        ___qtablewidgetitem1 = self.tableWidget_dirs_path.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("widget_table", u"\u6dfb\u52a0\u65f6\u95f4", None));
        ___qtablewidgetitem2 = self.tableWidget_dirs_path.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("widget_table", u"\u64cd\u4f5c", None));
    # retranslateUi

