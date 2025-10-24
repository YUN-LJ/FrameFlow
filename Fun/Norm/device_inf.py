"""
系统操作
"""

from Fun.Norm import get

from Fun.GUI_Qt import PlotCv2Mod


class HardMonitor:
    # HMO系统监测

    def __init__(self):
        # 导入HardwareMonitor.dll文件
        (self.__computer,
         self.__hardwareType,
         self.__sensorType,
         self.__SensorType) = self.__import_ohm()
        # 启动检测
        self.__computer.Open()
        # 绘图时用的上
        # 初始化绘图类
        self.__plot = PlotCv2Mod.PlotQt()
        # 存储数值
        self.__xlable = [f'00:00:0{i}' for i in range(0, 10)]
        self.__ycpu_temp = [0 for i in range(0, 10)]  # cpu温度
        self.__ygpu_temp = [0 for i in range(0, 10)]  # gpu温度
        self.__ycpu_load = [0 for i in range(0, 10)]  # cpu负载
        self.__ygpu_load = [0 for i in range(0, 10)]  # gpu负载
        # 更新时间
        self.time = 5.0

    def __import_ohm(self):
        # 导入HardwareMonitor.dll文件,返回computer,hardwareType,sensorType,SensorType实例化对象
        import clr, os
        work_path = os.path.dirname(__file__)  # 获取该文件路径
        ohm_dll_path = f'{work_path}/../libs/OpenHardwareMonitorLib.dll'
        clr.AddReference(ohm_dll_path)
        import OpenHardwareMonitor as ohm
        from OpenHardwareMonitor.Hardware import Computer, HardwareType, SensorType
        computer = Computer()
        computer.CPUEnabled = True  # 启用CPU监控
        computer.GPUEnabled = True  # 启用GPU监控
        computer.HDDEnabled = True  # 启用硬盘监控
        computer.RAMEnabled = True  # 启用内存监控
        computer.MainboardEnabled = True  # 启用主板监控
        computer.FanControllerEnabled = True  # 启用风扇监控
        hardwareType = ohm.Hardware.HardwareType  # 用于判断硬件类型
        sensorType = ohm.Hardware.SensorType
        return computer, hardwareType, sensorType, SensorType

    def get_TEMP(self, only_cpu=False, only_gpu=False, only_hdd=False, avg=False) -> float | dict:
        """
        获取cpu/gpu/hdd温度监测,单位℃,当only和avg同时启用时返回float类型
        :param only_cpu:只返回cpu温度
        :param only_gpu:只返回gpu温度
        :param only_hdd:只返回硬盘温度
        :param avg:返回平均值,默认返回每颗核心温度
        """
        cpu_TEMP = {}  # 全部cpu温度
        gpu_TEMP = {}  # 全部gpu温度
        hdd_TEMP = {}  # 全部硬盘温度
        for hardware in self.__computer.Hardware:
            hardware.Update()
            for sensor in hardware.Sensors:
                if sensor.SensorType == self.__sensorType.Temperature:
                    si_ls = str(sensor.Identifier).split('/')
                    # 格式化返回值名称得到intelcpu#0、intelcpu#1……
                    ss_name = f'{si_ls[1]}#{si_ls[-1]}'
                    if 'cpu' in ss_name:
                        index = ss_name.find('cpu')
                        temp = sensor.Value
                        cpu_TEMP.update({f'{ss_name[:index]}#{ss_name[index:]}': temp})
                    elif 'gpu' in ss_name:
                        index = ss_name.find('gpu')
                        temp = sensor.Value
                        gpu_TEMP.update({f'{ss_name[:index]}#{ss_name[index:]}': temp})
                    elif 'hdd' in ss_name:
                        temp = sensor.Value
                        hdd_TEMP.update({ss_name: temp})
        if avg:
            # 处理成平均值
            for cpu_name in cpu_TEMP:
                cpu_name = f'{cpu_name[:cpu_name.find('cpu')]}cpu'
                break
            try:
                cpu_avg_temp = round(sum(cpu_TEMP.values()) / len(cpu_TEMP), 2)
            except Exception as e:
                print(f'HaedMonitor-get_TEMP:数据获取失败,请以管理员权限运行\n{e}')
                cpu_avg_temp = 0
            cpu_TEMP = {cpu_name: cpu_avg_temp}

            for gpu_name in gpu_TEMP:
                gpu_name = f'{gpu_name[:gpu_name.find('gpu')]}gpu'
                break
            try:
                gpu_avg_temp = round(sum(gpu_TEMP.values()) / len(gpu_TEMP), 2)
            except Exception as e:
                print(f'HaedMonitor-get_TEMP:数据获取失败,请以管理员权限运行\n{e}')
                gpu_avg_temp = 0
            gpu_TEMP = {gpu_name: gpu_avg_temp}
            try:
                hdds_avg_temp = round(sum(hdd_TEMP.values()) / len(hdd_TEMP), 2)
            except Exception as e:
                print(f'HaedMonitor-get_TEMP:数据获取失败,请以管理员权限运行\n{e}')
                hdds_avg_temp = 0
            hdd_TEMP = {'hdd': hdds_avg_temp}

        if only_cpu:
            if avg:
                for i in cpu_TEMP.values():
                    return i
            else:
                return cpu_TEMP
        elif only_gpu:
            if avg:
                for i in gpu_TEMP.values():
                    return i
            else:
                return gpu_TEMP
        elif only_hdd:
            if avg:
                for i in hdd_TEMP.values():
                    return i
            else:
                return hdd_TEMP
        else:
            # 将两个字典合并后返回
            return cpu_TEMP | gpu_TEMP | hdd_TEMP

    def get_LOAD(self, only_cpu=False, only_gpu=False, only_ram=False, stat=False) -> float | dict:
        """
        获取cpu/gpu/内存的负载(使用率),单位%(百分比),当only和stat同时启用时返回float类型
        :param only_cpu:只返回cpu负载
        :param only_gpu:只返回gpu负载
        :param only_ram:只返回内存负载
        :param stat:返回统计值(更接近任务管理器数值),默认返回每颗核心的使用率
        """
        cpu_LOAD = {}  # 全部cpu负载
        gpu_LOAD = {}  # 全部gpu负载
        ram_LOAD = {}  # 全部内存负载
        for hardware in self.__computer.Hardware:
            hardware.Update()
            for sensor in hardware.Sensors:
                if sensor.SensorType == self.__sensorType.Load:
                    si_ls = str(sensor.Identifier).split('/')
                    # 格式化返回值名称得到intelcpu#0、intelcpu#1……
                    ss_name = f'{si_ls[1]}#{si_ls[-1]}'
                    if 'cpu' in ss_name:
                        index = ss_name.find('cpu')
                        load = sensor.Value
                        cpu_LOAD.update({f'{ss_name[:index]}#{ss_name[index:]}': load})
                    elif 'gpu' in ss_name:
                        index = ss_name.find('gpu')
                        load = sensor.Value
                        gpu_LOAD.update({f'{ss_name[:index]}#{ss_name[index:]}': load})
                    elif 'ram' in ss_name:
                        load = sensor.Value
                        ram_LOAD.update({ss_name: load})
        if stat:
            # 处理成平均值
            for cpu_name in cpu_LOAD:
                cpu_name = f'{cpu_name[:cpu_name.find('cpu')]}cpu'
                break
            cpu_avg_load = round(sum(cpu_LOAD.values()), 2)
            cpu_LOAD = {cpu_name: cpu_avg_load}

            for gpu_name in gpu_LOAD:
                gpu_name = f'{gpu_name[:gpu_name.find('gpu')]}gpu'
                break
            count = 1
            for i in gpu_LOAD.values():
                if i >= 1.0:
                    count += 1
            gpu_avg_temp = round(sum(gpu_LOAD.values()) / count, 2)
            gpu_LOAD = {gpu_name: gpu_avg_temp}

            ram_avg_load = round(sum(ram_LOAD.values()), 2)
            ram_LOAD = {'ram': ram_avg_load}

        if only_cpu:
            if stat:
                for i in cpu_LOAD.values():
                    return i
            else:
                return cpu_LOAD
        elif only_gpu:
            if stat:
                for i in gpu_LOAD.values():
                    return i
            else:
                return gpu_LOAD
        elif only_ram:
            if stat:
                for i in ram_LOAD.values():
                    return i
            else:
                return ram_LOAD
        else:
            # 将两个字典合并后返回
            return cpu_LOAD | gpu_LOAD | ram_LOAD

    def ohm_plot(self) -> PlotCv2Mod.PlotQt:
        """
        将HMO数据显示到qt窗口中,使用matplotlib绘制图形
        :return PlotCv2Mod.PlotWidget
        """
        # 删除最旧值
        del self.__xlable[0]
        del self.__ycpu_temp[0]
        del self.__ygpu_temp[0]
        del self.__ycpu_load[0]
        del self.__ygpu_load[0]
        # 获取最新值
        self.__xlable.append(get.now_time('%H:%M:%S'))
        self.__ycpu_temp.append(self.get_TEMP(only_cpu=True, avg=True))  # cpu温度
        self.__ygpu_temp.append(self.get_TEMP(only_gpu=True, avg=True))  # gpu温度
        self.__ycpu_load.append(self.get_LOAD(only_cpu=True, stat=True))  # cpu负载
        self.__ygpu_load.append(self.get_LOAD(only_gpu=True, stat=True))  # gpu负载

        # 计算平均温度
        try:
            avg_cpu_temp = round(sum(self.__ycpu_temp) / len([i for i in self.__ycpu_temp if i != 0]), 1)
        except ZeroDivisionError as e:
            print(f'HardMonitor-ohm_plot:CPU平均温度计算错误\n{e}')
            avg_cpu_temp = 0
        try:
            avg_gpu_temp = round(sum(self.__ygpu_temp) / len([i for i in self.__ygpu_temp if i != 0]), 1)
        except ZeroDivisionError as e:
            print(f'HardMonitor-ohm_plot:GPU平均温度计算错误\n{e}')
            avg_gpu_temp = 0

        # 清除画布内容
        self.__plot.clear_plot()

        # 绘制折线图
        self.__plot.plot_(dict(zip(self.__xlable, self.__ycpu_temp)), linewidth=1,
                          label=f'cpu温度:{avg_cpu_temp}℃', color='red')
        self.__plot.plot_(dict(zip(self.__xlable, self.__ygpu_temp)),
                          label=f'gpu温度:{avg_gpu_temp}℃', linewidth=1, marker='^')

        # 设置画布信息
        self.__plot.set_fig(title='cpu/gpu温度', xlabel='时间', ylabel='温度℃')

        # 固定绘图范围
        max_temp = str(int(max(self.__ycpu_temp + self.__ygpu_temp)))
        max_temp = int(max_temp[0] + '0' * (len(max_temp) - 1)) + 15
        self.__plot.set_ylimit(30, max_temp)

        return self.__plot

    # def HMO_polt_qt(self, window):
    #     """
    #     将HMO数据显示到qt窗口中,使用matplotlib绘制图形
    #     已经废弃
    #     :param window:qt窗口对象
    #     """
    #     self.window = window
    #     # 数据准备
    #     xlable = [f'00:0{i}' for i in range(1, 9)]
    #     yCPU = [i for i in range(1, 9)]
    #     yGPU = [i for i in range(1, 9)]
    #     yCPUuser = [i for i in range(1, 9)]
    #     # 初始化类
    #     self.__plot_diy = PlotDIY()
    #
    #     # 构建数据更新函数
    #     def updata_data():
    #         del xlable[0], yCPU[0], yGPU[0], yCPUuser[0]
    #         xlable.append(Get.NowTime('%M-%S').replace('-', ':'))
    #         cpu_temperature = self.Get_Cpu_Temperature()  # 获取cpu温度
    #         gpu_temperature = self.Get_Gpu_Temperature()  # 获取gpu温度
    #         cpu_user = self.Get_Cpu_User()  # 获取cpu使用率
    #         if cpu_temperature == None:
    #             yCPU.append(0)  # CPU温度
    #         else:
    #             yCPU.append(cpu_temperature)
    #         if gpu_temperature == None:
    #             yGPU.append(0)  # GPU温度
    #         else:
    #             yGPU.append(gpu_temperature)
    #         if cpu_user == None:
    #             yCPUuser.append(0)
    #         else:
    #             yCPUuser.append(cpu_user)
    #
    #     # 构建更新函数
    #     def updata_Func(frame):
    #         # 更新数据
    #         updata_data()
    #         # 清楚画布
    #         self.__plot_diy.Plt_cla()
    #         # 绘制折线图
    #         self.__plot_diy.Plot_draw(xlable, yCPU,
    #                                   f'CPU温度:{yCPU[-1]}℃\n平均温度:{round(sum(yCPU) / len(yCPU), 1)}℃\n最高温度:{max(yCPU)}℃',
    #                                   color='red', marker='o')
    #         self.__plot_diy.Plot_draw(xlable, yGPU,
    #                                   f'GPU温度:{yGPU[-1]}℃\n平均温度:{round(sum(yGPU) / len(yGPU), 1)}℃\n最高温度:{max(yGPU)}℃',
    #                                   color='green', marker='s')
    #         # 添加数据标点
    #         for i in range(len(xlable)):
    #             self.__plot_diy.Add_annotate([f'GPU:{yGPU[i]}', (xlable[i], yGPU[i]), (xlable[i], yGPU[i] - 3)])
    #             self.__plot_diy.Add_annotate([f'CPU:{yCPU[i]}', (xlable[i], yCPU[i]), (xlable[i], yCPU[i] + 3)])
    #         # 绘制条形图
    #         self.__plot_diy.Bar_draw(xlable, yCPUuser, label=f'CPU使用率{yCPUuser[-1]}%')
    #         # 图形基本设置
    #         self.__plot_diy.Set_plt(title='CPU、GPU温度监测', xlabel='时间s', ylabel='温度℃',
    #                                 ylim=(0, 120), legend='upper left', grid=True)
    #
    #     self.__plot_diy.Dynamic_graph(updata_Func, updata_time=self.__cycletime * 1000)
    #     self.__plot_diy.Bind_qt(window)c


if __name__ == '__main__':
    ohm = HardMonitor()
    print(ohm.get_TEMP(avg=True))
    print(ohm.get_LOAD(stat=True))
