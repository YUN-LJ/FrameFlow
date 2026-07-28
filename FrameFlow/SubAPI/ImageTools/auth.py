import asyncio
import random
import time

from Fun.BaseTools.AsyncHTTP import AsyncHTTPManage


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