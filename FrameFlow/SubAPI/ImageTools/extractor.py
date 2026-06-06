from dataclasses import dataclass, field
from functools import lru_cache
from posixpath import normpath
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import BinaryIO, Dict, Tuple, Optional, Union
import logging


logger = logging.getLogger(__name__)

@dataclass
class FloatImageInfo:
    anchor_type: str  # 'oneCell', 'twoCell', 'absolute'
    # 起始位置
    from_row: int = 0
    from_col: int = 0
    from_row_offset: int = 0   # EMU 单位
    from_col_offset: int = 0
    # 结束位置（仅 twoCellAnchor 需要）
    to_row: int = 0
    to_col: int = 0
    to_row_offset: int = 0
    to_col_offset: int = 0
    # 绝对位置（仅 absoluteAnchor 需要）
    x: int = 0
    y: int = 0
    # 图片数据
    image_bytes: bytes
    relationship_id: str
    image_path: str

@dataclass
class FloatingImagesContainer:
    images:list[FloatImageInfo]

@dataclass
class SheetInfo:
    sheet_id:int
    name:str
    rel_id:str
    file_path:str
    container:Optional[FloatingImagesContainer]

@dataclass
class WorkBookInfo:
    sheets_list=list[SheetInfo] = field(default_factory=list)





class ExcelImageExtractor:
    """Excel浮动图片提取器"""

    NAMESPACES = {
        "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "xdr": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "pkg": "http://schemas.openxmlformats.org/package/2006/relationships",
    }

    def __init__(self, source: Union[str, Path, BinaryIO]):
        self._source = source
        self._zip_file = None
        # 簿级缓存
        self._workbook_sheet_map = None  # {sheet_name:(sheet_path,sheet_rid)}
        self._workbook_rels_map = None # {rid: target_path}
        # 表级缓存
        self._sheet_drawing_cache = {} # sheet_path -> list[drawing_path]
        self._drawing_rels_cache = {}  # drawing_path -> {rid:image_path}
        # 图片缓存
        self._image_cache = {} # image_path -> bytes

        # # TODO
        # # 支持文件对象：__init__ 可接受 Path、str 或 BinaryIO，增加灵活性。

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        """打开Excel文件，返回self供链式调用"""
        if self._zip_file is None:
            if isinstance(self._source,(str,Path)):
                self._zip_file = zipfile.ZipFile(self._source,"r")
            else:
                # 二进制流，需支持seek
                self._zip_file = zipfile.ZipFile(self._source,"r")
        return self
    def close(self):
        """关闭zip文件，释放资源"""
        if self._zip_file:
            self._zip_file.close()
            self._zip_file = None
    
    '-----------------------解析工作簿---------------------'
    
    def _get_sheet_info(self, sheet_name: str) -> Optional[Tuple[str, str]]:
        """根据 sheet 名称获取 (sheet_path, sheet_rid)"""
        return self._workbook_sheets.get(sheet_name)

    @property
    def _workbook_sheets(self) -> Dict[str, Tuple[str, str]]:
        """返回{表名:(表路径,表关系)}的映射，并作为property缓存"""
        if self._workbook_sheet_map is None:
            self._workbook_sheet_map = self._parse_workbook_sheets()
        return self._workbook_sheet_map

    def _parse_workbook_sheets(self) -> Dict[str, Tuple[str, str]]:
        """解析xl/workbook.xml，返回sheet名称到(路径,rid)的映射"""
        try:
            tree = ET.parse(self._zip_file.open("xl/workbook.xml"))
            root = tree.getroot()
            ns = {"main": self.NAMESPACES["main"], "r": self.NAMESPACES["r"]}
            sheets = {}
            for sheet_el in root.findall(".//main:sheet", ns):
                name = sheet_el.get("name")
                rid = sheet_el.get(f"{{{self.NAMESPACES['r']}}}id")
                if name and rid:
                    # 通过workbook关系文件获取sheet实际路径
                    sheet_path = self._get_sheet_path_by_rid(rid)
                    if sheet_path:
                        sheets[name] = (sheet_path, rid)
            return sheets
        except Exception as e:
            logger.error(f"解析workbook.xml失败：{e}")
            return {}
    def get_workbook_info(self)->WorkBookInfo:

        if self._zip_file is None:
            raise RuntimeError("文件未打开")

        sheet_infos = []
        for sheet_name, (sheet_path,sheet_rid) in self._workbook_sheets.items():
            images = self.get_float_images(sheet_name)
            container = FloatingImagesContainer(images=images) if images else None

            # 获取sheet_id
            sheet_id = self._get_sheet_id_by_name(sheet_name)
            sheet_infos.append(
                SheetInfo(
                    sheet_id=sheet_id,
                    name = sheet_name,
                    rel_id=sheet_rid,
                    file_path=sheet_path,
                    container=container
                )
            )
    def _get_sheet_id_by_name(self,sheet_name:str)->int:
        try:
            tree = ET.parse(self._zip_file.open("xl/workbook.xml"))
            root = tree.getroot()
            ns = {"main":self.NAMESPACES["main"]}
            for sheet in root.findall(".//main:sheet",ns):
                if sheet.get("name") == sheet_name:
                    return int(sheet.get("sheetId",0))
        except Exception:
            raise RuntimeError("错误")

    '表分析'
    def _get_sheet_path_by_rid(self, rid: str) -> Optional[str]:
        """通过关系ID从xl/_rels/workbook.xml.rels获取sheet文件路径，并缓存结果"""
        if self._workbook_rels_map is None:
            self._workbook_rels_map = self._parse_workbook_rels()
        return self._workbook_rels_map.get(rid)

    def _parse_workbook_rels(self)->Dict[str,str]:
        """解析xl/_rels/workbook.xml.rels，返回rid->路径映射"""
        rels_path = "xl/_rels/workbook.xml.rels"
        try:
            tree = ET.parse(self._zip_file.open(rels_path))
            root = tree.getroot()
            ns_pkg = {"pkg": self.NAMESPACES["pkg"]}
            mapping = {}
            for rel in root.findall(".//pkg:Relationship", ns_pkg):
                rid = rel.get("Id")
                target = rel.get("Target")
                if rid and target:
                        full_path = normpath(f"xl/{target}")
                        mapping[rid] = full_path
            return mapping
        except Exception as e:
            logger.error(f"解析workbook关系文件失败{e}")
            return {}
    '--------------------------------------'
    def _get_sheet_drawing_paths(
        self, sheet_path: str
    ) -> list[str]:
        """获得所有与指定sheet关联的drawing文件路径"""
        if sheet_path in self._sheet_drawing_cache:
            return self._sheet_drawing_cache[sheet_path]
        sheet_rels_path = self._build_rels_path(sheet_path)
        try:
            tree = ET.parse(self._zip_file.open(sheet_rels_path))
            root = tree.getroot()
            ns_pkg = {"pkg": self.NAMESPACES["pkg"]}
            drawing_paths = []
            for rel in root.findall(".//pkg:Relationship", ns_pkg):
                rel_type = rel.get("Type")
                if rel_type == f"{{{self.NAMESPACES['r']}}}/drawing":
                    target = rel.get("Target")
                    if target:
                        abs_path = self._resolve_relative_path(sheet_path, target)
                        drawing_paths.append(abs_path)
            self._sheet_drawing_cache[sheet_path] = drawing_paths
            return drawing_paths
        except (KeyError, FileNotFoundError):
            logger.warning(f"未找到sheet的关系文件:{sheet_rels_path}")
            return []
    '图片提取-----------------------------------------------------------'

    def _extract_images_from_drawing(
        self,
        drawing_path: str,
        sheet_name: str,
    ) -> list[FloatImageInfo]:
        """解析drawing文件，返回所有图片信息"""
        results = []
        try:
            tree = ET.parse(self._zip_file.open(drawing_path))
            root = tree.getroot()
            ns = {
                "xdr": self.NAMESPACES["xdr"],
                "a": self.NAMESPACES["a"],
                "r": self.NAMESPACES["r"],
            }

            anchors_info = self._extract_anchors(root, ns)
            if not anchors_info:
                return []

            rid_to_path = self._get_drawing_rid_to_path(drawing_path)
            if not rid_to_path:
                return []

            results = []
            for info in anchors_info:
                r_id = info.pop("r_id")
                img_path = rid_to_path.get(r_id)
                if not img_path:
                    logger.warning(f"未找到rId={r_id}对应的图片路径")
                    continue
                image_bytes = self._get_image_bytes(img_path)
                if not image_bytes:
                    continue
                results.append(
                    FloatImageInfo(
                        image_bytes=image_bytes,
                        relationship_id=r_id,
                        image_path=img_path,
                        **info
                    )
                )
            return results

        except Exception as e:
            logger.error(f"解析drawing文件{drawing_path}失败:{e}")
            return []

    def _extract_anchors(
        self, root: ET.Element[str], ns: dict[str, str]
    ) -> list[Tuple[int, int, str, str]]:
        anchors = []
        for anchor_type in ("twoCellAnchor", "oneCellAnchor", "absoluteAnchor"):
            for anchor in root.findall(f".//xdr:{anchor_type}", ns):
                anchor_info = self._extract_anchor_info(anchor,anchor_type,ns)
                if anchor_info.get("r_id"):
                        anchors.append(anchor_info)
        return anchors
    
    def _extract_anchor_info(self, anchor, anchor_type: str, ns: dict) -> dict:
        """从单个anchor元素中提取位置信息（不含图片数据）"""
        info = {"anchor_type": anchor_type}
        
        # 解析 from 元素
        from_el = anchor.find(".//xdr:from", ns)
        if from_el is not None:
            row_el = from_el.find("xdr:row", ns)
            col_el = from_el.find("xdr:col", ns)
            row_off = from_el.find("xdr:rowOff", ns)
            col_off = from_el.find("xdr:colOff", ns)
            info["from_row"] = int(row_el.text) if row_el is not None else 0
            info["from_col"] = int(col_el.text) if col_el is not None else 0
            info["from_row_offset"] = int(row_off.text) if row_off is not None else 0
            info["from_col_offset"] = int(col_off.text) if col_off is not None else 0
        
        if anchor_type == "twoCellAnchor":
            to_el = anchor.find(".//xdr:to", ns)
            if to_el is not None:
                row_el = to_el.find("xdr:row", ns)
                col_el = to_el.find("xdr:col", ns)
                row_off = to_el.find("xdr:rowOff", ns)
                col_off = to_el.find("xdr:colOff", ns)
                info["to_row"] = int(row_el.text) if row_el is not None else 0
                info["to_col"] = int(col_el.text) if col_el is not None else 0
                info["to_row_offset"] = int(row_off.text) if row_off is not None else 0
                info["to_col_offset"] = int(col_off.text) if col_off is not None else 0
        
        elif anchor_type == "absoluteAnchor":
            pos_el = anchor.find(".//xdr:pos", ns)
            if pos_el is not None:
                info["x"] = int(pos_el.get("x", 0))
                info["y"] = int(pos_el.get("y", 0))
        
        # 提取图片关系ID
        blip = anchor.find(".//a:blip", ns)
        if blip is not None:
            info["r_id"] = blip.get(f"{{{self.NAMESPACES['r']}}}embed")
        
        return info
    
    def _get_drawing_rid_to_path(
        self, drawing_path: str
    ) -> Dict[str, str]:
        """解析drawing的关系文件，返回{rid:图片绝对路径}"""
        if drawing_path in self._drawing_rels_cache:
            return self._drawing_rels_cache[drawing_path]
        rels_path = self._build_rels_path(drawing_path)
        try:
            rels_tree = ET.parse(self._zip_file.open(rels_path))
            root = rels_tree.getroot()
            ns_pkg = {"pkg": self.NAMESPACES["pkg"]}
            rid_to_path = {}
            for rel in root.findall(".//pkg:Relationship", ns_pkg):
                rid = rel.get("Id")
                target = rel.get("Target")
                if rid and target:
                    abs_path = self._resolve_relative_path(drawing_path, target)
                    rid_to_path[rid] = abs_path
            self._drawing_rels_cache[drawing_path] = rid_to_path
            return rid_to_path
        except (KeyError, FileNotFoundError):
            logger.warning(f"未找到关系文件:{rels_path}")
            self._drawing_rels_cache[drawing_path] = {}
            return {}

    def _get_image_bytes(self, img_path: str) -> Optional[bytes]:
        """读取图片二进制数据，带缓存"""
        if img_path in self._image_cache:
            return self._image_cache[img_path]
        try:
            img_bytes = self._zip_file.read(img_path)
            self._image_cache[img_path] = img_bytes
            return img_bytes
        except KeyError:
            logger.warning(f"图片文件不存在{img_path}")
            self._image_cache[img_path] = None
    '工具方法---------------------------------------------------------------'
    @staticmethod
    def _build_rels_path(file_path: str) -> str:
        """根据文件路径构建对应的.rels文件路径"""
        p = Path(file_path)
        rels_dir = p.parent / "_rels"
        rels_file = rels_dir / (p.name + ".rels")
        return normpath(rels_file.as_posix())

    @staticmethod
    def _resolve_relative_path(base_path: str, target: str) -> str:
        """根据base_path和target计算出zip内的绝对路径"""
        base_dir = Path(base_path).parent
        abs_path = normpath((base_dir / target).as_posix())
        return abs_path
    '接口----------------------------------------------------'
    def get_float_images(
        self, sheet_name: str, load_bytes: bool = True
    ) -> list[FloatImageInfo]:
        """从指定表获得所有浮动图片"""
        # zf = self.open()
        if self._zip_file is None:
            raise RuntimeError("文件未打开，请使用'With ExcelImageExtractor(...) as ext'的方式打开")
        # 1. 获得sheet路径和关系ID
        sheet_info = self._get_sheet_info(sheet_name)
        if not sheet_info:
            logger.info(f"工作表{sheet_name}不存在")
            return []

        sheet_path, _ = sheet_info

        # 获取所有与该sheet关联的drawing文件路径
        drawing_paths = self._get_sheet_drawing_paths(sheet_path)
        if not drawing_paths:
            logger.info(f"工作表{sheet_name}没有浮动图片")
            return []

        # 遍历每个drawing文件
        all_images = []
        for drawing_path in drawing_paths:
            images = self._extract_images_from_drawing(drawing_path, sheet_name)
            all_images.extend(images)
        return all_images