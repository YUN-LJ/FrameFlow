# r\FrameFlow(PROJECT_ROOT)\FrameFlow\SubAPI\ImageTools\config.py

# 用户必填配置
from dataclasses import dataclass, field
from typing import ClassVar
from urllib.parse import urlencode

from FrameFlow.SubAPI.ImageTools.baidu_ocr import AccessTokenManager

_token_cache = {"token": None, "expires_at": 0}
_QPS = 2

_QUERY_PARAMS = {"access_token": ""}

# 模块级常量
GENERAL_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
"""通用OCR请求地址"""
IDCARD_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/idcard"
"""身份证OCR请求地址"""
BANKCARD_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/bankcard"
"""银行卡OCR请求地址"""

@dataclass
class OCRPostConfig:
    url: str = GENERAL_URL  # 当前使用的 URL
    """使用的URL，创建时是通用请求的URL，使用as_idcard()或as_bankcard()函数进行切换"""
    params: dict = field(default_factory=dict)
    """请求体参数"""
    headers: dict = field(default_factory=lambda: {'Content-Type': 'application/x-www-form-urlencoded'})
    """HTTP请求头，字典格式"""
    data:dict = field(default_factory=lambda:{'image':''})  # 请求体
    """跟随请求发送的数据"""

    def as_idcard(self):
        """设置地址为身份证查询地址"""
        self.url = IDCARD_URL
        return self

    def as_bankcard(self):
        """设置地址为银行卡查询地址"""
        self.url = BANKCARD_URL
        return self

    async def build_request(self,mgr:AccessTokenManager)->dict:
        """创建request请求需要的参数字典"""
        params = self.params.copy()
        params['access_token'] = await mgr.get_valid_token()
        query = urlencode(params)
        # query = '&'.join(f"{k}={v}" for k,v in self.params.items())

        return {
            'url':f"{self.url}?{query}",
            'headers':self.headers,
            'data':self.data
        }

    def clone(self,data:str)->'OCRPostConfig':
        """复制当前模板，并替换图片数据"""
        new_data = self.data.copy()
        new_data['image']=data
        return OCRPostConfig(
            url=self.url,
            params=self.params.copy(),
            headers=self.headers.copy(),
            data=new_data
        )

BASE_PROTOTYPE = OCRPostConfig()
"""OCR请求字典原型"""


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
    IDCARD_DEFS:ClassVar[list] = [
        ("USE_IDCARD_NAME", "姓名", "姓名"),
        ("USE_IDCARD_GENDER", "性别", "性别"),
        ("USE_IDCARD_NATION", "民族", "民族"),
        ("USE_IDCARD_BIRTH", "出生日期", "出生"),
        ("USE_IDCARD_ADDRESS", "住址", "住址"),
        ("USE_IDCARD_ID", "公民身份号码", "公民身份号码"),
    ]

    BANKCARD_DEFS:ClassVar[list] = [
        ("USE_BANKCARD_NUMBER", "银行卡号", "bank_card_number"),
        ("USE_BANKCARD_VALIDDATE", "有效期", "valid_date"),
        ("USE_BANKCARD_TYPE", "卡片类型", "type"),
        ("USE_BANKCARD_BANKNAME", "发卡行", "bank_name"),
        ("USE_BANKCARD_HOLDERNAME", "持卡人", "holder_name"),
    ]

    @classmethod
    def get_enabled_defs(cls, defs):
        """根据开关过滤出启用的字段定义"""
        return [d for d in defs if getattr(cls, d[0], False)]

    @classmethod
    def get_idcard_display_fields(cls):
        """获取身份证的API提取字段列表"""
        keys = []
        if cls.ENABLE_IDCARD_OCR:
            keys.extend([d[2] for d in cls.get_enabled_defs(cls.IDCARD_DEFS)])
        return keys

    @classmethod
    def get_bankcard_display_fields(cls):
        """获取银行卡的API提取字段列表"""
        keys = []
        if cls.ENABLE_BANKCARD_OCR:
            keys.extend([d[2] for d in cls.get_enabled_defs(cls.BANKCARD_DEFS)])
        return keys
    
    @classmethod
    def get_all_display_fields(cls):
        """获取最终要写入Excel的表头列表（按顺序）"""
        fields = []
        if cls.ENABLE_IDCARD_OCR:
            fields.extend(cls.get_idcard_display_fields())
        if cls.ENABLE_BANKCARD_OCR:
            fields.extend(cls.get_bankcard_display_fields())
        return fields
    
    @classmethod
    def get_total_extra_cols(cls):
        """获得写入Excel表头的字段数量"""
        return len(cls.get_all_display_fields())

    @classmethod
    def toggle(cls, attr_name: str):
        """切换指定布尔类属性的值（True ↔ False）"""
        if hasattr(cls, attr_name):
            current = getattr(cls, attr_name)
            if isinstance(current, bool):
                setattr(cls, attr_name, not current)
            else:
                raise TypeError(f"{attr_name} 不是布尔类型")
        else:
            raise AttributeError(f"{attr_name} 不存在")

    @classmethod
    def get_idcard_mapping(cls):
        """获得身份证字段映射列表"""
        return [(d[1],d[2]) for d in cls.get_enabled_defs(cls.IDCARD_DEFS)]

    @classmethod
    def get_bankcard_mapping(cls):
        """获得身份证字段映射列表"""
        return [(d[1],d[2]) for d in cls.get_enabled_defs(cls.BANKCARD_DEFS)]