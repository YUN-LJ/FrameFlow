"----------------------------------------------------------------------------"

# acess_token 大概能被设计成读写锁的形式？只有一个写锁，其余都是读锁？还是说没必要，因为在同一个进程中，分出线程，并各自管理session
import asyncio
import logging
import random
import sys
import threading
import time
from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

import requests
import utils

from FrameFlow.SubAPI.ImageTools.config import EditConfig, OCRPostConfig

sys.path.insert(
    0, r"D:\WorkDirectory\PythonProject\FrameFlow"
)  # 往上找到 PythonProject
# 必须先修改 LogConfig 的三个值，然后才能导入任何依赖 Fun.BaseTools 的模块
from Fun.BaseTools.LogClass import LogConfig

LogConfig.LOG_DIR = Path.cwd() / "config"  # 改到当前目录下的 config
LogConfig.LOG_FILE = LogConfig.LOG_DIR / "app.log"
LogConfig.ERROR_LOG_FILE = LogConfig.LOG_DIR / "error.log"

from Fun.BaseTools.AsyncHTTP import AsyncJson, Task, aiohttp, AsyncHTTPManage

logger = logging.getLogger(__name__)


class AccessTokenManager:
    ACCESS_POST_URL = "https://aip.baidubce.com/oauth/2.0/token"

    def __init__(self, http_client: AsyncHTTPManage, api_url, api_key, secret_key):
        self._http = http_client
        self.__api_url = api_url or self.ACCESS_POST_URL
        self.__api_key = api_key or config.API_KEY
        self.__secret_key = secret_key or config.SECRET_KEY
        self.__token = None
        self.__expires_at = 0
        self.__lock = asyncio.Lock()

    async def get_valid_token(self):
        async with self.__lock:
            if self.__token and time.time() + 300 < self.__expires_at:
                return self.__token
            await self.__refresh_token()
            return self.__token

    async def __refresh_token(self):
        post_url = (
            f"{self.__api_url}?api_key={self.__api_key}&secret_key={self.__secret_key}"
        )
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        max_retries = 3
        for attemp in range(1, max_retries + 1):
            # 遵守速率限制（若AsyncHTTPManage启用了rate_limit）
            if not await self._http.wait_for_rate_limit(parent_task=None):
                raise RuntimeError("任务已停止，无法刷新token")
            try:
                async with self._http.session.post(
                    post_url, headers=headers, data=""
                ) as resp:
                    if resp.status != 200:
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
                    self.__expires_at = time.time() + 2592000
                return
            except Exception as e:
                if attemp == max_retries:
                    raise ConnectionError(
                        f"刷新token失败，重试{max_retries}后仍失败：{e}"
                    )
                wait_sec = random.uniform(1, 2**attemp)
                await asyncio.sleep(wait_sec)


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
        path,
        access_token_manager: AccessTokenManager,
        post_config: OCRPostConfig,
        http_manager: AsyncHTTPManage,
    ):
        """创建通用OCR识别对象，能够基于post_config创建新的复制，并得到响应"""
        self.access_token_manager = access_token_manager
        self.http_manager = http_manager
        with open(path, "rb") as f:
            self.data = utils.image2base64(
                f.read()
            )  # TODO 待修改，适配从压缩文件中读取图片
        self.post_config = post_config.clone(
            self.data
        )  # 需要保留的对象，会在后续转发二次识别时使用

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
            return await response.json()


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
            return await response.json()


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

        self._error_dict = {}

    async def recognize(self, image_path: str, side: str = "front") -> dict:
        if not await self.http_manager.wait_for_rate_limit(parent_task=None):
            # 如果返回 False 通常意味着父任务停止，此处可处理
            raise RuntimeError("Task stopped due to rate limit interruption")
        # 2. 构建请求
        post_dict = await self.post_config.build_request(self.access_token_manager)

        # 3. 使用管理器的 session 发送请求
        async with self.http_manager.session.post(**post_dict) as response:
            return await response.json()

    def parse_response(self,response:dict)->dict|None:
        # 错误处理
        if response.status  != '200':
            logger.warning(f"通信失败，返回代码{response.status}")
            raise ConnectionError
        # 错误码处理
        if "error_msg" in response:
            error_code = response["error_msg"]
            logger.warning(f"成功通信但执行失败，返回消息{error_code}，对应问题{self._error_dict[error_code]}")
            raise OperationalError
        return self.extract_result(response)
    def extract_result(self,response:dict):
        # 根据editconfig，读结果
        
        column_name = self.edit_config.get_idcard_extract_keys()
        result = {}
        for item in column_name:
            result[item[1]]=response.getitem(item[2])
        return result
