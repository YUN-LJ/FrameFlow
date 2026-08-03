"""文字OCR识别接口"""
from typing import Optional, Any
from Fun.BaseTools import AsyncHTTPManage, AsyncJson, Task
from SubAPI.ImageTools.baiduOCR.Tools import *
from Fun.BaseTools import LogClass

logger = LogClass.get_logger(__name__, console_level='WARNING')


class OCRBase(AsyncJson):
    """OCR识别接口"""
    async_http_manage: Optional[AsyncHTTPManage] = None

    def __init__(self,
                 url,
                 payload: Config.PayloadBase,
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


class IDCardOCR(OCRBase):
    """身份证识别"""

    class Payload(Config.PayloadBase):
        """请求参数"""

        def __init__(self):
            super().__init__()
            self.id_card_side = 'id_card_side=front'
            self.detect_ps = 'detect_ps=false'
            self.detect_risk = 'detect_risk=false'
            self.detect_quality = 'detect_quality=false'
            self.detect_photo = 'detect_photo=false'
            self.detect_card = 'detect_card=false'
            self.detect_direction = 'detect_direction=true'
            self.detect_screenshot = 'detect_screenshot=false'

    def __init__(self, task_manage: AsyncHTTPManage = None, headers: dict[str, Any] = None):
        super().__init__(
            Config.API_URL_IDCARD,
            self.Payload(),
            task_manage,
            headers
        )

    def transformation_result(self, result: dict) -> dict | None:
        content: Optional[dict] = result.get("words_result", None)
        if content is not None:
            try:
                transformation_result = {
                    '姓名': content['姓名']['words'],
                    '性别': content['性别']['words'],
                    '出生': content['出生']['words'],
                    '民族': content['民族']['words'],
                    '住址': content['住址']['words'],
                    '公民身份号码': content['公民身份号码']['words'],
                }
                return transformation_result
            except KeyError:
                return None


class BankCardOCR(OCRBase):
    """银行卡识别"""

    class Payload(Config.PayloadBase):
        """请求参数"""

        def __init__(self):
            super().__init__()
            self.location = 'location=false'
            self.detect_quality = 'detect_quality=false'

    def __init__(self, task_manage: AsyncHTTPManage = None, headers: dict[str, Any] = None):
        super().__init__(
            Config.API_URL_BANKCARD,
            self.Payload(),
            task_manage,
            headers
        )

    def transformation_result(self, result: dict) -> dict | None:
        content: Optional[dict] = result.get("result", None)
        if content is not None:
            transformation_result = {
                '银行卡号': content.get('bank_card_number', ''),
                '银行名称': content.get('bank_name', ''),
                '卡片类型': content.get('card_type', ''),
                '有效期': content.get('valid_date', ''),
            }
            return transformation_result


class GeneralOCR(OCRBase):
    """通用OCR识别,返回每一段字符内容"""

    class Payload(Config.PayloadBase):
        """请求参数"""

        def __init__(self):
            super().__init__()
            self.detect_direction = 'detect_direction=true'
            self.detect_language = 'detect_language=false'
            self.paragraph = 'paragraph=false'
            self.probability = 'probability=false'

    def __init__(self, task_manage: AsyncHTTPManage = None, headers: dict[str, Any] = None):
        super().__init__(
            Config.API_URL_GENERAL,
            self.Payload(),
            task_manage,
            headers
        )

    def transformation_result(self, result: dict) -> str | None:
        content: Optional[dict] = result.get("words_result", None)
        return '\n'.join([words['words'] for words in content])


def check_image_is_IDCard(image_path: str = None, image_base64: str = None) -> bool:
    """检查图片是否是身份证"""
    ocr = GeneralOCR()
    result = ocr.start(timeout=10, image_path=image_path, image_base64=image_base64)
    keywords = ['姓名', '性别', '民族', '出生', '公民身份号码']
    return all(kw in result for kw in keywords)


def check_image_is_BankCard(image_path: str = None, image_base64: str = None) -> bool:
    """检查图片是否是银行卡"""
    ocr = BankCardOCR()
    result = ocr.start(timeout=10, image_path=image_path, image_base64=image_base64)
    keywords = ['银行卡', '卡号', '有效期', '发卡行', '借记卡', '信用卡', 'ABC', 'ATM', '银行']
    return all(kw in result for kw in keywords)


def start():
    ocr = GeneralOCR()
    # 需要替换为实际的图片路径
    print(ocr.start(
        timeout=10,
        image_path=r"E:\user_file\download\IMG_20260326_151150.jpg")
    )


if __name__ == '__main__':
    # from SubAPI import StartAPI, StartEnum
    #
    # start_api = StartAPI(
    #     ui_type=StartEnum.UI.CMD,
    #     func=start,
    #     console_level=StartEnum.LogLevel.DEBUG)
    start()
