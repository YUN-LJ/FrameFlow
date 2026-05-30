# import threading
# import time
# import logging
# from typing import Optional, Tuple
# import requests
# from config import 
# # 配置日志
# logging.basicConfig(
#     level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)


# def _get_access_token(api_key, secret_key):
#     """获取百度OCR access_token"""
#     url = "https://aip.baidubce.com/oauth/2.0/token"
#     data = {
#         "grant_type": "client_credentials",
#         "client_id": api_key,
#         "client_secret": secret_key,
#     }
#     response = session.post(url, data=data, timeout=(5, 10))
#     if response.status_code == 200:
#         result = response.json()
#         return result.get("access_token")
#     else:
#         raise Exception(f"获取token失败，状态码：{response.status_code}")


# def get_cached_access_token():
#     """获取缓存的token，若过期则重新获取"""
#     now = time.time()
#     if _token_cache["token"] and _token_cache["expires_at"] > now + 60:
#         return _token_cache["token"]
#     token = _get_access_token(__API_KEY, __SECRET_KEY)
#     _token_cache["token"] = token
#     _token_cache["expires_at"] = now + 2592000  # 30天
#     return token


# def general_ocr(img_base64, access_token):
#     _rate_limit()
#     request_url_base = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
#     request_url = request_url_base + "?access_token=" + access_token
#     params = {
#         "image": img_base64,
#         "detect_direction": "true",
#         # 'probability':'true'
#     }
#     headers = {"content-type": "application/x-www-form-urlencoded"}
#     response = session.post(request_url, data=params, headers=headers, timeout=(5, 10))
#     if response.status_code == 200:
#         result = response.json()
#         if "error_code" in result:
#             # API 返回错误
#             error_code = result.get("error_code")
#             error_msg = result.get("error_msg")
#             logger.error(
#                 f"通用OCR识别失败，error_code={error_code}，error_msg={error_msg}"
#             )
#             return None
#         words_list = result.get("words_result", [])
#         full_text = "".join(item["words"] for item in words_list)
#         idcard_keywords = ["姓名", "性别", "民族", "出生", "公民身份号码"]
#         if any(kw in full_text for kw in idcard_keywords):
#             logger.info("检测到身份证特征，调用身份证OCR")
#             id_result = _idcard_ocr(img_base64, access_token)
#             if id_result:
#                 return {"type": "idcard", "data": id_result}
#         bank_keywords = [
#             "银行卡",
#             "卡号",
#             "有效期",
#             "发卡行",
#             "借记卡",
#             "信用卡",
#             "ABC",
#             "ATM",
#             "银行",
#         ]
#         if any(kw in full_text for kw in bank_keywords):
#             logger.info("检测到银行卡特征，调用银行卡OCR")
#             bank_result = _bankcard_ocr(img_base64, access_token)
#             if bank_result:
#                 return {"type": "bankcard", "data": bank_result}
#         return {"type": "general", "data": {"text": full_text[:200]}}

#     else:
#         logger.error(f"请求失败，错误原因status_code = {response.status_code}")
#         return None


# def _idcard_ocr(img_base64, access_token):
#     _rate_limit()
#     request_url_base = "https://aip.baidubce.com/rest/2.0/ocr/v1/idcard"
#     params = {"id_card_side": "front", "image": img_base64}
#     request_url = request_url_base + "?access_token=" + access_token
#     headers = {"content-type": "application/x-www-form-urlencoded"}
#     response = session.post(request_url, data=params, headers=headers, timeout=(5, 10))
#     if response.status_code == 200:
#         result = response.json()
#         if "error_code" in result:
#             # API 返回错误
#             error_code = result.get("error_code")
#             error_msg = result.get("error_msg")
#             logger.error(
#                 f"身份证OCR识别失败，error_code={error_code}，error_msg={error_msg}"
#             )
#             return None
#         words_result = result.get("words_result", {})
#         return (
#             words_result.get("住址", {}).get("words"),
#             words_result.get("公民身份号码", {}).get("words"),
#             words_result.get("出生", {}).get("words"),
#             words_result.get("姓名", {}).get("words"),
#             words_result.get("性别", {}).get("words"),
#             words_result.get("民族", {}).get("words"),
#         )
#     else:
#         logger.error(f"身份证OCR请求失败，错误原因status_code = {response.status_code}")
#         return None
'----------------------------------------------------------------------------'
# acess_token 大概能被设计成读写锁的形式？只有一个写锁，其余都是读锁？还是说没必要，因为在同一个进程中，分出线程，并各自管理session
import sys
from pathlib import Path
import threading
import time
from typing import Tuple
import inspect
import requests

import random
import asyncio
from logging import Logger


sys.path.insert(0,r'D:\WorkDirectory\PythonProject\FrameFlow')  # 往上找到 PythonProject
# 必须先修改 LogConfig 的三个值，然后才能导入任何依赖 Fun.BaseTools 的模块
from Fun.BaseTools.LogClass import LogConfig
LogConfig.LOG_DIR = Path.cwd() / 'config'           # 改到当前目录下的 config
LogConfig.LOG_FILE = LogConfig.LOG_DIR / 'app.log'
LogConfig.ERROR_LOG_FILE = LogConfig.LOG_DIR / 'error.log'

from Fun.BaseTools.AsyncHTTP import Task,aiohttp,AsyncHTTPManage

logger = Logger(__name__)
class AsyncJson(Task):
    """异步请求Json文件"""

    def __init__(self, url: str, async_manager: 'AsyncHTTPManage', params: dict = None,
                 headers: dict = None, timeout: aiohttp.ClientTimeout = None, retry_count=3):
        """
        异步获取Json文件
        :param url: 请求的URL
        :param params:请求参数
        :param async_manager:异步请求管理类
        :param headers: 请求头,默认无
        :param timeout: 超时时间,默认请查看AsyncHTTPManage.default_timeout设置
        """
        super().__init__(self.__execute, async_manager)
        self.url = url
        self.params = params
        self.headers = headers
        self.async_manager = async_manager
        self.retry_count = retry_count
        self.timeout = async_manager.default_timeout if timeout is None else timeout
        # 请求后的状态和结果
        self.status_code = 0

    @property
    def request_args(self) -> dict:
        """实际请求时的关键词参数"""
        return {'headers': self.headers, 'params': self.params, 'timeout': self.timeout}

    async def __execute(self) -> dict:
        """异步请求,无结果时返回空字典"""
        retry_count = 0  # 当前重试次数
        kwargs = self.request_args  # 请求参数
        session = self.async_manager.session  # 连接对象
        tetry_time = round(random.uniform(*self.async_manager.default_retry_time), 2)  # 重试等待时间
        while self.isRunning and retry_count < self.retry_count:
            try:
                # 遵循任务池速率限制
                if not await self.async_manager.wait_for_rate_limit(self):
                    return {}
                async with session.get(self.url, **kwargs) as response:
                    self.status_code = response.status
                    if self.status_code == 200:
                        return await response.json()
            except Exception as e:
                retry_count += 1
                logger.warning(f"{self.__class__.__name__} 第{retry_count}次请求失败: "
                               f"{self.url} {tetry_time}秒后重试 错误: {e}")
            await asyncio.sleep(tetry_time)
        return {}


# i = AsyncJson("", AsyncHTTPManage())
# public_names = [name for name in dir(i) if not name.startswith('_')]

# for name in public_names:
#     attr = getattr(i, name)
#     if callable(attr):
#         print(f"方法: {name}")
#     else:
#         print(f"属性: {name}")
# exit()
class AccessTokenManager:
    def __init__(self,http_client:AsyncHTTPManage,api_url,api_key,secret_key):
        self._http = http_client
        self.__api_url = api_url or config.ACCESS_POST_URL
        self.__api_key = api_key or config.API_KEY
        self.__secret_key = secret_key or config.SECRET_KEY
        self.__token = None
        self.__expires_at = 0
        self.__lock = asyncio.Lock()
    async def get_valid_token(self):
        async with self.__lock():
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
                

                  

        
class OCRBase:
    # def __init__(self, url: str, async_manager: 'AsyncHTTPManage', params: dict = None,
    #              headers: dict = None, timeout: aiohttp.ClientTimeout = None, retry_count=3):
    #     """
    #     异步获取Json文件
    #     :param url: 请求的URL
    #     :param params:请求参数
    #     :param async_manager:异步请求管理类
    #     :param headers: 请求头,默认无
    #     :param timeout: 超时时间,默认请查看AsyncHTTPManage.default_timeout设置
    #     """
    #     super().__init__(self.__execute, async_manager)
    #     self.url = url
    #     self.params = params
    #     self.headers = headers
    #     self.async_manager = async_manager
    #     self.retry_count = retry_count
    #     self.timeout = async_manager.default_timeout if timeout is None else timeout
    #     # 请求后的状态和结果
    #     self.status_code = 0
    def __init__(
        self,
        url:str,
        access_token :str,
        headers: dict = None,
        data: dict = None,
        params: dict = None,
        timeout: Tuple[int, int] = None,
        session: requests.Session = None,

        enable_rate_limit: bool = True,
        rate_limit_per_sec: int = 2,
        # 需要传入的参数
        
    ):
        self.session = session or requests.Session()
        
        # 限流相关（线程安全）
        self.enable_rate_limit = enable_rate_limit
        self.rate_limit_per_sec = rate_limit_per_sec
        self._last_request_time = 0
        self._rate_lock = threading.Lock()
        super().__init__(self, url, async_manager, params,headers, timeout, retry_count=3)
    pass
class BankcardOCR:
    """身份证OCR类"""
    # 类常量 - 可配置的固定文本项
    DEFAULT_TIMEOUT = (5, 10)          # (连接超时, 读取超时)
    DEFAULT_CONTENT_TYPE = "application/x-www-form-urlencoded"
    PAYLOAD_KEY_IMAGE = "image"
    
    # 响应字段映射（可根据不同 API 提供商调整）
    RESPONSE_ERROR_CODE_KEY = "error_code"
    RESPONSE_ERROR_MSG_KEY = "error_msg"
    RESPONSE_RESULT_KEY = "result"
    
    # 结果字段提取键名
    FIELD_BANK_CARD_NUMBER = "bank_card_number"
    FIELD_VALID_DATE = "valid_date"
    FIELD_BANK_CARD_TYPE = "bank_card_type"
    FIELD_BANK_NAME = "bank_name"
    FIELD_HOLDER_NAME = "holder_name"
    
    # 可选：重试次数
    MAX_RETRIES = 3

    def __init__(
        self,
        url: str,
        headers: dict = None,
        data: dict = None,
        params: dict = None,
        timeout: Tuple[int, int] = None,
        session: requests.Session = None,
        # 额外配置参数
        access_token_param_name: str = "access_token",   # query string 中 token 的参数名
        enable_rate_limit: bool = True,
        rate_limit_per_sec: int = 2,
    ):
        """
        初始化银行卡OCR类

        :param url:                      API 基础地址（不含 query string）
        :param headers:                  请求头（如 API Key）
        :param data:                     请求体（POST 提交的 JSON 或表单数据）
        :param params:                   URL 查询参数字典（GET 方式的固定参数）
        :param timeout:                  超时 (connect, read)，默认使用类常量
        :param session:                  可复用的 requests.Session
        :param access_token_param_name:  传递 access_token 的 query 参数名
        :param enable_rate_limit:        是否启用限流
        :param rate_limit_per_sec:       每秒最大请求数（限流用）
        """
        self.url = url.rstrip('/')
        self.headers = headers or {"content-type": "application/x-www-form-urlencoded"}
        self.data = data or {}
        self.params = params or {}
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.session = session or requests.Session()
        self.access_token_param_name = access_token_param_name
        
        # 限流相关（线程安全）
        self.enable_rate_limit = enable_rate_limit
        self.rate_limit_per_sec = rate_limit_per_sec
        self._last_request_time = 0
        self._rate_lock = threading.Lock()
    def _bankcard_ocr(self,img_base64, access_token):

        payload = {"image": img_base64}
        request_url = self.url + self.params.xxx()
        response = self.session.post(
            request_url, data=payload, headers=self.headers, timeout=(5, 10)
        )
        return response
    def response_handle(self,jsonobject):
        """这个函数能够复用，提取到父类"""
        if jsonobject.status_code == 200:
            result = jsonobject.json()
            if "error_code" in result:
                # API 返回错误
                error_code = result.get("error_code")
                error_msg = result.get("error_msg")
                logger.error(
                    f"银行卡OCR识别失败，error_code={error_code}，error_msg={error_msg}"
                )
                return None
            else:
                return self.exactor_text("XXX")
        else:
            logger.error(
                f"银行卡OCR请求失败，错误原因status_code = {jsonobject.status_code}"
            )
            return None
    def exactor_text(self,jsonobject):
            _result = result.get("result", {})
            return (
                _result.get("bank_card_number"),
                _result.get("valid_date"),
                _result.get("bank_card_type"),
                _result.get("bank_name"),
                _result.get("holder_name"),
            )
    
    def _ratelimit(self):
        """线程安全的速率限制"""
        if not self.enable_rate_limit:
            return
        with self._rate_lock:
            import time
            now = time.monotonic()
            elapsed = now - self._last_request_time
            interval = 1.0 / self.rate_limit_per_sec
            if elapsed < interval:
                time.sleep(interval - elapsed)
            self._last_request_time = time.monotonic()
    
    def _build_request_url(self, access_token: str) -> str:
        """构建完整的请求 URL（包括固定 params 和 access_token）"""
        # 合并固定参数和动态 token
        query_params = dict(self.params)
        if access_token:
            query_params[self.access_token_param_name] = access_token
        # 生成 query string
        if query_params:
            import urllib.parse
            query_string = urllib.parse.urlencode(query_params)
            return f"{self.url}?{query_string}"
        return self.url
    
    def _bankcard_ocr(
        self, 
        img_base64: str, 
        access_token: str
    ) -> Optional[Tuple[str, str, str, str, str]]:
        """
        同步 OCR 识别（线程安全）
        返回: (卡号, 有效期, 卡片类型, 银行名称, 持卡人姓名)
        """
        self._ratelimit()
        
        # 构造请求 body
        payload = {self.PAYLOAD_KEY_IMAGE: img_base64}
        request_url = self._build_request_url(access_token)
        headers = {
            "content-type": self.DEFAULT_CONTENT_TYPE,
            **self.headers   # 允许外部覆盖或添加额外的 header
        }
        
        # 使用 Session 发送请求（线程安全）
        try:
            response = self.session.post(
                request_url,
                data=payload,
                headers=headers,
                timeout=self.timeout
            )
        except requests.RequestException as e:
            logger.error(f"银行卡OCR请求异常: {e}")
            return None
        
        if response.status_code != 200:
            logger.error(f"银行卡OCR请求失败，status_code = {response.status_code}")
            return None
        
        result_json = response.json()
        if self.RESPONSE_ERROR_CODE_KEY in result_json:
            error_code = result_json.get(self.RESPONSE_ERROR_CODE_KEY)
            error_msg = result_json.get(self.RESPONSE_ERROR_MSG_KEY)
            logger.error(f"银行卡OCR识别失败，error_code={error_code}，error_msg={error_msg}")
            return None
        
        ocr_result = result_json.get(self.RESPONSE_RESULT_KEY, {})
        return (
            ocr_result.get(self.FIELD_BANK_CARD_NUMBER),
            ocr_result.get(self.FIELD_VALID_DATE),
            ocr_result.get(self.FIELD_BANK_CARD_TYPE),
            ocr_result.get(self.FIELD_BANK_NAME),
            ocr_result.get(self.FIELD_HOLDER_NAME),
        )
    
    # 可选：异步版本（用于协程）
    async def _bankcard_ocr_async(self, img_base64: str, access_token: str):
        """异步 OCR（需配合 aiohttp，且需自己实现异步限流）"""
        # 此处略，如需协程支持，建议单独创建异步类
        pass