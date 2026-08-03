"""百度文字识别配置"""
QPS = 2  # 并发限制
# API密钥
API_KEY = ""  # 百度智能云API密钥
SECRET_KEY = ""  # 百度智能云API密钥
# 不同接口请求地址
API_URL_GENERAL = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token="  # 通用文字识别
API_URL_IDCARD = "https://aip.baidubce.com/rest/2.0/ocr/v1/idcard?access_token="  # 身份证识别
API_URL_BANKCARD = "https://aip.baidubce.com/rest/2.0/ocr/v1/bankcard?access_token="  # 银行卡识别
# 请求头
HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json'
}
TOKEN = ''  # 获取的TOKEN


class PayloadBase:
    """请求参数基类"""

    def __init__(self):
        self.image = 'image='

    def set_image(self, image_base64: str):
        self.image = 'image=' + image_base64

    @property
    def get_payload(self) -> str:
        """获取参数"""
        if self.image == 'image=':
            raise ValueError('请设置图片参数')
        return '&'.join(self.__dict__.values())
