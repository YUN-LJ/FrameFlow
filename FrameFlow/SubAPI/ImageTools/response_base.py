from Fun.BaseTools import AsyncHTTPManage, AsyncJson, Task
from typing import Optional, Any
from payload_base import PayloadBase
class OCRBase(AsyncJson):
    """OCR识别接口"""
    async_http_manage: Optional[AsyncHTTPManage] = None

    def __init__(self,
                 url,
                 payload: PayloadBase,
                 task_manage: AsyncHTTPManage = None,
                 headers: dict[str, Any] = None):
        if self.__class__.async_http_manage is None:
            self.__class__.async_http_manage = AsyncHTTPManage(Config.QPS)
        task_manage = task_manage or self.async_http_manage
        # 请求地址
        self.url = url + get_access_cache_token()
        self.payload = payload
        super().__init__(
            self.url, task_manage,
            headers=headers or Config.HEADERS,
            method="POST")

    def set_image_path(self, image_path: str):
        """加载本地图片"""
        self.payload.set_image(get_file_content_as_base64(image_path))

    def set_image(self, image_base64: str):
        """设置base64编码图片"""
        self.payload.set_image(image_base64)

    def start(self, timeout: float | int = None, priority: int = 5,
              parent_task: 'Task' = None, image_path: str = None, image_base64: str = None) -> Any | bool:
        """获取图像识别结果,结果自动转换"""
        if image_base64 and image_path:
            raise ValueError('image_path和image_base64不能同时存在')
        elif image_path:
            self.set_image_path(image_path)
        elif image_base64:
            self.set_image(image_base64)
        self.set_data(self.payload.get_payload.encode("utf-8"))
        # 执行
        result: Optional[dict] = super().start(timeout, priority, parent_task)
        if result is None:
            return None
        return self.transformation_result(result)

    def transformation_result(self, result: dict) -> dict | None:
        raise NotImplementedError(f'请实现结果转换函数')