"""将cv2中获取的照片或视频显示到qt中"""
import cv2, os
from numpy import ndarray
from PySide6.QtWidgets import QLabel, QFileDialog
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer, Qt


class Cv2ShowQt:

    def __init__(self, lable: QLabel = None):
        """
        :param lable: QLable对象
        :param layout: QHBoxLayout
        """
        self.__lable = lable
        # 视频捕获对象
        self.__cap = None

        # 是否循环播放
        self.__loop = False
        self.__video_path = None

        # 缩放选择
        self.__scale = 0

        # 定时器用于视频刷新
        self.__video = QTimer()
        self.__video.timeout.connect(self.__update_frame)

    def set_lable(self, lable: QLabel):
        """设置标签"""
        self.__lable = lable

    def open_image(self, show: bool = True) -> str:
        """
        打开照片

        :param show:是否显示
        """
        # 停止可能正在播放的视频
        self.__close_video()

        # 打开文件对话框选择图片
        file_path, _ = QFileDialog.getOpenFileName(None, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp)")

        if show and file_path:
            self.__display_image(file_path)
        if file_path:
            return file_path
        else:
            return ''

    def open_video(self, show: bool = True, loop: bool = False, scale=0) -> str:
        """
        打开视频

        :param show:是否自动显示
        :param loop:是否循环播放
        :param scale:缩放,0保持比例缩放,1强制拉伸,-1不缩放
        """
        # 停止可能正在播放的视频
        self.__close_video()

        # 打开文件对话框选择视频
        file_path, _ = QFileDialog.getOpenFileName(None, "选择视频", "", "视频文件 (*.mp4 *.avi *.mov *.mkv)")

        if show and file_path:
            self.__loop = loop
            self.__scale = scale
            self.__play_video(file_path)
        if file_path:
            return file_path
        else:
            return ''

    def __display_image(self, image):
        """
        显示图片

        :param image:图片地址或ndarray类型
        """
        # 判断类型,如果是numpy.ndarray就可以不处理了
        if isinstance(image, ndarray):
            cv_image = image
        elif isinstance(image, str):
            # 使用OpenCV读取图片
            try:
                # cv_image = cv2.imread(image)
                # 以下这种方式读取图片可以避免中文路径的问题
                cv_image = cv2.imdecode(np.fromfile(image, dtype=np.uint8), cv2.IMREAD_COLOR)
                if cv_image is None:
                    raise ValueError(image)
            except Exception as e:
                print(f'[Cv2ShowQt] 错误{image}')
                return False
        # 转换颜色空间，OpenCV默认是BGR，PyQt需要RGB
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)

        # 获取图像尺寸
        height, width, channel = rgb_image.shape
        # 计算字节数
        bytes_per_line = channel * width

        # 创建QImage对象
        q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)

        # 缩放图像以适应窗口，保持比例
        if self.__scale == 0:
            scaled_image = q_image.scaled(
                self.__lable.width(), self.__lable.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        elif self.__scale == 1:
            scaled_image = q_image.scaled(
                self.__lable.width(), self.__lable.height())

        # 在标签上显示图像
        self.__lable.setPixmap(QPixmap.fromImage(scaled_image))
        self.__lable.setAlignment(Qt.AlignCenter)  # 设置居中对齐

    def __play_video(self, video_path: str):
        # 打开视频文件
        self.__close_video()
        try:
            self.__cap = cv2.VideoCapture(video_path)
            self.__video_path = video_path
        except Exception as e:
            print(f'[Cv2ShowQt] {video_path}')
            return False
        if self.__cap.isOpened():
            fps = int(self.__cap.get(cv2.CAP_PROP_FPS))  # 获取原视频帧率
            update_time = 1000 // fps  # 换算每张之间的间隔为多少毫秒
            if update_time >= 1:
                self.__video.start(update_time)  # 启动视频播放
            return True
        return False

    def __update_frame(self):
        """视频播放"""
        # 读取视频帧
        ret, frame = self.__cap.read()
        if ret:
            # 显示视频帧
            self.__display_image(frame)
        else:
            if self.__loop:
                self.__cap = cv2.VideoCapture(self.__video_path)
            else:
                # 视频播放完毕
                self.__close_video()
                self.__lable.setText("视频播放完毕")

    def __close_video(self):
        """尝试关闭正在播放的视频"""
        if self.__cap is not None:
            self.__cap.release()
            self.__cap = None
        self.__video.stop()

    def show(self, file_path: str, loop: bool = False, scale=0):
        """
        显示
        :param file_path:文件路径
        :param loop:是否循环
        :param scale:缩放,0保持比例缩放,1强制拉伸,-1不缩放
        """
        if not os.path.exists(file_path):
            return False
        self.__scale = scale
        ext = os.path.splitext(file_path)[1]
        if ext in ['.png', '.jpg', '.jpeg', '.bmp']:
            self.__close_video()
            self.__display_image(file_path)
        elif ext in ['.mp4', '.avi']:
            self.__loop = loop
            self.__play_video(file_path)


"""matplotlib库针对Qt库的封装"""
import matplotlib

matplotlib.use('QtAgg')
# 打印当前使用的 Qt 绑定
from matplotlib.backends.qt_compat import QtCore

# print("当前matplotlib后端GUI绑定:", QtCore.__name__)

import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, Wedge
import numpy as np

# 修改matplotlib的字体,用于显示中文
plt.rcParams['font.sans-serif'] = ['SimHei']
# 修补字体修改成SimHei后符号显示不正确的情况
plt.rcParams['axes.unicode_minus'] = False

from PySide6.QtWidgets import QHBoxLayout


class PlotQt:
    """
    需要在Qt中对同一个fig图形对象进行重绘时
    需要调用clear_plot方法后再调用plot_等方法最后再调用show方法更新图形
    """

    def __init__(self, layout: QHBoxLayout = None, nrow: int = 1, ncol: int = 1):
        """
        :param layout: Qt布局
        :param nrow: 创建一个几行几列的子图,行
        :param ncol: 创建一个几行几列的子图,列
        """
        self.__layout = layout
        # 是否嵌入Qt中
        self.__bind = False
        # axes 是一个 nrow x nrow 的数组，可通过索引访问子图
        # axes[0, 0].plot([1, 2, 3], [4, 5, 1])
        self.__fig, self.__ax = plt.subplots(nrows=nrow, ncols=ncol)
        # 设置操作的子图,默认为第一行的第一个
        if nrow == 1 and ncol == 1:
            self.__cur_ax = self.__ax

    def set_index(self, row: int, col: int):
        """设置当前操作的子图"""
        self.__cur_ax = self.__ax[row, col]

    def set_layout(self, layout: QHBoxLayout):
        """设置显示的布局"""
        self.__layout = layout

    def set_fig(self, title: str = None, xlabel: str = None, ylabel: str = None,
                xticklabels: tuple = (45, 'right')):
        """
        设置当前子图的信息
        :param title: 标题
        :param xlabel: x轴标签
        :param ylabel: y轴标签
        :param xticklabels: x轴标签的旋转角度和旋转方向
        """
        # 设置标题和轴标签
        if isinstance(title, str):
            self.__cur_ax.set_title(title)
        if isinstance(xlabel, str):
            self.__cur_ax.set_xlabel(xlabel)
        if isinstance(ylabel, str):
            self.__cur_ax.set_ylabel(ylabel)

        # 旋转x轴标签避免重叠
        # 获取当前x轴标签
        xtick_labels = [label.get_text() for label in self.__cur_ax.get_xticklabels()]
        self.__cur_ax.set_xticks(xtick_labels)
        self.__cur_ax.set_xticklabels(labels=xtick_labels, rotation=xticklabels[0], ha=xticklabels[1])

        # 虚线网格，透明度0.7 '-'（实线）、'--'（虚线）、':'（点线）、'-.'（点划线）
        self.__cur_ax.grid(True, linestyle='--', alpha=0.7)

        # 添加图例
        self.__cur_ax.legend(loc="upper left", fontsize=10, framealpha=0.8)

        # 对整个图形调用 tight_layout()，自动调整所有子图布局
        self.__fig.tight_layout()  # 或 plt.tight_layout()

    def set_ylimit(self, min: float | int, max: float | int):
        """设置y轴的最小值和最大值"""
        self.__cur_ax.set_ylim(min, max)

    def set_xlimit(self, min: float | int, max: float | int):
        """设置x轴的最小值和最大值"""
        self.__cur_ax.set_xlim(min, max)

    def pie(self, data: dict, title: str = '', limit: int = 0, explode_index: int = 0, autopct='%1.1f%%'):
        """
        饼图

        :param data:值[标签名:值]
        :param title:标题
        :param limit:限制分类数量,None为全部显示,输入值时会将后续的合并为其它
        :param explode_index:突出显示,默认最大值
        :param autopct:显示数据标签
        """
        # 将字典按照值从大到小排序
        data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))
        x = list(data.values())
        if x == []:
            return False
        y = [f'{key}-{value}' for key, value in data.items()]
        if limit is not None:
            if 0 < limit < len(x):
                item = sum(x[limit:])
                x = x[:limit]
                x.append(item)
                y = y[:limit]
                y.append(f'其它-{item}')
        # 添加标题
        if title != '':
            self.__cur_ax.set_title(title)

        # 突出显示
        explode = [0 for i in range(len(x) - 1)]
        explode.insert(explode_index, 0.1)

        # 绘图
        self.__ax.pie(x,
                      labels=y,
                      explode=explode,  # 突出显示
                      autopct=autopct  # 显示百分比
                      )

    def plot_(self, data: dict, linewidth=3, color="#7da3d3", label: str = '--', linestyle: str = '--',
              sort: bool = None, marker: str = 'o', markersize='3', limit: int = 0):
        """
        折线图

        :param data: 值{x:y}
        :param linewidth: 线宽
        :param color: 线条颜色
        :param label: 图例名
        :param linestyle: 线条风格,默认虚线  --:虚线, -:实线
        :param sort: 排序,True从大到小,False从小到大,默认为None不排序
        :param marker: 标记点形状   1-4:奔驰图标,o:圆形,s:方形,p:正五边形,v:倒三角,^:正三角,>、<:三角形,d:菱形,h:正六边形,*:星星,x:叉叉
        :param markersize: 标记点大小
        :param limit: 截断显示前面多少条数据
        """
        # 处理数据排序
        if sort in [True, False]:
            data = dict(sorted(data.items(), key=lambda x: x[1], reverse=sort))

        # 处理数据截断
        if 0 < limit < len(data):
            x = list(data.keys())[:limit]
            y = list(data.values())[:limit]
        else:
            x = list(data.keys())
            y = list(data.values())

        # 绘制折线图
        self.__cur_ax.plot(x, y,
                           color=color,
                           linewidth=linewidth,
                           linestyle=linestyle,
                           marker=marker,
                           markersize=markersize,
                           label=label)

        # 添加数据标签（调整位置至数据点上方）
        for i, (xi, yi) in enumerate(zip(x, y)):
            # 计算标签位置偏移量（根据数据值动态调整，确保在点上方）
            y_offset = (max(y) - min(y)) * 0.02 if len(y) > 1 and max(y) != min(y) else 0.1

            self.__cur_ax.text(
                xi, yi + y_offset,  # 标签位置在数据点上方
                f'{yi}',
                fontsize=9,
                ha='center',  # 水平居中
                va='bottom',  # 垂直方向从底部对齐（确保在点上方）
                color="#333333",
                bbox=dict(facecolor='white', edgecolor='none', pad=1, alpha=0.7)  # 白色背景避免与网格线重叠
            )

    def bar(self, data: dict, sort: bool = None, limit: int = 0, show_value: bool = True,
            gradient_colors: list = ["#e2eafa", "#7DA3D3"]):
        """
        :param data: 数据源，格式{x:y}（如{'淘宝':280, '京东':210}）
        :param sort: 排序，True=降序（大→小），False=升序（小→大），None=不排序,默认不排序
        :param limit: 截断显示前N条数据，0=显示全部
        :param show_value: 柱子顶部显示数值，默认True
        :param gradient_colors: 柱子渐变色,开始值和结束值
        """
        if sort in [True, False]:
            data = dict(sorted(data.items(), key=lambda x: x[1], reverse=sort))

        labels = list(data.keys())[:limit] if (0 < limit < len(data)) else list(data.keys())
        values = list(data.values())[:limit] if (0 < limit < len(data)) else list(data.values())

        cmap = LinearSegmentedColormap.from_list("custom_gradient", gradient_colors)
        norm = plt.Normalize(0, max(values)) if values else plt.Normalize(0, 1)
        colors = [cmap(norm(val)) for val in values]

        bars = self.__ax.bar(labels, values, color=colors, edgecolor='white', linewidth=1)

        # 柱子顶部显示数值（简化位置计算，只适配纵向）
        if show_value:
            if values:
                max_val = max(values)  # 用于计算数值标签与柱子的间距
            else:
                max_val = 0
            for bar, val in zip(bars, values):
                # 数值标签位置：柱子顶部居中，距离顶部留1%间距（避免贴边）
                self.__ax.text(
                    bar.get_x() + bar.get_width() / 2,  # 水平居中
                    bar.get_height() + max_val * 0.01,  # 垂直在柱子顶部上方
                    str(val), ha='center', va='bottom',
                    fontsize=9, fontweight='bold', color='black'
                )

    def gauge(self, target: float, current: float, title: str = '销售额指标完成情况',
              labels: list = ['未达标', '达标', '优秀'],
              colors: list = ['#ff6b6b', '#4ecdc4', '#45b7d1'],
              min_value: float = 0, max_value: float = None):
        """
        仪表盘图表：显示销售额指标完成情况

        :param target: 目标销售额
        :param current: 当前销售额
        :param title: 图表标题
        :param labels: 不同完成度的标签（默认：未达标、达标、优秀）
        :param colors: 对应标签的颜色（默认：红色、青色、蓝色）
        :param min_value: 最小值（默认0）
        :param max_value: 最大值（默认目标值的1.5倍）
        """
        # 设置最大值默认值
        if max_value is None:
            max_value = target * 1.5

        # 计算完成率
        completion_rate = current / target if target != 0 else 0
        completion_text = f'完成率: {completion_rate:.1%}'
        value_text = f'当前: {current:.2f}\n目标: {target:.2f}'

        # 清除当前轴
        self.__ax.clear()

        # 设置标题
        if title:
            self.__ax.set_title(title, fontsize=14, fontweight='bold')

        # 计算仪表盘范围
        start_angle = 210  # 起始角度（左侧）
        end_angle = -30  # 结束角度（右侧）
        total_angle = start_angle - end_angle  # 总角度范围

        # 创建仪表盘颜色分区
        num_segments = len(colors)
        segment_angle = total_angle / num_segments

        for i in range(num_segments):
            # 计算每个分区的角度范围
            seg_start = start_angle - i * segment_angle
            seg_end = seg_start - segment_angle

            # 绘制扇形分区
            wedge = Wedge(
                center=(0, 0),
                r=1,
                theta1=seg_end,
                theta2=seg_start,
                width=0.3,
                facecolor=colors[i],
                edgecolor='white',
                linewidth=2,
                alpha=0.8
            )
            self.__ax.add_patch(wedge)

            # 添加分区标签 - 调整位置使其在颜色区域内居中
            label_angle = (seg_start + seg_end) / 2
            label_radius = 0.85  # 标签距离中心的距离
            # 计算标签坐标
            rad_angle = np.radians(label_angle)
            x = label_radius * np.cos(rad_angle)
            y = label_radius * np.sin(rad_angle)

            # 文本水平垂直居中对齐
            ha = 'center'
            va = 'center'
            # 添加标签，确保在颜色区域内
            self.__ax.text(x, y, labels[i], fontsize=13,
                           ha=ha, va=va, color='white', fontweight='bold')

        # 添加4个刻度
        tick_values = [min_value, target * 0.5, target, max_value]  # 刻度值
        tick_labels = [f'{v:.0f}' for v in tick_values]  # 刻度文本

        for value, label in zip(tick_values, tick_labels):
            # 计算每个刻度的角度
            value_range = max_value - min_value
            normalized_value = (value - min_value) / value_range if value_range != 0 else 0
            tick_angle = start_angle - normalized_value * total_angle

            # 绘制刻度线
            tick_outer_radius = 1.0
            tick_inner_radius = 0.9
            tick_x_outer = tick_outer_radius * np.cos(np.radians(tick_angle))
            tick_y_outer = tick_outer_radius * np.sin(np.radians(tick_angle))
            tick_x_inner = tick_inner_radius * np.cos(np.radians(tick_angle))
            tick_y_inner = tick_inner_radius * np.sin(np.radians(tick_angle))

            self.__ax.plot([tick_x_inner, tick_x_outer], [tick_y_inner, tick_y_outer],
                           color='white', linewidth=2)

            # 绘制刻度标签
            label_radius = 1.1  # 标签在刻度外侧
            label_x = label_radius * np.cos(np.radians(tick_angle))
            label_y = label_radius * np.sin(np.radians(tick_angle))

            # 根据刻度位置调整文本对齐
            if 90 < tick_angle < 270:
                ha = 'right'
            else:
                ha = 'left'

            va = 'center'
            if 0 < tick_angle < 180:
                va = 'bottom'
            elif 180 < tick_angle < 360:
                va = 'top'

            self.__ax.text(label_x, label_y, label, fontsize=12, ha=ha, va=va)

        # 绘制中心圆
        center_circle = Circle((0, 0), 0.7, facecolor='white', edgecolor='white', linewidth=1)
        self.__ax.add_patch(center_circle)

        # 计算指针角度
        value_range = max_value - min_value
        normalized_value = (current - min_value) / value_range if value_range != 0 else 0
        normalized_value = max(0, min(normalized_value, 1))  # 限制在0-1之间
        pointer_angle = start_angle - normalized_value * total_angle

        # 绘制指针
        pointer_length = 0.65
        pointer_x = pointer_length * np.cos(np.radians(pointer_angle))
        pointer_y = pointer_length * np.sin(np.radians(pointer_angle))
        self.__ax.plot([0, pointer_x], [0, pointer_y], color='#333333', linewidth=3, marker='o', markersize=6)

        # 添加中心文本（完成率和数值）
        self.__ax.text(0, -0.1, completion_text, fontsize=12, ha='center', va='center', fontweight='bold')
        self.__ax.text(0, -0.3, value_text, fontsize=10, ha='center', va='center', linespacing=1.5)

        # 设置轴属性
        self.__ax.set_aspect('equal')
        self.__ax.set_xlim(-1.3, 1.3)  # 稍微扩大范围以容纳刻度标签
        self.__ax.set_ylim(-0.9, 1.3)
        self.__ax.axis('off')  # 隐藏坐标轴

        # 调整布局
        plt.tight_layout()

    def __bind_qt(self):
        """嵌入qt图形界面中"""
        if not self.__bind:
            # 创建一个matplotlib图表
            self.__canvas = FigureCanvasQTAgg(self.__fig)
            # 绑定窗口
            self.__layout.addWidget(self.__canvas)
            self.__canvas.draw()
            self.__bind = True
        else:
            self.__canvas.draw()

    def clear_plot(self):
        """清除当前画布内容"""
        self.__cur_ax.clear()

    def remove_plot(self):
        """从Qt窗口中移除并销毁plot图像"""
        # 从窗口中移除画布
        try:
            if self.__canvas in self.__layout.findChildren(type(self.__canvas)):
                self.__layout.removeWidget(self.__canvas)
            # 释放画布资源
            self.__canvas.deleteLater()  # Qt的对象删除方法
            del self.__canvas  # 解除引用
            # self.__canvas = None  # 解除引用
            # 关闭画布对象
            plt.close(self.__fig)
            del self.__fig

        except Exception as e:
            print(f'PlotWidget-remove_plot 错误\n{e}')

    def show(self, layout: QHBoxLayout = None):
        if self.__layout is None:
            plt.show()
        else:
            self.__bind_qt()


if __name__ == '__main__':
    data1 = {'测试1': 200, '测试2': 300, '测试3': 456, '测试4': 888, '测试5': 253}
    plot = PlotQt()
    plot.plot_(data1, label='测试折线', linestyle='-')
    plot.set_fig(title='测试', xlabel='x轴标签', ylabel='y轴标签')
    plot.set_ylimit(100, 1000)
    plot.show()
