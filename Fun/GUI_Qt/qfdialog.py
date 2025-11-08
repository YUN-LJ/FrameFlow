"""带美化封装的弹窗类"""
from PySide6.QtWidgets import (QWidget, QLineEdit,
                               QCheckBox, QRadioButton)
from qfluentwidgets.components.dialog_box import MessageBoxBase
from qfluentwidgets.components.widgets import (
    InfoBarIcon, TeachingTip, TeachingTipTailPosition, ComboBox)


class DialogBase(MessageBoxBase):
    """
    该类是一个弹窗的基类,自定义弹窗时
    """

    def __init__(self, ui, parent=None):
        """
        :param ui: ui文件转py文件
        """
        self.__parent = parent
        super().__init__(self.__parent)
        widget = QWidget()
        self.ui = ui()
        self.ui.setupUi(widget)
        self.viewLayout.addWidget(widget)

    def data_init(self, data):
        """传入数据时的初始化"""

    def append_data(self):
        """添加数据的方法"""

    def update_data(self):
        """修改数据的方法"""

    def verify_data(self):
        """数据校验的方法"""

    def get_all_data(self):
        """获取全部数据的方法
        """

    def accept(self):
        """点击OK时的方法"""
        try:
            self.verify_data()
            super().accept()
        except Exception as e:
            TeachingTip.create(
                target=self.yesButton,
                icon=InfoBarIcon.WARNING,
                title='温馨提示',
                content=str(e),
                isClosable=True,
                tailPosition=TeachingTipTailPosition.BOTTOM,
                duration=2000,
                parent=self.__parent)
