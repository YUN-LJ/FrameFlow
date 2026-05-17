"""加载弹出类"""
# PySide6库
from PySide6.QtCore import QTimer, QObject
from PySide6.QtWidgets import QHBoxLayout, QProgressBar
# 风格组件
from qfluentwidgets import (
    IndeterminateProgressRing, TitleLabel,
    ProgressRing, IndeterminateProgressBar,
    MessageBoxBase
)


class LoadDialogBase(MessageBoxBase):
    """加载对话框基类"""

    def __init__(self, text, parent):
        super().__init__(parent)
        self.scale = 0.5
        self.resize_timer = QTimer(self)
        self.resize_timer.timeout.connect(self.resize_event)
        self.resize_timer.start(10)
        self.uiInit(text)

    def uiInit(self, text):
        """添加基本控件"""
        self.label = TitleLabel(text)
        self.label.setWordWrap(True)  # 标题自动换行
        self.viewLayout.addWidget(self.label)
        self.progress_layout = QHBoxLayout(self)
        self.viewLayout.addLayout(self.progress_layout)
        # 隐藏确定
        self.hideYesButton()
        # self.hideCancelButton()

    def setText(self, text):
        self.label.setText(text)

    def resize_event(self):
        """自适应调整窗口大小"""
        w = self.parent().width()
        h = self.parent().height()
        self.widget.setMinimumWidth(w * self.scale)
        self.widget.setMinimumHeight(h * self.scale)

    def closeEvent(self, event):
        """关闭时清理资源"""
        self.deleteLater()
        super().closeEvent(event)

    def accept(self):
        try:
            self.deleteLater()
        except RuntimeError:
            pass
        super().accept()

    def reject(self):
        try:
            self.deleteLater()
        except RuntimeError:
            pass
        super().reject()

    def deleteLater(self):
        """确保资源删除干净"""
        for object in self.findChildren(QObject):
            object.deleteLater()
        super().deleteLater()


class LoadRingDialog(LoadDialogBase):
    """加载环对话框"""

    def __init__(self, text, parent, use_indeter=False):
        """
        :param use_indeter:使用无进度 进度环
        """
        self.progress = IndeterminateProgressRing() if use_indeter else ProgressRing()
        super().__init__(text, parent)

    def uiInit(self, text):
        super().uiInit(text)
        # 添加环形进度条
        if isinstance(self.progress, ProgressRing):
            self.progress.setTextVisible(True)
        self.progress.setFixedSize(50, 50)
        self.progress.setStrokeWidth(4)
        self.progress_layout.addWidget(self.progress)


class LoadBarDialog(LoadDialogBase):
    """加载环对话框"""

    def __init__(self, text, parent, use_indeter=False):
        """
        :param use_indeter:使用无进度 进度环
        """
        self.progress = IndeterminateProgressBar() if use_indeter else QProgressBar()
        super().__init__(text, parent)

    def uiInit(self, text):
        super().uiInit(text)
        # 添加环形进度条
        if isinstance(self.progress, QProgressBar):
            self.progress.setTextVisible(True)
        self.progress_layout.addWidget(self.progress)
