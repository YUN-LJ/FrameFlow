from pathlib import Path

from baidu_ocr import BaiduBankCardOCR,BaiduIDCardOCR
from extractor import ExcelFloatImageExtractor



class BaiduOCRFacade:
    def __init__(self):
        self.config = None
        self.editconfig = None
        self.tokenmanger = None
        self.generalocr = None
        self.bankcardocr = None
        self.idcardocr = None
        self.extractor = None
        self.http_manager = None
    def func1(self,file:str):
        """输入指定excel文件，获取表名"""
        ...
    def func2(self,file:str,sheet_name:str):
        """输入表名，对表执行操作"""
        ...
    def process_excel(self,file_path:str,sheet_name:str,config:Config)->Path:
