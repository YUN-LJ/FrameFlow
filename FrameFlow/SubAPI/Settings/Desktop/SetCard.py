"""设置类卡片"""
from PySide6.QtCore import Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLayout

from qfluentwidgets import (
    CardWidget, IconWidget, FluentIcon as FIF, SubtitleLabel, SwitchButton,
    TransparentToolButton, LineEdit, CaptionLabel, PrimaryToolButton,
    SpinBox, ComboBox
)
from typing import Optional, Callable

from Fun.QtWidget import info_bar_decorator, debouncer_timer, get_exist_files, get_exist_dir


class CardBase(CardWidget):
    """设置卡片,内部包含一个垂直布局(主)和一个水平布局(标题栏)"""

    def __init__(self, text=None, parent=None):
        super().__init__(parent)
        self._uiInit()
        if text:
            self.setTitle(text)

    def _uiInit(self):
        # 布局
        self.view_layout = QVBoxLayout(self)  # 主布局
        self.view_layout.setContentsMargins(0, 0, 0, 0)

        self._title_layout = QHBoxLayout(self)  # 标题布局
        self._title_layout.setContentsMargins(20, 15, 20, 15)  # 左，上，右，下

        self.view_layout.addLayout(self._title_layout)

        self.setLayout(self.view_layout)

        # 添加标题
        self._title = SubtitleLabel(self)

        self._title_layout.addWidget(self._title)
        self._title_layout.addStretch()

    def setTitle(self, text):
        """设置标题"""
        self._title.setText(text)

    def setLeftIcon(self, icon):
        """设置最左侧图标"""
        item = self._title_layout.itemAt(0)
        if isinstance(item, IconWidget):
            item.setIcon(icon)
        else:
            icon_widget = IconWidget(icon)
            icon_widget.setFixedSize(20, 20)
            self._title_layout.insertWidget(0, icon_widget)

    def setRightWidget(self, widget: QWidget):
        """设置最右侧组件,推荐设置widget.setFixedSize(20, 20),否则可能不显示"""
        item = self._title_layout.itemAt(self._title_layout.count() - 1)
        if isinstance(item, QWidget):
            self._title_layout.removeWidget(item)
            item.deleteLater()
        self._title_layout.addWidget(widget)

    def addTitleWidget(self, widget: QWidget):
        """添加组件"""
        self._title_layout.addWidget(widget)


class SwitchCard(CardBase):
    """切换类设置卡片"""
    checkedChanged = Signal(bool)

    def __init__(self, text=None, parent=None):
        super().__init__(text, parent)
        self.switch_button = SwitchButton(self)
        self.setOnText('开启')
        self.setOffText('关闭')

        self.switch_button.checkedChanged.connect(self.checkedChanged.emit)
        self.setRightWidget(self.switch_button)

    def setOffText(self, text):
        self.switch_button.setOffText(text)

    def setOnText(self, text):
        self.switch_button.setOnText(text)

    def setChecked(self, checked: bool):
        self.switch_button.setChecked(checked)


class MenuCard(CardBase):
    """菜单类设置卡片"""

    def __init__(self, text=None, parent=None):
        super().__init__(text, parent)
        self.__uiInit()

    def _addRightWidget(self):
        """添加右侧图标透明按钮"""
        self._icon_widget = TransparentToolButton(self)
        self._icon_widget.setFixedSize(35, 35)
        self._icon_widget.clicked.connect(
            lambda:
            self.hideContent()
            if self._content_widget.isVisible() else
            self.showContent()
        )

        self.setRightWidget(self._icon_widget)

    def __uiInit(self):
        # 添加右侧图标组件
        self._addRightWidget()

        # 添加内容组件
        self._content_widget = QWidget(self)
        self._content_widget_layout = QVBoxLayout(self._content_widget)
        self._content_widget_layout.setContentsMargins(20, 15, 20, 15)  # 左，上，右，下

        self.view_layout.addWidget(self._content_widget)

        # 创建动画对象 第一参数为对象,第二参数为更改对象的属性名称,这段代码的意思为不断更改self._content_widget对象的maximumHeight属性参数
        self._animation = QPropertyAnimation(self._content_widget, b"maximumHeight")
        self._animation.setDuration(300)  # 动画时长300ms
        self._animation.setEasingCurve(QEasingCurve.Type.InOutCubic)  # 缓动曲线

        self.hideContent(animation=False)

    def enableCliked(self, enable: bool):
        """设置点击事件是否生效"""
        if enable:
            self.clicked.connect(
                lambda:
                self.hideContent()
                if self._content_widget.isVisible() else
                self.showContent()
            )
        else:
            self.clicked.disconnect()

    def showContent(self, animation=True):
        """显示内容 - 带动画"""
        self._content_widget.show()
        self._icon_widget.setIcon(FIF.CHEVRON_DOWN_MED)
        if animation:
            # 先设置为一个较大的值，让动画能计算
            self._content_widget.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX

            # 获取内容实际高度
            self._content_widget.updateGeometry()
            target_height = self._content_widget.sizeHint().height()

            # 开始动画
            self._animation.setStartValue(0)
            self._animation.setEndValue(target_height)
            self._animation.finished.connect(self._on_show_finished)
            self._animation.start()

    def hideContent(self, animation=True):
        """隐藏内容 - 带动画"""
        self._icon_widget.setIcon(FIF.MENU)
        if animation:
            current_height = self._content_widget.height()
            self._animation.setStartValue(current_height)
            self._animation.setEndValue(0)
            self._animation.finished.connect(self._on_hide_finished)
            self._animation.start()
        else:
            self._content_widget.hide()

    def _on_show_finished(self):
        """显示动画完成后的回调"""
        self._content_widget.show()
        self._content_widget.setMaximumHeight(16777215)  # 重置,不限制大小
        self._content_widget.updateGeometry()
        self._animation.finished.disconnect(self._on_show_finished)

    def _on_hide_finished(self):
        """隐藏动画完成后的回调"""
        self._content_widget.hide()
        self._content_widget.setMaximumHeight(16777215)  # 重置,不限制大小
        self._animation.finished.disconnect(self._on_hide_finished)

    def addContentWidget(self, widget: QWidget):
        """添加内容组件"""
        self._content_widget_layout.addWidget(widget)

    def addContentLayout(self, layout: QLayout):
        """添加内容布局"""
        self._content_widget_layout.addLayout(layout)

    @property
    def isExpand(self) -> bool:
        """是否展开"""
        return self._content_widget.isVisible()


class MenuCardInput(MenuCard):
    """
    输入类菜单模式设置卡片
    通过继承该类并重写以下四个方法来实现不同控件的输入选项卡
    getContentValue
    _addContentWidget
    _refulsh_title_value
    _refulsh_content_value
    """

    def __init__(self,
                 text=None,
                 parent=None,
                 get_value_func: Optional[Callable[[], str]] = None,
                 set_value_func: Optional[Callable[[str], None]] = None):
        """
        输入类菜单模式设置卡片
        :param text:标题
        :param parent:父对象
        :param get_value_func:获取数据函数
        :param set_value_func:设置数据函数
        """
        super().__init__(text, parent)

        self.get_value_func: Optional[Callable[[], str]] = None
        self.set_value_func: Optional[Callable[[str], bool | None]] = None

        if get_value_func is not None:
            self.setGetValueFunc(get_value_func)
        if set_value_func is not None:
            self.setSetValueFunc(set_value_func)

        self._addContentWidget()

        self._refulsh_title_value()

        self.enableCliked(True)

    def setGetValueFunc(self, func: Callable[[], str | int]):
        """获取显示内容函数"""
        if not callable(func):
            raise TypeError("get_value_func must be callable")
        self.get_value_func = func
        self._refulsh_title_value()

    def setSetValueFunc(self, func: Callable[[str], bool | None]):
        """设置显示内容函数"""
        if not callable(func):
            raise TypeError("set_value_func must be callable")
        self.set_value_func = func

    def getValue(self) -> object | None:
        """获取值函数返回值"""
        last_value = None
        if callable(self.get_value_func):
            last_value = self.get_value_func()
        return last_value

    def getContentValue(self) -> str:
        """获取内容区域值"""
        raise NotImplementedError('子类必须实现内容区域值')

    @info_bar_decorator
    def _accept_set_value(self):
        """确认修改值"""
        self.hideContent()
        state = False
        content = '修改失败'
        parent = self.parent() or self
        if callable(self.set_value_func):
            result = self.set_value_func(self.getContentValue())
            if isinstance(result, bool):
                state = result
            else:
                state = result
            content = '修改成功' if state else '修改失败'
        self._refulsh_title_value()
        return state, content, parent

    def _addRightWidget(self):
        """添加右侧图标组件"""
        # 添加图标显示控件
        self._icon_widget = IconWidget(FIF.SETTING)
        self._icon_widget.setFixedSize(20, 20)
        self.setRightWidget(self._icon_widget)

        # 添加值显示标签
        self._title_value = CaptionLabel(self)
        self._title_layout.insertWidget(self._title_layout.count() - 1, self._title_value)

    def _addContentWidget(self):
        """添加内容组件"""
        raise NotImplementedError('子类必须实现内容组件')

    def _refulsh_title_value(self):
        """刷新标题区域值"""
        raise NotImplementedError('子类必须实现标题区域值刷新')

    def _refulsh_content_value(self):
        """刷新内容区域值"""
        raise NotImplementedError('子类必须实现内容区域值刷新')

    def showContent(self, animation=True):
        super().showContent(animation)

        self._refulsh_content_value()

    def hideContent(self, animation=True):
        super().hideContent(animation)

        self._icon_widget.setIcon(FIF.SETTING)


class MenuCardLineEdit(MenuCardInput):
    """输入框设置选项卡"""

    @property
    def lineEdit(self) -> LineEdit:
        return self._line_edit

    def getContentValue(self) -> str:
        return self._line_edit.text()

    def _addContentWidget(self):
        """添加内容组件"""
        self._content_layout = QHBoxLayout(self)
        self._content_layout.setContentsMargins(0, 0, 0, 0)

        # 输入框
        self._line_edit = LineEdit(self)
        self._line_edit.returnPressed.connect(self._accept_set_value)
        self._content_layout.addWidget(self._line_edit)

        # 确认按钮
        self._ok_button = PrimaryToolButton(FIF.ACCEPT)
        self._ok_button.clicked.connect(self._accept_set_value)
        self._content_layout.addWidget(self._ok_button)

        # 取消按钮
        self._cancel_button = PrimaryToolButton(FIF.CLOSE)
        self._cancel_button.clicked.connect(self.hideContent)
        self._content_layout.addWidget(self._cancel_button)

        self.addContentLayout(self._content_layout)

    def _refulsh_title_value(self):
        """刷新标题区域值"""
        value = self.getValue()
        self._title_value.setText(str(value) or '')

    def _refulsh_content_value(self):
        """刷新内容区域值"""
        value = self.getValue()
        self._line_edit.setText(str(value) or '')

    def _dir_button_clicked(self):
        """目录选择按钮点击事件"""
        file_path = get_exist_dir('选择目录', dir_path=str(self.getValue()))
        self._line_edit.setText(file_path)

    def _file_button_clicked(self):
        """文件选择按钮点击事件"""
        file_path = get_exist_files('选择文件', dir_path=str(self.getValue()))
        if file_path:
            file_path = file_path[0]
            self._line_edit.setText(file_path)

    def enableDirChoose(self, enable: bool = True):
        """开启目录选择"""
        if enable:
            self._dir_button = PrimaryToolButton(FIF.FOLDER_ADD)
            self._dir_button.clicked.connect(self._dir_button_clicked)

            self._content_layout.insertWidget(self._content_layout.count() - 2, self._dir_button)
        else:
            if hasattr(self, '_dir_button'):
                self._content_layout.removeWidget(self._dir_button)
                self._dir_button.deleteLater()

    def enableFileChoose(self, enable: bool = True):
        """开启文件选择"""
        if enable:
            self._file_button = PrimaryToolButton(FIF.FOLDER_ADD)
            self._file_button.clicked.connect(self._file_button_clicked)

            self._content_layout.insertWidget(self._content_layout.count() - 2, self._file_button)
        else:
            if hasattr(self, '_file_button'):
                self._content_layout.removeWidget(self._file_button)
                self._file_button.deleteLater()


class MenuCardSpinBox(MenuCardInput):
    """数值框(整型)设置选项卡"""

    def getContentValue(self) -> str:
        return str(self._spin_box.value())

    def _addContentWidget(self):
        """添加内容组件"""
        self._content_layout = QHBoxLayout(self)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.addStretch()

        # 微调框
        self._spin_box = SpinBox(self)
        self._content_layout.addWidget(self._spin_box)

        # 确认按钮
        self._ok_button = PrimaryToolButton(FIF.ACCEPT)
        self._ok_button.clicked.connect(self._accept_set_value)
        self._content_layout.addWidget(self._ok_button)

        # 取消按钮
        self._cancel_button = PrimaryToolButton(FIF.CLOSE)
        self._cancel_button.clicked.connect(self.hideContent)
        self._content_layout.addWidget(self._cancel_button)

        self.addContentLayout(self._content_layout)

    def _refulsh_title_value(self):
        """刷新标题区域值"""
        try:
            value = self.getValue()
            value = int(value)
        except Exception:
            value = 0
        self._title_value.setText(str(value))

    def _refulsh_content_value(self):
        """刷新内容区域值"""
        try:
            value = self.getValue()
            value = int(value)
        except Exception:
            value = 0
        self._spin_box.setValue(value)


class MenuCardComboBox(MenuCardInput):
    """下拉框设置选项卡"""

    @property
    def comboBox(self) -> ComboBox:
        return self._combo_box

    def getContentValue(self) -> str:
        return str(self._combo_box.currentText())

    def _addContentWidget(self):
        """添加内容组件"""
        self._content_layout = QHBoxLayout(self)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.addStretch()

        # 微调框
        self._combo_box = ComboBox(self)
        self._content_layout.addWidget(self._combo_box)

        # 确认按钮
        self._ok_button = PrimaryToolButton(FIF.ACCEPT)
        self._ok_button.clicked.connect(self._accept_set_value)
        self._content_layout.addWidget(self._ok_button)

        # 取消按钮
        self._cancel_button = PrimaryToolButton(FIF.CLOSE)
        self._cancel_button.clicked.connect(self.hideContent)
        self._content_layout.addWidget(self._cancel_button)

        self.addContentLayout(self._content_layout)

    def _refulsh_title_value(self):
        """刷新标题区域值"""
        value = self.getValue()
        self._title_value.setText(str(value) or '')

    def _refulsh_content_value(self):
        """刷新内容区域值"""
        value = self.getValue()
        self._combo_box.setCurrentText(str(value))

    def addComboBoxItem(self, text: str):
        """添加下拉框选项"""
        self._combo_box.addItem(text)

    def addComboBoxItems(self, items: list):
        """添加下拉框选项"""
        self._combo_box.addItems(items)

    def clearComboBoxItems(self):
        """清空下拉框选项"""
        self._combo_box.clear()


if __name__ == '__main__':
    test_value = None


    def get_value():
        return test_value


    def set_value(value):
        global test_value
        test_value = value


    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    window = MenuCardComboBox('输入测试')
    window.addComboBoxItems(['123', 'abc', 'def'])
    window.setGetValueFunc(get_value)
    window.setSetValueFunc(set_value)
    window.show()
    app.exec()
