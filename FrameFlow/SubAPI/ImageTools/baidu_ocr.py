'----------------------------------------------------------------------------'
# acess_token 大概能被设计成读写锁的形式？只有一个写锁，其余都是读锁？还是说没必要，因为在同一个进程中，分出线程，并各自管理session
import asyncio
import base64
import logging
import random
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

import requests
from utils import check_keys, input_keys

sys.path.insert(0,r'D:\WorkDirectory\PythonProject\FrameFlow')  # 往上找到 PythonProject
# 必须先修改 LogConfig 的三个值，然后才能导入任何依赖 Fun.BaseTools 的模块
from Fun.BaseTools.LogClass import LogConfig
LogConfig.LOG_DIR = Path.cwd() / 'config'           # 改到当前目录下的 config
LogConfig.LOG_FILE = LogConfig.LOG_DIR / 'app.log'
LogConfig.ERROR_LOG_FILE = LogConfig.LOG_DIR / 'error.log'

from Fun.BaseTools.AsyncHTTP import AsyncJson, Task,aiohttp,AsyncHTTPManage

logger = logging.getLogger(__name__)

class AccessTokenManager:
    ACCESS_POST_URL="https://aip.baidubce.com/oauth/2.0/token"
    def __init__(self,http_client:AsyncHTTPManage,api_url,api_key,secret_key):
        self._http = http_client
        self.__api_url = api_url or self.ACCESS_POST_URL
        self.__api_key = api_key or config.API_KEY
        self.__secret_key = secret_key or config.SECRET_KEY
        self.__token = None
        self.__expires_at = 0
        self.__lock = asyncio.Lock()
    async def get_valid_token(self):
        async with self.__lock:
            if self.__token and time.time()+300 < self.__expires_at:
                return self.__token
            await self.__refresh_token()
            return self.__token
    async def __refresh_token(self):
        post_url = f"{self.__api_url}?api_key={self.__api_key}&secret_key={self.__secret_key}"
        headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'            
        }
        max_retries = 3
        for attemp in range(1,max_retries+1):
            # 遵守速率限制（若AsyncHTTPManage启用了rate_limit）
            if not await self._http.wait_for_rate_limit(parent_task=None):
                raise RuntimeError("任务已停止，无法刷新token")
            try:
                async with self._http.session.post(post_url,headers=headers,data="") as resp:
                    if resp.status!=200:
                        raise RuntimeError(f"HTTP {resp.status}")
                    body = await resp.json()
                    if "error_description" in body:
                        err_desc = body.get("error_description")
                        if err_desc == "unknown client id":
                            raise ValueError("API Key不正确")
                        if err_desc == "Client authentication failed":
                            raise ValueError("Secret Key不正确")
                        raise RuntimeError(f"认证错误{err_desc}")
                    if "access_token" not in body:
                        raise RuntimeError("响应中无access_token")
                    self.__token = body.get("access_token")
                    self.__expires_at = time.time()+2592000
                return
            except Exception as e:
                if attemp == max_retries:
                    raise ConnectionError(f"刷新token失败，重试{max_retries}后仍失败：{e}")
                wait_sec = random.uniform(1,2**attemp)
                await asyncio.sleep(wait_sec)
        


class BasePayload:
    def _img2base64(raw:str)->str:
        """
        将提供的图片，转换成需要的格式，存储进返回对象中
        """
        pass
    def _bool2str(v:bool)->str:
        """将bool类型的数值转换成对应的小写字符串"""
        return "true" if v else "false"


        
class OCRBase:
    """OCR基类"""
    OCR_ERR_DICT:ClassVar[dict] = {
        1: "未知错误",
        2: "服务暂不可用",
        3: "不支持的OpenAPI方法",
        4: "集群超限额",
        6: "无权限访问数据",
        14: "IAM鉴权失败",
        17: "每天请求量超限额",
        18: "QPS超限额",
        19: "请求总量超限额",
        100: "无效的参数",
        110: "Access token无效或已失效",
        111: "Access token已过期",
        216100: "请求中包含非法参数",
        216101: "缺少必须的参数",
        216102: "请求了不支持的服务",
        216103: "参数过长",
        216110: "appid不存在",
        216200: "图片为空",
        216201: "图片格式错误",
        216202: "图片大小错误",
        216630: "识别错误",
        216631: "识别银行卡错误",
        216633: "识别身份证错误",
        216634: "检测错误",
        282000: "服务器内部错误",
        282003: "缺少参数: {param}",
        282005: "批量处理错误",
        282006: "批量任务数量超限",
        282110: "URL参数不存在",
        282111: "URL格式非法",
        282112: "URL下载超时",
        282113: "URL返回无效参数",
        282114: "URL长度错误",
        283501: "授权文件不匹配",
        283502: "BundleId不匹配",
        283503: "授权文件不存在",
        283507: "签名MD5不匹配",
        283602: "时间戳不正确",
    }
    """200返回错误码的字典"""
    def __init__(
        self,
        url:str,
        access_token_manager :AccessTokenManager,
        headers: dict = None,
        payload: dict = None,
        params: dict = None,
        timeout: tuple[int, int] = None,
        session: requests.Session = None,
        enable_rate_limit: bool = True,
        rate_limit_per_sec: int = 2,
    ):
        """

        Args:
            url (str): 网络请求地址
            access_token_manager (AccessTokenManager): AccessToken管理器
            headers (dict, optional): 请求头. Defaults to None.
            payload (dict, optional): 携带数据. Defaults to None.
            params (dict, optional): 参数体. Defaults to None.
            timeout (tuple[int, int], optional): 超时设置. Defaults to None.
            session (requests.Session, optional): 会话管理. Defaults to None.
            enable_rate_limit (bool, optional): 限流标识. Defaults to True.
            rate_limit_per_sec (int, optional): 每秒限制请求次数. Defaults to 2.
        """
        self.session = session or requests.Session()
        self.access_token_manager = access_token_manager
        # 限流相关（线程安全）
        self.enable_rate_limit = enable_rate_limit
        self.rate_limit_per_sec = rate_limit_per_sec
        self._last_request_time = 0
        self._rate_lock = threading.Lock()
    async def get_access_token(self)->str:
        return await self.access_token_manager.get_valid_token()
    def get_ocr_response(self)->requests.Response:
        return ...
    def get_ocr_error_msg(self,err_code:int)->str:
        return self.OCR_ERR_DICT.get(err_code)
    

class GeneralOCRConfig:
    # 类常量
    TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
    API_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"

    def __init__(self, api_key: str, secret_key: str):
        # ---------- 实例属性：每个用户独立的凭证 ----------
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None

    def _ensure_token(self):
        """获取或刷新 Access Token"""
        if self.access_token is None:
            # 直接使用类常量 TOKEN_URL
            url = f"{self.TOKEN_URL}?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}"
            response = requests.get(url)
            self.access_token = response.json().get("access_token")

    def recognize(self, image_path: str) -> dict:
        """识别图片中的文字"""
        self._ensure_token()

        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        # 直接使用类常量 API_URL
        full_url = f"{self.API_URL}?access_token={self.access_token}"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'image': image_data, 'language_type': 'CHN_ENG'}

        response = requests.post(full_url, headers=headers, data=data)
        return response.json()

class GeneralOCR(OCRBase):
    def __init__(self, url, access_token_manager, headers = None, payload = None, params = None, timeout = None, session = None, enable_rate_limit = True, rate_limit_per_sec = 2):
        super().__init__(
            url, 
            access_token_manager, 
            headers, 
            payload, 
            params, 
            timeout, 
            session
        )
class BaiduBankCardOCR:
    """百度银行卡识别类"""

    # 类常量
    TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
    API_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/bankcard"

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None

    def _ensure_token(self):
        if self.access_token is None:
            url = f"{self.TOKEN_URL}?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}"
            response = requests.get(url)
            self.access_token = response.json().get("access_token")

    def recognize(self, image_path: str) -> dict:
        self._ensure_token()
        with open(image_path, 'rb') as f:
            image_data = bytes_to_base64(f.read()) # TODO 待修改，适配从压缩文件中读取图片

        full_url = f"{self.API_URL}?access_token={self.access_token}"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'image': image_data}

        response = requests.post(full_url, headers=headers, data=data)
        return response.json()
class BaiduIDCardOCR:
    """百度身份证识别类"""

    # 类常量
    TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
    API_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/idcard"

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None

    def _ensure_token(self):
        if self.access_token is None:
            url = f"{self.TOKEN_URL}?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}"
            response = requests.get(url)
            self.access_token = response.json().get("access_token")

    def recognize(self, image_path: str, side: str = "front") -> dict:
        self._ensure_token()
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        full_url = f"{self.API_URL}?access_token={self.access_token}"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'image': image_data, 'id_card_side': side}

        response = requests.post(full_url, headers=headers, data=data)
        return response.json()