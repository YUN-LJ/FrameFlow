"""底层工具"""

import base64
import getpass

import keyring


def image2base64(img_bytes: bytes) -> str:
    """直接将图片数据转换为base64字符串"""
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    return img_base64


def load_image_as_base64(file_path: str) -> str:
    """将文件路径对应的文件转换成base64字符串"""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def input_keys() -> None:
    """进行一次百度OCRKeys的输入，重复输入则覆盖"""
    if check_keys():
        print("有已保存的Key，继续输入则会覆盖")
        confirm = input("是否继续？(y/n)").strip().lower()
        if confirm != "y":
            print("取消操作")
            return
    api_key = getpass.getpass("请输入 ApiKey：")
    secret_key = getpass.getpass("请输入 SecretKey：")

    # 简单非空校验
    if not api_key or not secret_key:
        print("ApiKey和SecretKey不得为空，请重新输入")

    keyring.set_password("baidu_ocr", "api_key", api_key)
    keyring.set_password("baidu_ocr", "secret_key", secret_key)
    print("Key保存成功")


def check_keys() -> bool:
    """检查使用的百度OCRKey是否存在"""
    api_key = keyring.get_password("baidu_ocr", "api_key")
    secret_key = keyring.get_password("baidu_ocr", "secret_key")
    return bool(api_key and secret_key)
