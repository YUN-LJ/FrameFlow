from bisect import bisect_left
from dataclasses import dataclass
from functools import cached_property, lru_cache
import logging
import posixpath
from typing import Any, BinaryIO, Callable, Dict, List, Optional, Tuple, Union
from xml.etree import ElementTree as ET
import zipfile

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# 2. 创建一个控制台处理器，并设置其级别
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # 关键：处理器的级别也要设为DEBUG

# 3. 将处理器添加到记录器
logger.addHandler(console_handler)


class ExcelFloatImageExtractor:
    NAMESPACES = {
        "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "xdr": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "pkg": "http://schemas.openxmlformats.org/package/2006/relationships",
    }
    def __init__(self, source: str):
        self._source = source
        self._zip_file: zipfile.ZipFile = None  # 延迟打开

        # self._sheet_drawing_cache:Dict[str,str]={}
        # self._draw_anchors_cache:Dict[str,List[str]] = {}

        self._image_cache: Dict[str, bytes] = {}
        self._image_cache_order: List[str] = []

    "------------------上下文管理------------------------------------------"

    def __enter__(self):
        if self._zip_file is None:
            self._open_zip()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._zip_file.close()
        self._zip_file = None

    def _open_zip(self):
        self._zip_file = zipfile.ZipFile(self._source)

    "------------------工具函数------------------------------------------"
    @staticmethod
    def _get_relative_file(source) -> str:
        """从传入的xml文件获取对应的.rel关系文件"""
        source_dir = posixpath.dirname(source)
        source_name = posixpath.basename(source)
        rels_path = posixpath.join(source_dir, "_rels", source_name + ".rels")
        return ExcelFloatImageExtractor._normalize_zip_path(rels_path)

    # @staticmethod
    # def path_resolve(path: str) -> str:
    #     path = path.replace("\\", "/")
    #     return path

    @staticmethod
    def _normalize_zip_path(path:str)->str:
        raw = str(path).replace("\\", "/")

        normalized = posixpath.normpath(raw)

        if normalized.startswith("/"):
            normalized = normalized.lstrip("/")
        return normalized
        

    "---------------------簿级操作-----------------------------------------"
    @cached_property
    def sheets(self) -> Dict[str, str]:
        """返回所有工作表的名称到内部路径的映射，例如 {'Sheet1': 'xl/worksheets/sheet1.xml'}"""
        if self._zip_file is None:
            raise RuntimeError("must use in 'with' block")

        # 1. 读取 workbook.xml 获取 sheet 名称和 r:id
        wb_tree = ET.parse(self._zip_file.open('xl/workbook.xml'))
        wb_root = wb_tree.getroot()
        sheet_elements = wb_root.findall('.//main:sheet', self.NAMESPACES)

        # 2. 读取关系文件获取 r:id 到 target 的映射
        rel_tree = ET.parse(self._zip_file.open('xl/_rels/workbook.xml.rels'))
        rel_root = rel_tree.getroot()
        rel_map = {}
        for rel in rel_root.findall('.//pkg:Relationship', self.NAMESPACES):
            rid = rel.get('Id')
            target = rel.get('Target')
            if rid and target:
                # 注意 target 是相对路径，需补上 xl/ 前缀
                rel_map[rid] = self._normalize_zip_path('xl/' + target)

        # 3. 构建字典
        name_to_path = {}
        for sheet in sheet_elements:
            name = sheet.get('name')
            # 注意命名空间：r:id 的完整名称为 {http://...}id
            rid = sheet.get(f"{{{self.NAMESPACES['r']}}}id")
            if name and rid and rid in rel_map:
                name_to_path[name] = rel_map[rid]
                # name_to_path.append((name,rel_map[rid]))

        return name_to_path
        

    "表级缓存-----------------------------------------------------"
    "存曾打开过的sheet的drawing关联信息，因为表一般不会太多"
        
    @lru_cache(maxsize=4) # 最多同时记录四个表的路径
    def drawings(self,sheet_name:str) -> Optional[str]:
        """通过单个工作表的名称到内部drawing文件的映射，例如 {'Sheet1': 'xl/drawings/drawing1.xml'}"""
        if self._zip_file is None:
            raise RuntimeError("must use in 'with' block")

        # 1. 通过表名得到对应的工作表路径
        # if sheet_name not in self._sheets:
        #     logger.warning("不存在相应表格")
        #     return None # 返回None便于检查重试            
        # else:
        #     sheet_path = self._sheets[sheet_name]
        if sheet_name not in self.sheets:
            logger.error("不存在对应表")
            return None
        else:
            sheet_path = self.sheets[sheet_name]
        st_tree = ET.parse(self._zip_file.open(sheet_path))
        st_root = st_tree.getroot()
        drawing_elements = st_root.findall('.//main:drawing', self.NAMESPACES)

        # 2. 读取关系文件获取 r:id 到 target 的映射
        rel_tree = ET.parse(self._zip_file.open(self._normalize_zip_path(self._get_relative_file(sheet_path))))
        rel_root = rel_tree.getroot()
        rel_map = {}
        for rel in rel_root.findall('.//pkg:Relationship', self.NAMESPACES):
            rid = rel.get('Id')
            target = rel.get('Target')
            if rid and target:
                abs_path = posixpath.join(posixpath.dirname(sheet_path),target)
                rel_map[rid] = self._normalize_zip_path(abs_path)

        # 3. 构建字典
        for drawing in drawing_elements:
            rid = drawing.get(f"{{{self.NAMESPACES['r']}}}id")
            if rid and rid in rel_map:
                return rel_map[rid]
        return None

    @lru_cache(maxsize=4)
    def _get_sheet_dimensions(self, sheet_name):
        """AI编写 可能存在问题"""
        sheet_path = self.sheets[sheet_name]
        sheet_tree = ET.parse(self._zip_file.open(sheet_path))
        sheet_root = sheet_tree.getroot()

        # 读取默认列宽和行高（从 sheetFormatPr）
        default_col_width = 8.43  # Excel 默认
        default_row_height = 15   # 磅
        fmt_pr = sheet_root.find(".//main:sheetFormatPr", self.NAMESPACES)
        if fmt_pr is not None:
            default_col_width = float(fmt_pr.get("defaultColWidth", default_col_width))
            default_row_height = float(fmt_pr.get("defaultRowHeight", default_row_height))

        # 构建列宽映射：col_index -> width (字符数)
        col_width_map = {}
        cols = sheet_root.findall(".//main:col", self.NAMESPACES)
        for col in cols:
            min_c = int(col.get("min", 1))
            max_c = int(col.get("max", min_c))
            width = float(col.get("width", default_col_width))
            for c in range(min_c, max_c + 1):
                col_width_map[c] = width  # 相同范围宽度相同

        # 构建列宽前缀（1-based索引）
        if col_width_map:
            max_col = max(col_width_map.keys())
            col_prefix = [0]
            for i in range(1, max_col + 1):
                w = col_width_map.get(i, default_col_width)
                col_prefix.append(col_prefix[-1] + w * 9525)  # 单位转换
        else:
            col_prefix = [0]

        # 构建行高映射：row_index -> height (磅)
        row_height_map = {}
        rows = sheet_root.findall(".//main:row", self.NAMESPACES)
        for row in rows:
            r = int(row.get("r", 1))
            ht = float(row.get("ht", default_row_height))
            row_height_map[r] = ht

        # 构建行高前缀（1-based索引）
        if row_height_map:
            max_row = max(row_height_map.keys())
            row_prefix = [0]
            for i in range(1, max_row + 1):
                h = row_height_map.get(i, default_row_height)
                row_prefix.append(row_prefix[-1] + h * 12700)  # 磅 → EMU
        else:
            row_prefix = [0]

        return row_prefix, col_prefix

    @lru_cache(maxsize=256) 
    def images(self, sheet_name: str):
        if self._zip_file is None:
            raise RuntimeError("must use in 'with' block")
        # 1. 通过表名得到对应的drawing文件路径
        drawing_fp = self.drawings(sheet_name)
        if drawing_fp is None:
            logger.error("未找到对应表")
            return None
        # 2. 通过drawing文件，得到anchors列表
        # draw_dir = "xl/drawings"
        drawing_tree = ET.parse(self._zip_file.open(self._normalize_zip_path(drawing_fp)))
        drawing_root = drawing_tree.getroot()
        target_tags = {
            f"{{{self.NAMESPACES['xdr']}}}oneCellAnchor",
            f"{{{self.NAMESPACES['xdr']}}}twoCellAnchor",
            f"{{{self.NAMESPACES['xdr']}}}absoluteAnchor"
        }

        raw_anchors = [elem for elem in drawing_root.iter() if elem.tag in target_tags]
        logger.debug(f"找到 {len(raw_anchors)} 个锚点")
        anchors = []
        # 表格的行列前缀计算 行高和列宽的前缀和命名数组

        # 解析drawing rel的媒体路径，做成map
        drawing_rel_tree = ET.parse(self._zip_file.open(self._get_relative_file(drawing_fp)))
        drawing_rel_root = drawing_rel_tree.getroot()
        drawing_rels = drawing_rel_root.findall(".//pkg:Relationship",self.NAMESPACES)
        drawing_rel_map = {}
        for drawing_rel in drawing_rels:
            rel_id = drawing_rel.get("Id")
            target = drawing_rel.get("Target")
            if rel_id and target:
                abs_path = posixpath.join(posixpath.dirname(drawing_fp),target)
                drawing_rel_map[rel_id] = self._normalize_zip_path(abs_path)
        



        row_prefix,col_prefix = self._get_sheet_dimensions(sheet_name)
        for anchor in raw_anchors:
            # 计算中心点 需要用到
            tag = anchor.tag.rsplit('}', 1)[-1]
            if tag == "oneCellAnchor":
                from_elem = anchor.find(".//xdr:from", self.NAMESPACES)
                ext_elem = anchor.find(".//xdr:ext", self.NAMESPACES)
                if from_elem is not None and ext_elem is not None:
                    row_from = int(from_elem.find(".//xdr:row", self.NAMESPACES).text)
                    col_from = int(from_elem.find(".//xdr:col", self.NAMESPACES).text)
                    row_off = int(from_elem.find(".//xdr:rowOff", self.NAMESPACES).text)
                    col_off = int(from_elem.find(".//xdr:colOff", self.NAMESPACES).text)
                    cx = int(ext_elem.get("cx"))
                    cy = int(ext_elem.get("cy"))
                    center_x = col_prefix[col_from] + col_off + cx // 2
                    center_y = row_prefix[row_from] + row_off + cy // 2
                    row = bisect_left(row_prefix, center_y) + 1
                    col = bisect_left(col_prefix, center_x) + 1
                else:
                    row = col = 0
            elif tag == "twoCellAnchor":
                row_from = int(anchor.find(".//xdr:from",self.NAMESPACES).find(".//xdr:row",self.NAMESPACES).text)
                col_from = int(anchor.find(".//xdr:from",self.NAMESPACES).find(".//xdr:col",self.NAMESPACES).text)
                row_to = int(anchor.find(".//xdr:to",self.NAMESPACES).find(".//xdr:row",self.NAMESPACES).text)
                col_to = int(anchor.find(".//xdr:to",self.NAMESPACES).find(".//xdr:col",self.NAMESPACES).text)
                rowoff_from = int(anchor.find(".//xdr:from",self.NAMESPACES).find(".//xdr:rowOff",self.NAMESPACES).text)
                coloff_from = int(anchor.find(".//xdr:from",self.NAMESPACES).find(".//xdr:colOff",self.NAMESPACES).text)
                rowoff_to = int(anchor.find(".//xdr:to",self.NAMESPACES).find(".//xdr:rowOff",self.NAMESPACES).text)
                coloff_to = int(anchor.find(".//xdr:to",self.NAMESPACES).find(".//xdr:colOff",self.NAMESPACES).text)

                center_y = round(1/2*(row_prefix[row_to]+rowoff_to+row_prefix[row_from]+rowoff_from))
                center_x = round(1/2*(col_prefix[col_to]+coloff_to+col_prefix[col_from]+coloff_from))
                row = bisect_left(row_prefix, center_y) + 1
                col = bisect_left(col_prefix, center_x) + 1 
            elif tag == "absoluteAnchor":
                pos = anchor.find(".//xdr:pos", self.NAMESPACES) 
                ext = anchor.find(".//xdr:ext", self.NAMESPACES)
                if pos is not None and ext is not None:
                    x = int(pos.get("x"))
                    y = int(pos.get("y"))
                    cx = int(ext.get("cx"))
                    cy = int(ext.get("cy"))
                    center_x = x + cx // 2
                    center_y = y + cy // 2
                    row = bisect_left(row_prefix, center_y) + 1
                    col = bisect_left(col_prefix, center_x) + 1
                else:
                    row = 0
                    col = 0
            # 一个在使用图片数据时才加载的图片数据
            bilp = anchor.find(".//a:blip",self.NAMESPACES)
            rid = bilp.get(f"{{{self.NAMESPACES['r']}}}embed")
            image_path = drawing_rel_map.get(rid)
            anchors.append(
                {
                    "row":row,
                    "col":col,
                    "path":image_path
                }
            )
        return anchors

    def _get_image_data(self, image_path:str) -> Optional[bytes]:
        if self._zip_file is None:
            raise RuntimeError("must use in 'with' block")

        # 无缓存版本
        # 因为整个工作流只会打开图片一次并读取完数据后关闭，不保留缓存
        data = self._zip_file.read(image_path)
        return data

    "------------------ 公共接口 ------------------------------------------"
    def get_single_sheet_floating_images(
        self, sheet_name: str
    ) -> List[dict]:
        """
        获取指定工作表中的所有浮动图片信息。
        """
        # 上下文校验
        if self._zip_file is None:
            raise RuntimeError("must use in 'with' block")
        images = self.images(sheet_name)
        return images

if __name__ == "__main__":
    file_path = "assert/南方科技2标2026.4.26月工资表.xlsx"
    sheet_name = "Sheet1 (2)"
    with ExcelFloatImageExtractor(file_path) as extractor:
        print("成功打开文件")

        print("所有工作表：", extractor.sheets)
        print("目标表的 drawing 文件：", extractor.drawings(sheet_name))
        anchors = extractor.images(sheet_name)
        print("解析到的锚点数量：", len(anchors) if anchors else 0)   # 实际个数


        images  = extractor.get_single_sheet_floating_images(sheet_name)
        for image in images:
            print(image,end="\n")
        print("成功结束")
        
