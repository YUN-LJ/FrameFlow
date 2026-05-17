"""组合式部件"""
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt, QEvent, QTimer
from qfluentwidgets import (
    IndeterminateProgressRing, ProgressRing, TransparentToolButton
)


class CombinationIndeterminateProgressRing(IndeterminateProgressRing):
    """组合式进度进度环,传入父对象后将居中显示在父对象之上"""

    def __init__(self, parent=None, useAni=True):
        super().__init__(parent, useAni)
        self.__uiInit()
        if self.parent():
            self.parent().installEventFilter(self)

    def __uiInit(self):
        self.setStrokeWidth(4)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        # self.__progressRing.setCustomBarColor("#005a9e", "#0078d4")
        # self.__progressRing.setCustomBackgroundColor("#005a9e", "#0078d4")

    def eventFilter(self, obj, event):
        """事件过滤器"""
        # 监听父对象的移动和调整大小事件
        if obj == self.parent() and event.type() in [QEvent.Move, QEvent.Resize]:
            parent = self.parent()
            # 设置大小为父对象的0.8
            parent_size = parent.size()
            radius = min(int(parent_size.width() * 0.8), int(parent_size.height() * 0.8))
            self.setFixedSize(radius, radius)
            # 进度环居中
            x = (parent_size.width() - radius) // 2
            y = (parent_size.height() - radius) // 2
            self.move(x, y)

        return super().eventFilter(obj, event)


class CombinationProgressRing(ProgressRing):
    """组合式进度进度环,传入父对象后将居中显示在父对象之上"""

    def __init__(self, parent=None, useAni=True):
        super().__init__(parent, useAni)
        self.__uiInit()
        if self.parent():
            self.parent().installEventFilter(self)

    def __uiInit(self):
        self.setStrokeWidth(4)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        # self.__progressRing.setCustomBarColor("#005a9e", "#0078d4")
        # self.__progressRing.setCustomBackgroundColor("#005a9e", "#0078d4")

    def eventFilter(self, obj, event):
        """事件过滤器"""
        # 监听父对象的移动和调整大小事件
        if obj == self.parent() and event.type() in [QEvent.Move, QEvent.Resize]:
            parent = self.parent()
            # 设置大小为父对象的0.8
            parent_size = parent.size()
            radius = min(int(parent_size.width() * 0.8), int(parent_size.height() * 0.8))
            self.setTextVisible(radius >= 35)
            self.setFixedSize(radius, radius)
            # 进度环居中
            x = (parent_size.width() - radius) // 2
            y = (parent_size.height() - radius) // 2
            self.move(x, y)

        return super().eventFilter(obj, event)


class ProgressRingButton(TransparentToolButton):
    """带进度显示的按钮,构造函数与TransparentToolButton一致"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__progressRing = ProgressRing(parent=self)
        self.uiInit()

    def uiInit(self):
        self.__progressRing.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.__progressRing.setTextVisible(True)
        self.__progressRing.setStrokeWidth(4)
        # self.__progressRing.setCustomBarColor("#005a9e", "#0078d4")
        # self.__progressRing.setCustomBackgroundColor("#005a9e", "#0078d4")

    def setMinimum(self, value):
        self.__progressRing.setMinimum(value)

    def setMaximum(self, value):
        self.__progressRing.setMaximum(value)

    def setValue(self, value):
        self.__progressRing.setValue(value)

    def value(self):
        return self.__progressRing.value()

    def setTextVisible(self, value: bool):
        self.__progressRing.setTextVisible(value)

    def setStrokeWidth(self, width: int):
        self.__progressRing.setStrokeWidth(width)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # 进度环居中，大小为按钮的0.8
        btn_size = self.size()
        radius = min(int(btn_size.width() * 0.8), int(btn_size.height() * 0.8))
        self.__progressRing.setFixedSize(radius, radius)

        # 居中
        x = (btn_size.width() - radius) // 2
        y = (btn_size.height() - radius) // 2
        self.__progressRing.move(x, y)


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    win = QWidget()
    btn = ProgressRingButton()
    btn.setFixedSize(45, 45)
    progress = CombinationProgressRing(btn)

    layout = QHBoxLayout(win)
    layout.addWidget(btn)
    win.show()

    progress_timer = QTimer()
    progress_timer.timeout.connect(lambda: progress.setValue(progress.value() + 1))
    progress_timer.start(100)
    app.exec()
