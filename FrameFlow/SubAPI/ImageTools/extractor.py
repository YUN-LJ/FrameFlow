from posixpath import normpath
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class ExcelImageExtractor:
    """Excel浮动图片提取器"""

    def __init__(self, xlsx_path):
        self.xlsx_path = Path(xlsx_path)
        if not self.xlsx_path.exists():
            raise FileNotFoundError(f"文件不存在: {xlsx_path}")

    def get_float_images(self, sheet_name: str) -> List[Any]:
        """从指定表获得所有浮动图片"""
        with zipfile.ZipFile(self.xlsx_path, 'r') as zf:
            # 1. 获得所有drawing文件路径
            drawing_paths = self._get_sheet_drawing_paths(sheet_name, zf)
            if not drawing_paths:
                logger.info(f"工作表{sheet_name}没有浮动图片")
                return

            # 遍历每个drawing文件
            all_images = []
            for drawing_path in drawing_paths:
                images = self._extract_from_drawing(drawing_path, zf)
                all_images.extend(images)
            return all_images

    def _get_sheet_drawing_paths(self, sheet_name: str, zf: zipfile.ZipFile) -> List[str]:
        """获得所有与指定sheet关联的drawing文件路径"""
        try:
            wb_tree = ET.parse(zf.open('xl/workbook.xml'))
            root = wb_tree.getroot()
            ns = {
                'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
                'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
            }
            sheet_r_id = None
            for sheet in root.findall('.//main:sheet', ns):
                if sheet.get('name') == sheet_name:
                    sheet_r_id = sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                    break
            if not sheet_r_id:
                return []

            # sheet_r_id 存在，读取workbook.xml.rels 获取sheet文件路径

            rels_tree = ET.parse(zf.open('xl/_rels/workbook.xml.rels'))
            rels_root = rels_tree.getroot()
            sheet_path = None
            for rel in rels_root.findall(
                    './/{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
                if rel.get('Id') == sheet_r_id:
                    sheet_path = f"xl/{rel.get('Target')}"
                    break
            if not sheet_path:
                return []

            # 读取sheet的rels文件，找到所有drawing关系
            sheet_rels_path = Path(sheet_path).parent / '_rels' / (Path(sheet_path).name + '.rels')
            sheet_rels_path_posix = normpath(sheet_rels_path.as_posix())
            try:
                sheet_rels_tree = ET.parse(zf.open(str(sheet_rels_path_posix)))
                sheet_rels_root = sheet_rels_tree.getroot()
                drawing_paths = []
                for rel in sheet_rels_root.findall(
                        './/{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
                    if rel.get('Type') == 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing':
                        target = rel.get('Target')
                        abs_path = normpath((Path(sheet_path).parent / target).as_posix())
                        abs_path = abs_path.lstrip('/')
                        if not abs_path.startswith('xl/'):
                            abs_path = 'xl/' + abs_path
                        drawing_paths.append(abs_path)
                return drawing_paths
            except KeyError:
                logging.warning(f"未找到sheet的关系文件:{sheet_rels_path_posix}")
                return []
        except Exception as e:
            logger.error(f'获取工作表drawing失败:{e}')
            return []

    def _extract_from_drawing(self, drawing_path: str, zf: zipfile.ZipFile) -> List[Tuple[int, bytes]]:
        """从单个drawing XML提取图片信息，返回列表"""
        results = []
        drawing_path = normpath(drawing_path)
        try:
            drawing_tree = ET.parse(zf.open(drawing_path))
            root = drawing_tree.getroot()
            ns = {
                'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
                'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
            }

            pic_list = []
            for anchor in root.findall('.//xdr:twoCellAnchor', ns):
                from_row = anchor.find('.//xdr:from/xdr:row', ns)
                if from_row is None:
                    continue
                row = int(from_row.text) + 1
                blip = anchor.find('.//a:blip', ns)
                if blip is not None:
                    r_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    if r_id:
                        pic_list.append((row, r_id))

            #
            for anchor in root.findall('.//xdr:oneCellAnchor', ns):
                from_row = anchor.find('.//xdr:from/xdr:row', ns)
                if from_row is None:
                    continue
                row = int(from_row.text) + 1
                blip = anchor.find('.//a:blip', ns)
                if blip is not None:
                    r_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    if r_id:
                        pic_list.append((row, r_id))

            if not pic_list:
                return []

            # 解析drawing对应的rels文件，获取rId->media路径
            # rels_path = drawing_path.replace('.xml','.xml.rels').replace('xl/drawings/','xl/drawings/_rels')
            # if not rels_path.startswith('xl/drawing/_rels'):
            #     drawing_dir = Path(drawing_path).parent
            #     rels_path = (drawing_dir / '_rels'/(Path(drawing_path).name + '.rels')).as_posix()
            rels_path = normpath(
                ((Path(drawing_path).parent) / '_rels' / (Path(drawing_path).name + '.rels')).as_posix())
            try:
                rels_tree = ET.parse(zf.open(rels_path))
                rels_root = rels_tree.getroot()
                rid_to_target = {}
                for rel in rels_root.findall(
                        './/{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
                    rid = rel.get('Id')
                    target = rel.get('Target')
                    if rid and target:
                        abs_target = normpath((Path(drawing_path).parent / target).as_posix())
                        if not abs_target.startswith('xl/'):
                            abs_target = 'xl/' + abs_target
                        rid_to_target[rid] = abs_target
            except KeyError:
                logger.warning(f"未找到关系文件:{rels_path}")
                return []

            for row, r_id in pic_list:
                target_path = rid_to_target.get(r_id)
                if target_path:
                    try:
                        img_bytes = zf.read(target_path)
                        results.append((row, img_bytes))
                    except KeyError:
                        logger.warning(f"图片文件不存在:{target_path}")
                else:
                    logger.warning(f"未找到 rId = {r_id}对应的图片路径")
            return results
        except Exception as e:
            logger.error(f"解析drawing文件{drawing_path}失败:{e}")
            return []
