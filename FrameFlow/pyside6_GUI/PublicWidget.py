from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QCheckBox
from PySide6.QtCore import Signal
from Fun.GUI_Qt.PySide6Mod import ImageWidget


class GroupBoxCell(QGroupBox):
    """带标题的单元格组件"""
    StateChange = Signal(bool)  # 内部的checkBox状态改变时

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent  # 父对象
        self.layout = QVBoxLayout(self)
        self.layout_title = QHBoxLayout(self)
        self.image_widget = ImageWidget()
        self.checkBox = QCheckBox()
        self.uiInit()
        self.bind()

    def uiInit(self):
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout_title.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout_title.setSpacing(0)
        self.layout.addLayout(self.layout_title)
        self.layout_title.addWidget(self.checkBox)
        self.layout.addWidget(self.image_widget)

    def bind(self):
        self.checkBox.stateChanged.connect(self.StateChange.emit)

    def getState(self) -> bool:
        return self.checkBox.isChecked()

    def setText(self, text: str):
        self.checkBox.setText(text)

    def setState(self, state: bool):
        self.checkBox.setChecked(state)

    def setImage(self, image):
        if image is not None:
            self.image_widget.set_image(image)

    def addWidget(self, widget):
        self.layout_title.addWidget(widget)

    def setColor(self, color: str):
        self.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {color};
                border-radius: 5px;
                margin-top: 3px;
                font-size: 12px;
                }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: {color};
                }}
                """
                           )


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    w = GroupBoxCell()
    w.show()
    app.exec()
