"""主页"""
import sys, os, multiprocessing as mp, time, gc

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.realpath(__file__))
# 计算父级目录的路径(wallpaper路径)
parent_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
# 将父级目录添加到模块搜索路径
sys.path.append(parent_dir)

# UI界面-PySide6模块及其美化库
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import QThread, Signal
# from qfluentwidgets.components.widgets.button import PrimaryToolButton
# from qfluentwidgets import FluentIcon as FIF

# 本项目公用库
from Fun.Norm import device_inf

# 导入UI界面
try:
    from .ui.home import Ui_home
except:
    from ui.home import Ui_home


class TempPlot(QThread):
    update_signal = Signal(dict)

    def __init__(self, layout, parent=None):
        super(TempPlot, self).__init__(parent)
        self.__layout = layout

        # 初始化设备监测
        self.__ohm = device_inf.HardMonitor()  # HardMonitor实例

        self.time = 5  # 更新时间

    def set_time(self, time: float):
        self.time = time

    def update_plot(self):
        self.__polt.show()

    def run(self):
        start = 0
        # 获取绘图对象
        self.__polt = self.__ohm.ohm_plot()
        self.__polt.set_layout(self.__layout)
        data = {'temp': self.__ohm.get_TEMP(avg=True)} | {'load': self.__ohm.get_LOAD(stat=True)}
        self.update_signal.emit(data)
        # 进入循环
        while True:
            if time.time() - start > self.time:
                self.__ohm.ohm_plot()
                data = {'temp': self.__ohm.get_TEMP(avg=True)} | {'load': self.__ohm.get_LOAD(stat=True)}
                self.update_signal.emit(data)
                start = time.time()
            else:
                time.sleep(0.3)


class HomeWin(QWidget, Ui_home):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__parent = parent
        self.setupUi(self)

        self.__thread = TempPlot(self.verticalLayout_4)
        self.__thread.update_signal.connect(self.__update_ui)
        self.__thread.start()

        self.__bind()

    def __bind(self):
        """控件绑定"""
        self.spinBox.setValue(5)
        self.spinBox.valueChanged.connect(lambda value: self.__thread.set_time(value))

    def __update_ui(self, data: dict):
        for key, value in data['temp'].items():
            if key.find('cpu') != -1:
                cpu_temp = value
            if key.find('gpu') != -1:
                gpu_temp = value
            if key.find('hdd') != -1:
                hdd_temp = value
        for key, value in data['load'].items():
            if key.find('cpu') != -1:
                cpu_load = value
            if key.find('gpu') != -1:
                gpu_load = value
            if key.find('ram') != -1:
                ram_load = value
        self.label_cpu_temp.setText(f'CPU温度:{cpu_temp}℃')
        self.label_gpu_temp.setText(f'GPU温度:{gpu_temp}℃')
        self.label_hdd_temp.setText(f'HDD温度:{hdd_temp}℃')
        self.label_cpu_load.setText(f'CPU使用率:{cpu_load}%')
        self.label_gpu_load.setText(f'GPU使用率:{gpu_load}%')
        self.label_ram_load.setText(f'RAM使用率:{ram_load}%')
        self.__thread.update_plot()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    win = HomeWin()
    win.show()
    app.exec()
