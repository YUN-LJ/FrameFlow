import os

import numpy as np
import cv2
import time


class ClippImg:

    def __init__(self):
        # 待处理图像
        self.image_file = str | np.ndarray | list[str | np.ndarray]
        # 当前处理的图像
        self.image = np.ndarray
        self.h = int  # 图像高
        self.w = int  # 图像宽
        self.out_put_dir = str  # 保存路径
        self.file_name = str  # 保存时的文件名
        self.clipp_image = np.ndarray  # 裁剪后的图像
        # 裁剪区域[x,y,h,w]
        self.clipp_input = list[int]

    def set_image_file(self, image_file: str | np.ndarray | list[str | np.ndarray]) -> bool:
        """
        设置待处理图像

        :param image_file:图像路径|ndarray|list
        """
        res = self.open_image(image_file)
        if isinstance(res, bool):
            return False
        elif isinstance(res, tuple):
            if isinstance(image_file, str):
                self.file_name = os.path.basename(image_file)
            self.image_file = image_file
            self.image, self.h, self.w = res
            return True

    def set_clipp_input(self, clipp_input: list[int]) -> bool:
        if self.h is int or self.w is int:
            raise ValueError('图像不合法或没有调用set_image_file方法')
        self.clipp_input = self.clipp_plot(clipp_input, self.h, self.w)
        return True

    @staticmethod
    def open_image(img_input: str | np.ndarray | list[str | np.ndarray]) -> tuple:
        """
        打开图片并验证输入合法性

        :param img_input 输入图像路径或者图像的numpy.ndarray类型
        :return: img, img.shape[0], img.shape[1]
        """
        try:
            # input_status为0时代表输入的是图像路径， 1代表输入的是图像数组, -1代表不支持该输入
            if isinstance(img_input, str):
                img = cv2.imread(img_input, cv2.IMREAD_UNCHANGED)
            elif isinstance(img_input, np.ndarray):
                if len(img_input.shape) == 3 and img_input.shape[-1] <= 4:
                    img = img_input
                else:
                    raise ValueError('不是图像数组')
            else:
                raise TypeError('输入参数不是路径或者np数组')
            return img, img.shape[0], img.shape[1]

        except Exception as e:
            print(e)
            return False

    @staticmethod
    def clipp_plot(clipp_left_up: list[int], h: int, w: int) -> list[int]:
        """
        验证裁剪合法性

        :param clipp_left_up 裁剪左上点的坐标
        :param h 被裁剪图像的高
        :param w 被裁剪图像的宽
        :return: clipp_left_up 返回验证成功并优化的裁剪左上点
        """
        try:
            # 裁剪框的左上点的坐标
            x = clipp_left_up[0]
            y = clipp_left_up[1]

            h1 = clipp_left_up[2] + 1
            w1 = clipp_left_up[3] + 1

            # 判断裁剪是否超过原图
            # print('clipp_left_up', clipp_left_up)
            # print('h', h)
            # print('w', w)
            if x >= w - w1 or y >= h - h1:
                # print("裁剪区域超过原图")
                raise ValueError("裁剪区域超过原图")
            return clipp_left_up
        except ValueError as e:
            print(e)

    def clipp_rectangle_img(self, clipp_input: list[int] = None, save: bool = False) -> np.ndarray:
        """
        裁剪矩形区域

        :param clipp_input 裁剪位置的左上点的x, y坐标，高，宽
        :return: 裁剪后的图像
        """
        # 读取图片并验证输入合法性
        img, img_height, img_width = self.image, self.h, self.w
        # 确保裁剪合法性
        if clipp_input is None and self.clipp_input is not list:
            clipp = self.clipp_input
        else:
            clipp = self.clipp_plot(clipp_input, img_height, img_width)

        if clipp:
            self.clipp_image = img[clipp[1]: clipp[1] + clipp[2], clipp[0]: clipp[0] + clipp[3], :]
            return self.clipp_image
        else:
            print('图像裁剪区域超过源图像')

    def clipp_circle_img(self, img_input: str | np.ndarray | list[str | np.ndarray],
                         clipp_input: list[int]) -> np.ndarray:
        """
        裁剪矩形区域内切圆形区域

        :param img_input 输入图像路径或者图像的numpy.ndarray类型
        :param clipp_input 裁剪矩形的左上点的x, y坐标，高，宽
        :return: 裁剪后的图像
        """
        # 读取图片并验证输入合法性
        img, img_height, img_width = self.open_image(img_input)
        # 确保裁剪合法性
        clipp = self.clipp_plot(clipp_input, img_height, img_width)
        if clipp:
            circle_r = min(clipp[2], clipp[3]) / 2
            # 圆心坐标
            circle_x = clipp[3] / 2
            circle_y = clipp[2] / 2

            circle_alpha = np.ones((clipp[2], clipp[3]))

            for index_y, circle_alpha_y in enumerate(circle_alpha):
                for index_x, _ in enumerate(circle_alpha_y):
                    if (circle_y - index_y) ** 2 + (circle_x - index_x) ** 2 > circle_r ** 2:
                        circle_alpha[index_y][index_x] = 0

            circle_alpha = circle_alpha * 255
            img_alpha = np.concat((img[clipp[1]: clipp[1] + clipp[2], clipp[0]: clipp[0] + clipp[3], :],
                                   circle_alpha[..., np.newaxis]), axis=2)
            return img_alpha
        else:
            print('图像裁剪区域超过源图像')

    # 裁剪自定义圆角
    def clipp_angle_img(self, img_input: str | np.ndarray | list[str | np.ndarray],
                        clipp_input: list[int], angle: int) -> np.ndarray:
        """
        裁剪矩形区域内切圆形区域

        :param img_input 输入图像路径或者图像的numpy.ndarray类型
        :param clipp_input 裁剪矩形的左上点的x, y坐标，高，宽
        :param angle 自定义圆角，数字越大越接近正方形，越小越接近圆形
        :return: 裁剪后的图像
        """
        # 读取图片并验证输入合法性
        img, img_height, img_width = self.open_image(img_input)
        # 确保裁剪合法性
        clipp = self.clipp_plot(clipp_input, img_height, img_width)
        if clipp:
            circle_r = min(clipp[2], clipp[3]) / 2
            # 圆心坐标
            circle_x = clipp[3] / 2
            circle_y = clipp[2] / 2

            circle_alpha = np.ones((clipp[2], clipp[3]))

            for index_y, circle_alpha_y in enumerate(circle_alpha):
                for index_x, _ in enumerate(circle_alpha_y):
                    if (circle_y - index_y) ** (2 * angle) + (circle_x - index_x) ** (2 * angle) > circle_r ** (
                            2 * angle):
                        circle_alpha[index_y][index_x] = 0

            circle_alpha = circle_alpha * 255
            img_alpha = np.concat((img[clipp[1]: clipp[1] + clipp[2], clipp[0]: clipp[0] + clipp[3], :],
                                   circle_alpha[..., np.newaxis]), axis=2)

            return img_alpha
        else:
            print('图像裁剪区域超过源图像')

    def save_(self, dir_path: str, file_name: str = None):
        if file_name is None:
            file_name = self.file_name
            out_file = os.path.join(dir_path, file_name)
        cv2.imwrite(out_file, self.clipp_image)


if __name__ == '__main__':
    start = time.time()
    image_file = r'E:\code\Python\test_feijian\data\123.jpg'
    a = ClippImg()
    # 设置待处理图像
    a.set_image_file(image_file)

    # 设置裁剪区域
    clipp_input = [0, 0, 3000, 3000]
    a.set_clipp_input(clipp_input)

    # # 裁剪矩形区域
    clipp1 = a.clipp_rectangle_img([0, 0, 1500, 1500])
    cv2.imwrite('./rectangle.jpg', clipp1)
    #
    # # 裁剪圆形区域
    # clipp2 = a.clipp_circle_img('./data/123.jpg', [0, 0, 3000, 3000])
    # cv2.imwrite('./clipp_img/circle.png', clipp2)

    # # 裁剪圆角区域
    # clipp3 = a.clipp_angle_img('./data/123.jpg', [0, 0, 3000, 3000], 10)
    # cv2.imwrite('./clipp_img/clipp_angle.png', clipp3)

    print(f'{time.time() - start}s')
