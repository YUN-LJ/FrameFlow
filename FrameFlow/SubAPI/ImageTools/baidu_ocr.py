'----------------------------------------------------------------------------'
# acess_token 大概能被设计成读写锁的形式？只有一个写锁，其余都是读锁？还是说没必要，因为在同一个进程中，分出线程，并各自管理session
import sys
from pathlib import Path
import threading
import time
from typing import Any, List, Tuple
from dataclasses import dataclass
import requests

import random
import asyncio
import logging


sys.path.insert(0,r'D:\WorkDirectory\PythonProject\FrameFlow')  # 往上找到 PythonProject
# 必须先修改 LogConfig 的三个值，然后才能导入任何依赖 Fun.BaseTools 的模块
from Fun.BaseTools.LogClass import LogConfig
LogConfig.LOG_DIR = Path.cwd() / 'config'           # 改到当前目录下的 config
LogConfig.LOG_FILE = LogConfig.LOG_DIR / 'app.log'
LogConfig.ERROR_LOG_FILE = LogConfig.LOG_DIR / 'error.log'

from Fun.BaseTools.AsyncHTTP import AsyncJson, Task,aiohttp,AsyncHTTPManage

logger = logging.getLogger(__name__)

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
class ImageLoader:
    @staticmethod
    def load(filepath)->bytes:
        """从普通图片文件加载二进制数据"""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"图片文件不存在: {filepath}")
        with open(path, 'rb') as f:
            return f.read()
    def load_into_self(self) -> bytes:
        """将图片数据加载到 self.data 并返回"""
        self.data = self.load(self.filepath)
        return self.data
class ImageLoader2:
    """从 Excel (.xlsx) 的指定工作表中提取所有浮动图片的二进制数据"""

    def __init__(self, xlsx_path: str):
        """
        :param xlsx_path: Excel 文件路径
        """
        self.xlsx_path = Path(xlsx_path)
        if not self.xlsx_path.exists():
            raise FileNotFoundError(f"Excel 文件不存在: {xlsx_path}")
        # 可以在这里初始化提取器（延迟加载也可以）
        self._extractor = None  # 懒加载

    def _get_extractor(self):
        if self._extractor is None:
            # 假设你的 ExcelImageExtractor 在当前作用域可用
            # 如果不在同一个文件，请导入：from your_module import ExcelImageExtractor
            from extractor import ExcelImageExtractor  # 修改为实际导入路径
            self._extractor = ExcelImageExtractor(self.xlsx_path)
        return self._extractor

    def get_float_images(self, sheet_name: str) -> List[Tuple[int, bytes]]:
        """
        获取指定工作表中所有的浮动图片（按行号排序）
        :param sheet_name: 工作表名称
        :return: 列表，元素为 (行号, 图片二进制数据)  行号从1开始
        """
        extractor = self._get_extractor()
        # 假设 extractor.get_float_images 返回 List[Tuple[int, bytes]]
        images = extractor.get_float_images(sheet_name)
        if not images:
            logger.info(f"工作表 '{sheet_name}' 中没有找到浮动图片")
            return []
        # 按行号排序，保证稳定性
        images.sort(key=lambda x: x[0])
        return images
        


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
    OCR_ERR_DICT = {
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
    def __init__(
        self,
        url:str,
        access_token_manager :AccessTokenManager,
        headers: dict = None,
        payload: dict = None,
        params: dict = None,
        timeout: Tuple[int, int] = None,
        session: requests.Session = None,
        enable_rate_limit: bool = True,
        rate_limit_per_sec: int = 2,
    ):
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
    

class BankcardOCR:
    """身份证OCR类"""
    # Payload类需求
    # image图片文件：不提供默认值
    # url：不提供默认值
    # location: 基本类型，不进行配置
    # detect_quality:基本类型，不进行配置
    # 额外需求：本地文件的文件路径，用于从本地读取图片

    # 




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
    @dataclass
    class Payload(BasePayload):
        image:str
        """图像数据，base64编码后进行urlencode，需去掉编码头data:image/jpeg;base64"""
        url:str 
        """图片完整URL，URL长度不超过1024字节 当image字段存在时url字段失效 请注意关闭URL防盗链"""
        location:bool  = False
        """是否返回银行卡号的字段位置坐标，默认为 false"""
        detect_quality:bool = False
        """是否开启银行卡质量类型（清晰模糊、边框/四角不完整）检测功能，默认不开启"""
        
        def to_request_dict(self)->dict:
            """将Payload转换为API所需的字典格式"""
            result = {
                "location":self._bool2str(self.location),
                "detect_quality":self._bool2str(self.detect_quality)
            }
            if self.image:
                result["image"] = self._img2base64(self.image)
            elif self.url:
                result["url"] = self.url
            else:
                raise ValueError("至少提供image或url中的一个参数")
            return result
        
    def __init__(
        self,
        url: str,
        headers: dict = None,
        payload: dict = None,
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
        :param payload:                     请求体（POST 提交的 JSON 或表单数据）
        :param params:                   URL 查询参数字典（GET 方式的固定参数）
        :param timeout:                  超时 (connect, read)，默认使用类常量
        :param session:                  可复用的 requests.Session
        :param access_token:  传递 access_token 的 query 参数名
        :param enable_rate_limit:        是否启用限流
        :param rate_limit_per_sec:       每秒最大请求数（限流用）
        """
        self.url = url.rstrip('/')
        self.headers = headers or {"content-type": "application/x-www-form-urlencoded"}
        self.payload = self.Payload()
        self.params = params or config.params
        self.timeout = timeout or config.DEFAULT_TIMEOUT
        self.session = session or requests.Session()
        self.access_token = None
        
        # 限流相关（线程安全）
        self.enable_rate_limit = enable_rate_limit
        self.rate_limit_per_sec = rate_limit_per_sec
        self._last_request_time = 0
        self._rate_lock = threading.Lock()
    def lumbda1(self,img_base64):

        request_url = f"{self.url}?{self.params.__repr__()}"
        response = self.session.post(
            request_url, data=self.payload, headers=self.headers, timeout=(5, 10)
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