"""
系统操作
"""

from . import Get
from .PlotCv2Mod import PlotDIY


class HardMonitor:
    # HMO系统监测

    def __init__(self):
        self.__isRun = True

    def __ImportHardwareMonitor(self):
        # 导入HardwareMonitor.dll文件,返回computer,hardwareType,sensorType,SensorType实例化对象
        import ctypes, clr, os
        work_path = os.path.dirname(__file__)  # 获取该文件路径
        ohmdll = f'{work_path}\\libs\\OpenHardwareMonitorLib.dll'
        clr.AddReference(ohmdll)
        import OpenHardwareMonitor as ohm
        from OpenHardwareMonitor.Hardware import Computer, HardwareType, SensorType
        computer = Computer()
        computer.CPUEnabled = True
        computer.GPUEnabled = True
        computer.HDDEnabled = True
        computer.RAMEnabled = True
        computer.MainboardEnabled = True
        computer.FanControllerEnabled = True
        hardwareType = ohm.Hardware.HardwareType
        sensorType = ohm.Hardware.SensorType
        return computer, hardwareType, sensorType, SensorType

    def __HMOData(self) -> dict:
        """获取硬件信息"""
        import time
        computer, hardwareType, sensorType, SensorType = self.__ImportHardwareMonitor()  # 导入HardwareMonitor.dll文件
        computer.Open()  # 启动检测
        computerdict = {}  # 将获得的数据全部存入字典中
        while self.__isRun:
            for hardware in computer.Hardware:
                hardware.Update()
                for sensor in hardware.Sensors:
                    if sensor.SensorType == sensorType.Temperature:
                        si_ls = str(sensor.Identifier).split('/')
                        # 格式化返回值名称得到intelcpu#0、intelcpu#1……
                        ss_temperatures_name = f'{si_ls[1]}#{si_ls[-1]}'
                        if 'cpu' in ss_temperatures_name:
                            cpu_temperature = sensor.Value
                            computerdict[f'{ss_temperatures_name}温度'] = cpu_temperature
                        elif 'gpu' in ss_temperatures_name:
                            gpu_temperature = sensor.Value
                            computerdict[f'{ss_temperatures_name}温度'] = gpu_temperature
                    elif sensor.SensorType == sensorType.Load:
                        si_ls = str(sensor.Identifier).split('/')
                        ss_user_name = f'{si_ls[1]}#{si_ls[-1]}'
                        if 'cpu' in ss_user_name:
                            cpu_user = sensor.Value
                            computerdict[f'{ss_user_name}使用率'] = cpu_user
                        elif 'gpu' in ss_user_name:
                            gpu_user = sensor.Value
                            computerdict[f'{ss_user_name}使用率'] = gpu_user
            if not self.__cycle:
                self.__hmodata = computerdict
                return self.__hmodata
            else:
                self.__hmodata = computerdict
            time.sleep(self.__cycletime)

    def Get_Cpu_Temperature(self) -> float:
        cpu_temperatures = []
        if self.__hmodata == None:
            return None
        for key in self.__hmodata.keys():
            if 'cpu' in key and '温度' in key and self.__hmodata[key] != None:
                cpu_temperatures.append(self.__hmodata[key])
        try:
            cpu_temperature = round(sum(cpu_temperatures) / len(cpu_temperatures), 1)
        except:
            return None
        return cpu_temperature

    def Get_Gpu_Temperature(self) -> float:
        gpu_temperatures = []
        if self.__hmodata == None:
            return None
        for key in self.__hmodata.keys():
            if 'gpu' in key and '温度' in key and self.__hmodata[key] != None:
                gpu_temperatures.append(self.__hmodata[key])
        try:
            gpu_temperature = round(sum(gpu_temperatures) / len(gpu_temperatures), 1)
        except:
            return None
        return gpu_temperature

    def Get_Cpu_User(self) -> float:
        cpu_user = []
        if self.__hmodata == None:
            return None
        for key in self.__hmodata.keys():
            if 'cpu' in key and '使用率' in key and self.__hmodata[key] != None:
                cpu_user.append(self.__hmodata[key])
        try:
            cpu_user = round(sum(cpu_user) * 10 / len(cpu_user), 1)
            if cpu_user >= 100.0:
                cpu_user = 100.0
        except:
            return None
        return cpu_user

    def Start(self, 循环=False, 循环时间=1.5):
        """
        获取HMO的全部数据,启动后可以通过GetCpuTemperature访问数据
        ShowHMOPolt展示图表
        """
        import threading
        self.__isRun = True
        self.__data_cycle = threading.Thread(target=self.__HMOData, daemon=True)
        self.__cycle = 循环
        self.__cycletime = 循环时间
        self.__hmodata = None
        self.__data_cycle.start()
        return True

    def Stop(self):
        self.__isRun = False

    def HMO_polt_qt(self, window):
        """
        将HMO数据显示到qt窗口中,使用matplotlib绘制图形
        :param window:qt窗口对象
        """
        self.window = window
        # 数据准备
        xlable = [f'00:0{i}' for i in range(1, 9)]
        yCPU = [i for i in range(1, 9)]
        yGPU = [i for i in range(1, 9)]
        yCPUuser = [i for i in range(1, 9)]
        # 初始化类
        self.__plot_diy = PlotDIY()

        # 构建数据更新函数
        def updata_data():
            del xlable[0], yCPU[0], yGPU[0], yCPUuser[0]
            xlable.append(Get.NowTime('%M-%S').replace('-', ':'))
            cpu_temperature = self.Get_Cpu_Temperature()  # 获取cpu温度
            gpu_temperature = self.Get_Gpu_Temperature()  # 获取gpu温度
            cpu_user = self.Get_Cpu_User()  # 获取cpu使用率
            if cpu_temperature == None:
                yCPU.append(0)  # CPU温度
            else:
                yCPU.append(cpu_temperature)
            if gpu_temperature == None:
                yGPU.append(0)  # GPU温度
            else:
                yGPU.append(gpu_temperature)
            if cpu_user == None:
                yCPUuser.append(0)
            else:
                yCPUuser.append(cpu_user)

        # 构建更新函数
        def updata_Func(frame):
            # 更新数据
            updata_data()
            # 清楚画布
            self.__plot_diy.Plt_cla()
            # 绘制折线图
            self.__plot_diy.Plot_draw(xlable, yCPU,
                                    f'CPU温度:{yCPU[-1]}℃\n平均温度:{round(sum(yCPU) / len(yCPU), 1)}℃\n最高温度:{max(yCPU)}℃',
                                      color='red', marker='o')
            self.__plot_diy.Plot_draw(xlable, yGPU,
                                    f'GPU温度:{yGPU[-1]}℃\n平均温度:{round(sum(yGPU) / len(yGPU), 1)}℃\n最高温度:{max(yGPU)}℃',
                                      color='green', marker='s')
            # 添加数据标点
            for i in range(len(xlable)):
                self.__plot_diy.Add_annotate([f'GPU:{yGPU[i]}', (xlable[i], yGPU[i]), (xlable[i], yGPU[i] - 3)])
                self.__plot_diy.Add_annotate([f'CPU:{yCPU[i]}', (xlable[i], yCPU[i]), (xlable[i], yCPU[i] + 3)])
            # 绘制条形图
            self.__plot_diy.Bar_draw(xlable, yCPUuser, label=f'CPU使用率{yCPUuser[-1]}%')
            # 图形基本设置
            self.__plot_diy.Set_plt(title='CPU、GPU温度监测', xlabel='时间s', ylabel='温度℃',
                                    ylim=(0, 120), legend='upper left', grid=True)

        self.__plot_diy.Dynamic_graph(updata_Func, updata_time=self.__cycletime * 1000)
        self.__plot_diy.Bind_qt(window)


class Thread():
    """多线程封装,处理对象要创建文件夹时需要提前创建！！！"""

    def __init__(self, thread_num=20):
        """
        :param thread_num:创建的线程数量
        """
        self.thread_num = thread_num
        self.thread_running_list = []  # 正在运行的线程名称,默认采用int类型如[0,1,...]

    def TaskDiv(self, list_arg: list) -> list[tuple]:
        """
        将传入的列表按照thread_num尽可能等份并升高一维
        """
        # 计算每一份的元素数量
        phr_num = round(len(list_arg) / self.thread_num, 0)
        # 计算最后一份的元素数量
        end_num = phr_num + len(list_arg) - phr_num * self.thread_num
        if len(list_arg) > self.thread_num:
            return_list = [[] for i in range(self.thread_num)]
        else:
            return_list = [[] for i in range(len(list_arg))]
        for item in list_arg:
            for index, i in enumerate(return_list):
                # 如果索引是最后一个则直接添加元素
                if index == len(return_list) - 1:
                    if isinstance(i, tuple):
                        i.append(item)
                    else:
                        i.append((item,))
                    break
                # 检查该索引值中的元素是否超过每一份元素数量
                if len(i) < phr_num:
                    if isinstance(i, tuple):
                        i.append(item)
                    else:
                        i.append((item,))
                    break
        return return_list

    def thread(self, der_name, tuple_arg=(), dict_arg=None, daeamon=True):
        """
        创建一个子线程

        :param der_name: 传入函数名称
        :param tuple_arg: tuple_arg需要的位置元组参数,必须为元组形式,默认None
        :param dict_arg: dict_arg需要的关键字字典参数,默认None
        """
        import threading
        thread_name = threading.Thread(target=der_name,
                                       args=tuple_arg,
                                       kwargs=dict_arg,
                                       daemon=daeamon)
        thread_name.start()
        return thread_name

    def Iteration(self, der_name, list_arg: list[tuple]):
        """
        传入一个函数名,执行该函数索要的参数列表
        :param der_name:函数名称
        :param list_arg:列表中的每个元素是执行函数的所需参数
        """
        for arg in list_arg:
            self.thread(der_name, arg).join()  # 等待线程执行

    def Start(self, der_name, list_arg: list, daeamon=True):
        """
        传入函数名称,所需的形参列表,开始多线程执行
        """
        # 将列表升维并将元素处理成元组类型
        list_arg = self.TaskDiv(list_arg)
        for arg in list_arg:
            self.thread(self.Iteration,
                        (der_name, arg),
                        daeamon=daeamon)


class Multi():
    """多进程类封装"""
