# r\FrameFlow(PROJECT_ROOT)FrameFlow\SubAPI\ImageTools\config.py

# 用户必填配置
from dataclasses import dataclass,field
from typing import Literal, Optional


API_KEY = 'API_KEY'
SECRET_KEY = 'SECRET_KEY'

# 用户可选配置
## 功能开关
ENABLE_IDCARD_OCR = True
"""是否执行身份证OCR，默认为True"""
ENABLE_BANKCARD_OCR = True
"""是否执行银行卡OCR，默认为True"""

## 性能相关

# 系统内部配置
_token_cache = {"token": None, "expires_at": 0}
_QPS = 2

# 环境/部署配置
_ACCESS_TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
_GENERAL_OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
_IDCARD_OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/idcard"
_HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json'
}
_QUERY_PARAMS = {"access_token":""}
# 假设添加其他OCR/API的话，我应该怎么调整这个文件
'------------------------------------------------------------------'
LanguageType = Literal['CHN_ENG','ENG','JAP','KOR','FRE','SPA','POR','GER','ITA','RUS']
BoolStr = Literal['true','false']
class Config:
    def __init__(self):
        # 应该是允许Config类作为结点或者属性类作为结点，后续再研究
        return self
    def revert(self,text):
        """输入格式化文本，转变成对应的配置内容"""
        pass
@dataclass
class GeneralOCRConfig:
    GENERAL_OCR_POST_URL:str = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    URL_PARAMS:dict = {'access_token':''}
    HEADERS:dict = field(default_factory = lambda:{'content-type': 'application/x-www-form-urlencoded'})
    BODY_PARAMS:dict = {
        'image':'',
        'url':'',
        'pdf_file':'',
        'pdf_file_num':'',
        'ofd_file':'',
        'ofd_file_num':'',
    }
    language_type:LanguageType = 'CHN_ENG',
    detect_direction:bool =False,
    detect_language:bool = False
    paragraph:bool = False
    probability:bool = False
    # 输入源（四选一），默认都为空
    image_path: Optional[str] = None        # 本地图片路径（会自动 base64）
    image_url: Optional[str] = None
    pdf_path: Optional[str] = None
    pdf_page_num: int = 1
    ofd_path: Optional[str] = None
    ofd_page_num: int = 1
    access_token:str = ''



    RESPONSE_STRUCT = {
        'direction','log_id','words_result_num','words_result',
    }


@dataclass
class OCRConfig:
    ACCESS_TOKEN_POST_URL:str = "https://aip.baidubce.com/oauth/2.0/token"

    IDCARD_OCR_POST_URL:str = "https://aip.baidubce.com/rest/2.0/ocr/v1/idcard"
    BANKCARD_OCR_POST_URL:str = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    ENABLE_IDCARD_OCR:bool = True
    ENABLE_BANCARD_OCR:bool = True

@dataclass
class PackConfig:
    ocr:OCRConfig = OCRConfig()
