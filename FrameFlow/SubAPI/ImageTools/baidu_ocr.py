"----------------------------------------------------------------------------"

# acess_token 大概能被设计成读写锁的形式？只有一个写锁，其余都是读锁？还是说没必要，因为在同一个进程中，分出线程，并各自管理session
import logging
import sys
import threading
from pathlib import Path
from typing import ClassVar

import requests

from FrameFlow.SubAPI.ImageTools.auth import AccessTokenManager
from FrameFlow.SubAPI.ImageTools.config import EditConfig, OCRPostConfig
from FrameFlow.SubAPI.ImageTools.exception import APIError, NetworkError

sys.path.insert(
    0, r"D:\WorkDirectory\PythonProject\FrameFlow"
)  # 往上找到 PythonProject
# 必须先修改 LogConfig 的三个值，然后才能导入任何依赖 Fun.BaseTools 的模块
from Fun.BaseTools.LogClass import LogConfig

LogConfig.LOG_DIR = Path.cwd() / "config"  # 改到当前目录下的 config
LogConfig.LOG_FILE = LogConfig.LOG_DIR / "app.log"
LogConfig.ERROR_LOG_FILE = LogConfig.LOG_DIR / "error.log"

from Fun.BaseTools.AsyncHTTP import AsyncHTTPManage

logger = logging.getLogger(__name__)


class OCRBase:
    """OCR基类"""

    OCR_ERR_DICT: ClassVar[dict] = {
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
        url: str,
        access_token_manager: AccessTokenManager,
        headers: dict | None = None,
        payload: dict | None = None,
        params: dict | None = None,
        timeout: tuple[int, int] | None = None,
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

    async def get_access_token(self) -> str:
        return await self.access_token_manager.get_valid_token()

    def get_ocr_response(self) -> requests.Response:
        return ...

    def get_ocr_error_msg(self, err_code: int) -> str:
        return self.OCR_ERR_DICT.get(err_code)


class GeneralOCR:
    def __init__(
        self,
        img_base64,
        access_token_manager: AccessTokenManager,
        post_config: OCRPostConfig,
        http_manager: AsyncHTTPManage,
        edit_config:EditConfig
    ):
        """创建通用OCR识别对象，能够基于post_config创建新的复制，并得到响应"""
        self.access_token_manager = access_token_manager
        self.http_manager = http_manager
        self.data = img_base64
        self.post_config = post_config.clone(self.data)  # 需要保留的对象，会在后续转发二次识别时使用
        self.edit_config = edit_config
    async def recognize(self):
        """识别图片中的文字"""
        # self.post_dict = await self.post_config.build_request(self.access_token_manager)
        # # response = requests.post(**self.post_dict)
        # # 4. 使用 aiohttp 异步发送 POST 请求
        # # async with aiohttp.ClientSession() as session:
        # #     async with session.post(**self.post_dict
        # #     ) as response:
        # #         # 异步读取并解析 JSON 响应
        # #         return await response.json()
        # async with aiohttp.ClientSession() as session, session.post(**self.post_dict) as response:
        #     return await response.json()

        # 1. 速率限制检查
        if not await self.http_manager.wait_for_rate_limit(parent_task=None):
            # 如果返回 False 通常意味着父任务停止，此处可处理
            raise RuntimeError("Task stopped due to rate limit interruption")
        # 2. 构建请求
        post_dict = await self.post_config.build_request(self.access_token_manager)

        # 3. 使用管理器的 session 发送请求
        async with self.http_manager.session.post(**post_dict) as response:

            # 检查HTTP状态码
            if response.status != 200:
                logger.warning(f"HTTP通信失败，状态码{response.status}")
                raise NetworkError(f"HTTP{response.status}")
            data = await response.json()
            general_result = self.parse_api_response(data)
            return await self.auto_transfer(general_result)

    def parse_api_response(self,response:dict)->dict:
        # 错误码处理
        if "error_msg" in response:
            # error_msg = response["error_msg"]
            logger.warning(f"成功通信但执行失败，返回消息{response["error_msg"]}，错误代码{response["error_code"]}")
            raise APIError(response["error_code"],response["error_msg"])
        return self.extract_result(response)
    def extract_result(self,response:dict)->list:
        # 根据editconfig，读结果
        return [item.get("words")    for item in response.get("words_result",[])]

    async def auto_transfer(self,result:list[str])->tuple[str,dict|list]:
        id_keywords = {"身份证", "居民身份证", "姓名", "性别", "民族", "住址", "公民身份号码"}
        bank_keywords = {"银行卡", "信用卡", "卡号", "有效期", "银联", "借记卡"} 
        full_text = "".join(result)
        if any(kw in full_text for kw in id_keywords):
            data = await self.recognize_as_idcard()   # 返回 dict
            return ('idcard', data)
        if any(kw in full_text for kw in bank_keywords):
            data = await self.recognize_as_bankcard() # 返回 dict
            return ('bankcard', data)
        return ('general', result)

    async def recognize_as_idcard(self):
        return await BaiduIDCardOCR(
            self.post_config,
            self.access_token_manager,
            self.http_manager,
            self.edit_config
        ).recognize()

    async def recognize_as_bankcard(self):
        return await BaiduBankCardOCR(
            self.post_config,
            self.access_token_manager,
            self.http_manager,
            self.edit_config
        ).recognize()


class BaiduBankCardOCR:
    """百度银行卡识别类"""

    def __init__(
        self,
        general_post_config: OCRPostConfig,
        access_token_manager: AccessTokenManager,
        http_manager: AsyncHTTPManage,
        edit_config:EditConfig
    ):
        self.post_config = general_post_config.as_bankcard()
        self.access_token_manager = access_token_manager
        self.http_manager = http_manager
        self.edit_config = edit_config

    async def recognize(self):
        if not await self.http_manager.wait_for_rate_limit(parent_task=None):
            # 如果返回 False 通常意味着父任务停止，此处可处理
            raise RuntimeError("Task stopped due to rate limit interruption")
        # 2. 构建请求
        post_dict = await self.post_config.build_request(self.access_token_manager)

        # 3. 使用管理器的 session 发送请求
        async with self.http_manager.session.post(**post_dict) as response:

            # 检查HTTP状态码
            if response.status != 200:
                logger.warning(f"HTTP通信失败，状态码{response.status}")
                raise NetworkError(f"HTTP{response.status}")
            data = await response.json()
            return self.parse_api_response(data)

    def parse_api_response(self,response:dict)->dict:
        # 错误码处理
        if "error_msg" in response:
            # error_msg = response["error_msg"]
            logger.warning(f"成功通信但执行失败，返回消息{response["error_msg"]}，错误代码{response["error_code"]}")
            raise APIError(response["error_code"],response["error_msg"])
        return self.extract_result(response)
    def extract_result(self,response:dict)->dict:
        # 根据editconfig，读结果
        
        result = {}
        for display_name,api_key in self.edit_config.get_bankcard_mapping():
            result[display_name]=response.get("result",{}).get(api_key,"error_result")
        return result



class BaiduIDCardOCR:
    """百度身份证识别类"""

    def __init__(
        self,
        general_post_config: OCRPostConfig,
        access_token_manager: AccessTokenManager,
        http_manager: AsyncHTTPManage,
        edit_config:EditConfig
    ):
        self.post_config = general_post_config.as_idcard()
        self.access_token_manager = access_token_manager
        self.http_manager = http_manager
        self.edit_config = edit_config

    async def recognize(self) -> dict:
        if not await self.http_manager.wait_for_rate_limit(parent_task=None):
            # 如果返回 False 通常意味着父任务停止，此处可处理
            raise RuntimeError("Task stopped due to rate limit interruption")
        # 2. 构建请求
        post_dict = await self.post_config.build_request(self.access_token_manager)

        # 3. 使用管理器的 session 发送请求
        async with self.http_manager.session.post(**post_dict) as response:

            # 检查HTTP状态码
            if response.status != 200:
                logger.warning(f"HTTP通信失败，状态码{response.status}")
                raise NetworkError(f"HTTP{response.status}")
            data = await response.json()
            return self.parse_api_response(data)

    def parse_api_response(self,response:dict)->dict:
        # 错误码处理
        if "error_msg" in response:
            # error_msg = response["error_msg"]
            logger.warning(f"成功通信但执行失败，返回消息{response["error_msg"]}，错误代码{response["error_code"]}")
            raise APIError(response["error_code"],response["error_msg"])
        return self.extract_result(response)
    def extract_result(self,response:dict)->dict:
        # 根据editconfig，读结果
        
        result = {}
        for display_name,api_key in self.edit_config.get_idcard_mapping():
            result[display_name]=response.get("words_result",{}).get(api_key,"error_result")
        return result
