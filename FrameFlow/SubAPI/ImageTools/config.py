# r\FrameFlow(PROJECT_ROOT)FrameFlow\SubAPI\ImageTools\config.py

# 用户必填配置
from dataclasses import dataclass,field
from typing import Literal, Optional


# API_KEY = 'API_KEY' 
# SECRET_KEY = 'SECRET_KEY'



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


class EditConfig:
    """写回Excel的相关配置"""
    ## 功能开关
    ENABLE_IDCARD_OCR = True
    """是否执行身份证OCR，默认为True"""
    ENABLE_BANKCARD_OCR = True
    """是否执行银行卡OCR，默认为True"""
    USE_IDCARD_ADDRESS = False
    """是否启用身份证的住址返回"""
    USE_IDCARD_ID = True
    """是否启用身份证的公民身份号码返回"""
    USE_IDCARD_BIRTH = False
    """是否启用身份证的出生返回"""
    USE_IDCARD_NAME = True
    """是否启用身份证的姓名返回"""
    USE_IDCARD_GENDER = False
    """是否启用身份证的性别返回"""
    USE_IDCARD_NATION = False
    """是否启用身份证的民族返回"""
    USE_BANKCARD_NUMBER = True
    """是否启用银行卡的银行卡卡号返回"""
    USE_BANKCARD_VALIDDATE = False
    """是否启用银行卡的有效期返回"""
    USE_BANKCARD_TYPE = False
    """是否启用银行卡的类型返回"""
    USE_BANKCARD_BANKNAME = False
    """是否启用银行卡的银行名返回"""
    USE_BANKCARD_HOLDERNAME = False
    """是否启用银行卡的持卡人姓名返回"""

    # IDCARD_FIELDS = ["姓名","公民身份号码"]
    # """身份证字段（固定顺序）"""
    IDCARD_DEFS = [
        ('USE_IDCARD_NAME', '姓名', '姓名'),          # 百度返回 key 就是 '姓名'
        ('USE_IDCARD_GENDER', '性别', '性别'),
        ('USE_IDCARD_NATION', '民族', '民族'),
        ('USE_IDCARD_BIRTH', '出生日期', '出生'),    # 注意：展示名和提取名不一致！
        ('USE_IDCARD_ADDRESS', '住址', '住址'),
        ('USE_IDCARD_ID', '公民身份号码', '公民身份号码'),
    ]

    BANKCARD_DEFS = [
        ('USE_BANKCARD_NUMBER', '银行卡号', 'bank_card_number'),
        ('USE_BANKCARD_VALIDDATE', '有效期', 'valid_date'),
        ('USE_BANKCARD_TYPE', '卡片类型', 'type'),
        ('USE_BANKCARD_BANKNAME', '发卡行', 'bank_name'),
        ('USE_BANKCARD_HOLDERNAME', '持卡人', 'holder_name'),
    ]

    @classmethod
    def _get_enabled_defs(cls, defs):
        """根据开关过滤出启用的字段定义"""
        return [d for d in defs if getattr(cls, d[0], False)]

    @classmethod
    def get_all_display_fields(cls):
        """获取最终要写入Excel的表头列表（按顺序）"""
        fields = []
        if cls.ENABLE_IDCARD_OCR:
            fields.extend([d[1] for d in cls._get_enabled_defs(cls.IDCARD_DEFS)])
        if cls.ENABLE_BANKCARD_OCR:
            fields.extend([d[1] for d in cls._get_enabled_defs(cls.BANKCARD_DEFS)])
        return fields

    @classmethod
    def get_idcard_extract_keys(cls):
        """获取身份证的API提取字段列表"""
        keys = []
        if cls.ENABLE_IDCARD_OCR:
            keys.extend([d[2] for d in cls._get_enabled_defs(cls.IDCARD_DEFS)])
        return keys
    
    @classmethod
    def get_bankcard_extract_keys(cls):
        """获取银行卡的API提取字段列表"""
        keys = []
        if cls.ENABLE_BANKCARD_OCR:
            keys.extend([d[2] for d in cls._get_enabled_defs(cls.BANKCARD_DEFS)])
        return keys

    
    @classmethod
    def get_total_extra_cols(cls):
        return len(cls.get_all_display_fields())


