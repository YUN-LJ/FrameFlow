"""百度OCR工具类"""
import base64
import urllib
import requests
from SubAPI.ImageTools.baiduOCR import BaiduConfig as Config
from Fun.BaseTools import LogClass

logger = LogClass.get_logger(__name__, console_level='WARNING')


def get_access_token() -> str:
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials",
              "client_id": Config.API_KEY,
              "client_secret": Config.SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


def get_access_cache_token() -> str:
    """获取缓存的token"""
    if not Config.TOKEN:
        Config.TOKEN = get_access_token()
    return Config.TOKEN


def get_file_content_as_base64(path, urlencoded=True) -> str:
    """
    获取文件base64编码
    :param path: 文件路径
    :param urlencoded: 是否对结果进行urlencoded
    :return: base64编码信息
    """
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content


def get_image_OCR(url: str, payload: Config.PayloadBase) -> dict:
    """获取图像识别结果"""
    response = requests.request(
        "POST", url,
        headers=Config.HEADERS,
        data=payload.get_payload.encode("utf-8"))
    return response.json()
