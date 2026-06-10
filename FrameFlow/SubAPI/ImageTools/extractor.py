from dataclasses import dataclass
from functools import cached_property, lru_cache
import logging
from pathlib import Path
from typing import Any, BinaryIO, Callable, Dict, List, Optional, Tuple, Union
from xml.etree import ElementTree as ET
import zipfile


@dataclass
class ExtractionRule:
    """提取规则"""

    path: str  # 相对于上下文的XPath
    attributes: Optional[Dict[str, str]]  # 属性映射 {目标字段名:属性名}
    children: Optional[List["ExtractionRule"]] = None  # 子规则，嵌套用
    text_field: Optional[str] = None  # 存到哪个字段
    multiple: bool = False  # 是否匹配多个元素，返回列表
    transform: Optional[Callable[[Any], Any]] = None  # 可选的值转换函数


class ExcelFloatImageExtractor:
    NAMESPACES = {
        "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "xdr": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "pkg": "http://schemas.openxmlformats.org/package/2006/relationships",
    }
    EXTRACTION_RULES: Dict[str, ExtractionRule] = {
        "workbook": ExtractionRule(
            path="main:sheet",
            attributes={"name": "name", "sheet_rid": "r:id"},
            multiple=True,
        ),  # <sheet name="Sheet1 (2)" sheetId="2" r:id="rId1"/>
        "workbook_rel": ExtractionRule(
            path="r:Relationship",
            attributes={"rid": "Id", "target": "Target"},
            multiple=True,
        ),  # .rel文件默认命名空间为r, 元素名Relationship,属性名Id和Target <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
        "sheet": ExtractionRule(
            path="main:drawing", attributes={"drawing_rid": "r:id"}, multiple=False
        ),  # <drawing r:id="rId1"/>
        "sheet_rel": ExtractionRule(
            path="r:Relationship",
            attributes={"drid": "Id", "target": "Target"},
            multiple=True,
        ),  # <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing" Target="../drawings/drawing1.xml"/>
        "drawing_twocellanchor": ExtractionRule(
            path="xdr:twoCellAnchor",
            multiple=True,
            children=[
                ExtractionRule(
                    path="xdr:from",
                    children=[
                        ExtractionRule(path="xdr:col", text_field="col"),
                        ExtractionRule(path="xdr:colOff", text_field="colOff"),
                        ExtractionRule(path="xdr:row", text_field="row"),
                        ExtractionRule(path="xdr:rowOff", text_field="rowOff"),
                    ],
                ),
                ExtractionRule(
                    path="xdr:to",
                    children=[
                        ExtractionRule(path="xdr:col", text_field="col"),
                        ExtractionRule(path="xdr:colOff", text_field="colOff"),
                        ExtractionRule(path="xdr:row", text_field="row"),
                        ExtractionRule(path="xdr:rowOff", text_field="rowOff"),
                    ],
                ),
                ExtractionRule(
                    path=".//a:blip",
                    attributes={"embed_rid": "r:embed"},
                ),
            ],
        ),
        "drawing_onecellanchor": ExtractionRule(
            path="xdr:oneCellAnchor",
            multiple=True,
            children=[
                ExtractionRule(
                    path="xdr:from",
                    children=[
                        ExtractionRule(path="xdr:col", text_field="col"),
                        ExtractionRule(path="xdr:colOff", text_field="colOff"),
                        ExtractionRule(path="xdr:row", text_field="row"),
                        ExtractionRule(path="xdr:rowOff", text_field="rowOff"),
                    ],
                ),
                ExtractionRule(
                    path="xdr:ext",
                    attributes={"cx": "cx", "cy": "cy"},
                ),
                ExtractionRule(
                    path=".//a:blip",
                    attributes={"embed_rid": "r:embed"},
                ),
            ],
        ),
        "drawing_absoluteanchor": ExtractionRule(
            path="xdr:absoluteAnchor",
            multiple=True,
            children=[
                ExtractionRule(
                    path="xdr:pos",
                    attributes={"x": "x", "y": "y"},
                ),
                ExtractionRule(
                    path="xdr:ext",
                    attributes={"cx": "cx", "cy": "cy"},
                ),
                ExtractionRule(
                    path=".//a:blip",
                    attributes={"embed_rid": "r:embed"},
                ),
            ],
        ),
        "drawing_rel": ExtractionRule(
            path="pkg:Relationship",
            attributes={"rid": "Id", "target": "Target"},
            multiple=True,
        ),  # <Relationship Id="rId8" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/image8.jpeg"/>
    }

    def __init__(self, source: Union[str, Path, BinaryIO], image_cache_size: int = 4):
        self._source = source
        self._zip_file: zipfile.ZipFile = None  # 延迟打开

        self._image_cache: Dict[str, bytes] = {}
        self._image_cache_order: List[str] = []
        self._image_cache_size = image_cache_size

        # 工作表级缓存：因为cached_property不能缓存带有参数的函数，所以简单使用装饰器作为缓存
        self._sheet_drawing_cache:Dict[str,str]={}
        self._draw_anchors_cache:Dict[str,List[str]] = {}


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

    def _extract_from_xml(
        self,
        extract_strategy: str,
        source: str,
    ) -> list:
        """通用XML属性提取函数"""
        if self._zip_file is None:
            raise RuntimeError("must use in 'with' block")
        if extract_strategy not in self.EXTRACTION_RULES:
            raise ValueError(f"Unknown extract strategy:{extract_strategy}")

        zf = self._zip_file
        tree = ET.parse(zf.open(source))
        root = tree.getroot()

        rule: ExtractionRule = self.EXTRACTION_RULES.get(extract_strategy)
        return self.extract_by_rule(root, rule, self.NAMESPACES)

    @classmethod
    def extract_by_rule(
        cls, root: ET.Element, rule: ExtractionRule, namespaces: Dict[str, str]
    ):
        elements = root.findall(rule.path, namespaces)
        if not elements:
            return [] if rule.multiple else None
        if rule.multiple:
            return [cls.extract_single(e, rule, namespaces) for e in elements]
        return cls.extract_single(elements[0], rule, namespaces)

    @classmethod
    def extract_single(
        cls, elem: ET.Element, rule: ExtractionRule, namespaces: Dict[str, str]
    ):
        result = {}
        if rule.attributes:
            for field, attr_name in rule.attributes.items():
                value = elem.get(attr_name)
                if value is not None:
                    result[field] = value
        if rule.text_field is not None:
            result[rule.text_field] = elem.text

        if rule.children:
            for child_rule in rule.children:
                child_result = cls.extract_by_rule(elem, child_rule, namespaces)
                if child_result is not None:
                    if isinstance(child_result, dict):
                        result.update(child_result)
                    else:
                        key = child_rule.path.split(":")[-1].split("/")[-1]
                        result[key] = child_result

        if rule.transform and result:
            result = rule.transform(result)

        return result

    @staticmethod
    def _get_relative_file(source) -> str:
        """从传入的xml文件获取对应的.rel关系文件"""
        source_dir = Path(source).parent
        source_name = Path(source).name
        rels_path = source_dir / "_rels" / f"{source_name}.rels"
        return str(rels_path)

    @staticmethod
    def path_resolve(path: Union[str, Path]) -> str:
        path = path.replace("\\", "/")
        return path

    "---------------------簿级缓存-----------------------------------------"

    @cached_property
    def sheet_name_to_rid(self) -> dict:
        # <sheet name="Sheet1 (2)" sheetId="2" r:id="rId1"/>
        items = self._extract_from_xml("workbook", "workbook.xml")
        return {item["name"]: item["sheet_rid"] for item in items}

    @cached_property
    def sheet_rid_to_path(self) -> dict:
        items = self._extract_from_xml("workbook_rel", "_rels/workbook.xml.rels")
        return {item["rid"]: self.path_resolve(item["target"]) for item in items}

    def get_path_by_sheet_name(self, sheet_name) -> str:
        rid = self.sheet_name_to_rid.get(sheet_name)
        if rid is None:
            raise KeyError
        path = self.sheet_rid_to_path.get(rid)
        if path is None:
            raise KeyError
        return path

    "表级缓存-----------------------------------------------------"
    "存曾打开过的sheet的drawing关联信息，因为表一般不会太多，所以全缓存"

    
    def get_drawing_rid(self, sheet_file: str)->str:
        if sheet_file in self._sheet_drawing_cache:
            return self._sheet_drawing_cache[sheet_file]
        item = self._extract_from_xml("sheet", sheet_file)
        self._sheet_drawing_cache[sheet_file]=item["drawing_rid"]
        return self._sheet_drawing_cache[sheet_file]

    
    def get_drawing_path(self, sheet_rel_file: str) -> str:
        if sheet_rel_file in self._draw_anchors_cache:
            return self._draw_anchors_cache[sheet_rel_file]
        item = self._extract_from_xml("sheet_rel", sheet_rel_file)
        self._draw_anchors_cache[sheet_rel_file]=self.path_resolve(item["target"])
        return self._draw_anchors_cache[sheet_rel_file]

    def get_drawing_path_by_sheet(self,sheet_file:str):
        sheet_rel_file = self._get_relative_file(sheet_file)
        sheet_rid = self.get_drawing_rid(sheet_file)
        drawing_path = self.get_drawing_path(sheet_rel_file)
        



    "drawing缓存----------------------------------------------------"
    "drawing得到的是一大堆锚点的信息与对应的图片链接，本身内存占用不大？保留整个列表？字典？"

    
    def all_anchor(self, drawing_file: str):
        anchors = []
        anchors.append(self._extract_from_xml("drawing_twocellanchor", drawing_file))
        anchors.append(self._extract_from_xml("drawing_onecellanchor", drawing_file))
        anchors.append(self._extract_from_xml("drawing_absoluteanchor", drawing_file))
        return anchors

    "image缓存------------------------------------------------------------"
    "应该会占用较大内存？姑且默认值为4"

    def _get_image_data(self, drawing_path: str, embed_rid: str) -> Optional[bytes]:
        drawing_rel_path = self._get_relative_file(drawing_path)
        try:
            rel_items = self._extract_from_xml("drawing_rel", drawing_rel_path)
        except (KeyError, FileNotFoundError):
            return None

        target = None
        for item in rel_items:
            if item.get("rid") == embed_rid:
                target = item.get("target")
                break
        if target is None:
            return None

        base_dir = Path(drawing_path).parent
        image_path = self.path_resolve(base_dir / target)

        # LRU缓存逻辑
        if image_path in self._image_cache:
            # 移动到最近使用
            self._image_cache_order.remove(image_path)
            self._image_cache_order.append(image_path)
            return self._image_cache[image_path]
        if self._zip_file is None:
            raise RuntimeError("Zip file not opened")
        try:
            data = self._zip_file.read(image_path)
        except KeyError:
            return None

        # 缓存管理
        if len(self._image_cache) >= self._image_cache_size:
            # 淘汰最久未使用的
            oldest = self._image_cache_order.pop(0)
            del self._image_cache[oldest]

        self._image_cache[image_path] = data
        self._image_cache_order.append(image_path)
        return data

    # ------------------ 公共接口 ------------------------------------------
    def get_floating_images(
        self, sheet_name: str, include_image_data: bool = True
    ) -> List[dict]:
        """
        获取指定工作表中的所有浮动图片信息。
        返回列表，每个元素包含：
            - type: 锚点类型 ("twoCellAnchor"/"oneCellAnchor"/"absoluteAnchor")
            - 位置信息 (col, row, colOff, rowOff 等，取决于类型)
            - image_data (bytes, 可选，仅当 include_image_data=True)
            - image_path (str, 图片在 zip 中的路径)
        """
        drawing_path = self._get_drawing_path_by_sheet(sheet_name)
        if drawing_path is None:
            return []  # 该表没有浮动图片

        anchors = self._parse_drawing(drawing_path)
        result = []
        for anchor in anchors:
            embed_rid = anchor.get("embed_rid")
            if not embed_rid:
                continue

            info = {
                "type": anchor["type"],
            }
            # 复制位置/尺寸字段
            for key in ["col", "row", "colOff", "rowOff", "cx", "cy", "x", "y"]:
                if key in anchor:
                    info[key] = anchor[key]

            # 获取图片路径
            drawing_rel_path = self._get_relative_file(drawing_path)
            try:
                rel_items = self._extract_from_xml("drawing_rel", drawing_rel_path)
            except (KeyError, FileNotFoundError):
                continue
            target = None
            for item in rel_items:
                if item.get("rid") == embed_rid:
                    target = item.get("target")
                    break
            if target is None:
                continue
            base_dir = Path(drawing_path).parent
            image_path = self.path_resolve(base_dir / target)
            info["image_path"] = image_path

            if include_image_data:
                data = self._get_image_data(drawing_path, embed_rid)
                info["image_data"] = data
            result.append(info)

        return result

        
        