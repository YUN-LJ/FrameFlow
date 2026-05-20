# 整个流程
# （用户）通过一个按钮，打开选择文件窗口，选择了xlsx文件 需求，无参函数
# （函数）打开选择文件窗口，拿到选择的文件地址
# （函数）加载文件，读取文本表清单
# （用户）选择需要使用的工作表
# （函数）读取所有图片内容
# （函数）对所有图片，进行通用OCR识别，根据识别结果使用银行卡OCR和身份证OCR进行二次识别，拿到精准结果
# （函数）在表格每条记录的右侧，添加相关的数据
# （用户）得到完成消息

import logging
import tkinter as tk
from tkinter import filedialog,ttk
import json
from pathlib import Path
import openpyxl
import openpyxl.worksheet
import base64
import zipfile
# from FrameFlow.SubAPI.ImageTools.my_image import _import_image,MyImage
from baidu_ocr import general_ocr,get_cached_access_token
from extractor import ExcelImageExtractor
# 配置项
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_PATH = 'extracted_images'
_MEMORY_FILE = Path.home() / ".file_selector_memory.json"
_DEFAULT_DIR = Path.home() / "Documents"

def _load_last_directory()->Path:
    """从文件中读取上次访问的目录位置"""
    if not _MEMORY_FILE.exists():
        return None
    try:
        with open(_MEMORY_FILE,'r',encoding ='utf-8') as f:
            data = json.load(f)
        last_dir = data.get('last_directory')
        if last_dir:
            path = Path(last_dir)
            if path.is_dir():
                return path
    except (json.JSONDecodeError,OSError,KeyError) as e:
        logger.warning(f'读取记忆文件失败：{e}')

def _save_last_directory(directory:Path)->None:
    """保存用户选择目录到记忆文件"""
    try:
        with open(_MEMORY_FILE,'w',encoding='utf-8')as f:
            json.dump({"last_directory":str(directory)},f,indent=2)
    except OSError as e:
        logger.warning(f"保存记忆文件失败：{e}")

def _openwindow()->Path:
    """打开文件选择窗口，返回所选文件路径；用户取消返回空字符串；不允许选择多个文件"""
    initial_dir = _load_last_directory()
    if not initial_dir or not initial_dir.exists():
        initial_dir = _DEFAULT_DIR if _DEFAULT_DIR.exists() else Path.home()


    # 创建根窗口并隐藏
    root = tk.Tk()
    root.withdraw()

    # 弹出文件选择对话框
    file_path = filedialog.askopenfilename(
        title='选择文件',
        initialdir=str(initial_dir),
        filetypes=[('xlsx文件',"*.xlsx")]
    )

    root.destroy()
    if file_path:
        selected= Path(file_path)
        _save_last_directory(selected.parent)
        return selected
    return Path()

def _select_sheet(wb:openpyxl.Workbook):
    """弹出选择工作表对话框，返回选中的工作表名"""
    sheet_names = wb.sheetnames
    if not sheet_names:
        print('工作簿中无工作表')
        return None
    
    win = tk.Toplevel()
    win.title('选择工作表')
    win.geometry('300x150')
    win.resizable(False,False)

    tk.Label(win,text="请选择要使用的工作表").pack(pady=10)
    combo = ttk.Combobox(win,values=sheet_names,state='readonly')
    combo.pack(pady=5)
    combo.current(0)

    result = [None]

    def on_ok():
        result[0] = combo.get()
        win.destroy()
    def on_cancel():
        win.destroy()
    
    tk.Button(win,text='确定',command=on_ok).pack(side=tk.LEFT,padx=20,pady=10)
    tk.Button(win,text='取消',command=on_cancel).pack(side=tk.RIGHT,padx=20,pady=10)

    win.grab_set()
    win.wait_window()
    return result[0]

# def _getimage(sheet:openpyxl.worksheet):
#     """获得图片"""
#     images_info= []
#     for img in sheet._images:
#         row = img.anchor._from.row + 1
#         col = img.anchor._from.col + 1
#         images_info.append((row,col,img))
#     return images_info

# def _extract_images_from_sheet(xlsx_path: Path, sheet: openpyxl.worksheet.worksheet.Worksheet):
#     """
#     从指定工作表中提取所有图片的二进制数据和所在行号
#     返回生成器，每个元素为 (row, image_bytes)
#     """
#     # 获取工作表名，用于定位对应的 drawing 关系
#     sheet_name = sheet.title

#     # 使用 openpyxl 的 _images 属性获取图片锚点信息（不读取二进制数据）
#     if not hasattr(sheet, '_images') or not sheet._images:
#         logger.info(f"工作表 {sheet_name} 中没有图片")
#         return
#     for img in sheet._images:
#         # 拿到锚点信息
#         row = img.anchor._from.row + 1
#         print(row)
#         # 拿到路径信息
#         path = img.path
#         print(path)

    # 拿到所有图片
    # rows = []
    # for img in sheet._images:
    #     row = img.anchor._from.row + 1
    #     rows.append(row)

    # media_files = []
    # with zipfile.ZipFile(xlsx_path, 'r') as zf:
    #     for name in sorted(zf.namelist()):
    #         if name.startswith('xl/media/'):
    #             media_files.append(zf.read(name))    

    
    # zip_data = {}
    # with zipfile.ZipFile(xlsx_path, 'r') as zf:
    #     for name in zf.namelist():
    #         if name.startswith('xl/media/'):
    #             zip_data[name] = zf.read(name)
    
    # if len(rows) != len(media_files):
    #     logger.warning(f"图片数量({len(rows)})与 media 文件数量({len(media_files)})不匹配，将按索引匹配")

    # for idx, row in enumerate(rows):
    #     if idx < len(media_files):
    #         yield row, media_files[idx]
    #     else:
    #         logger.warning(f"第 {idx+1} 个图片没有对应的文件")




# def _getimage(xlsx_path:Path,sheet: openpyxl.worksheet.worksheet.Worksheet):
#     """获得图片（迭代器版本）"""

#     return _extract_images_from_sheet(xlsx_path,sheet)

class _MyImages:
    
    def __init__(self,xlsx_path,sheet):
        self.imgs_list = self._read_from_zip()

        self.imgs = self._get_image()
    # def get_data(self) -> bytes:
    #     """返回图片二进制数据（只读一次，后续从缓存返回）"""
    #     if self._cached_data is None:
    #         self._cached_data = self._read_from_zip()
    #     return self._cached_data
    def _get_image(self):
        for img in self.imgs_list:
            row = img.anchor._from.row + 1
            yield row,img
    def _read_from_zip(self):
        """从原始xlsx文件中读取图片数据，带详细的调试输出"""
        if not self._xlsx_path.exists():
            raise FileNotFoundError(f"Excel文件不存在: {self._xlsx_path}")

        with zipfile.ZipFile(self._xlsx_path, 'r') as zf:
            # 调试：列出ZIP内所有顶级目录和media文件
            all_files = zf.namelist()
            # media_files = [f for f in all_files if f.startswith('xl/media/')]
            return all_files


def _image2base64(img_bytes)->str:
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    return img_base64


    
def _find_data_start_row(sheet):
    """找到第一条数据行（A列为数字且不为空的行）"""
    for row in range(1, sheet.max_row + 1):
        cell_value = sheet.cell(row=row, column=1).value
        if cell_value is not None and isinstance(cell_value, (int, float)) and cell_value != '':
            return row
    return None




def excel_process():
    file_path = _openwindow()
    if not file_path:
        print('未选择文件')
        return
    wb = openpyxl.load_workbook(filename=file_path)
    selected_sheet = _select_sheet(wb)
    if selected_sheet:
        sheet = wb[selected_sheet]
    else:
        print('未选择工作表')
        return
    
    data_start_row = _find_data_start_row(sheet)
    if data_start_row is None:
        print('未找到数据行')
        return

    header_row = data_start_row - 1

    max_col = sheet.max_column
    new_id_col = max_col + 1
    new_bankcard_col = max_col + 2
    new_bankname_col = max_col + 3
    sheet.cell(row=header_row, column=new_id_col, value="身份证号")
    sheet.cell(row=header_row, column=new_bankcard_col, value="银行卡号")
    sheet.cell(row=header_row, column=new_bankname_col, value="开户行")
    
    # images = _getimage(file_path,sheet)
    e_extor = ExcelImageExtractor(file_path)
    images = e_extor.get_float_images(selected_sheet)
    if not images:
        logger.info('当前工作表中没有图片')
        return


    try:
        access_token = get_cached_access_token()
    except Exception as e:
        logger.error(f'无法获得access_token:{e}')
        return
    
    for row, img_bytes in images:
        # raw_data = my_img.get_data()
        img_base64 = _image2base64(img_bytes)
        # print('目前执行到此为止')
        # exit()
        result = general_ocr(img_base64,access_token)
        if not result:
            logger.error('OCR无结果返回')
        else:
            if result['type'] == 'idcard':
                sheet.cell(row=row,column=new_id_col,value=result['data'][1])
            if result['type'] == 'bankcard':
                sheet.cell(row=row,column=new_bankcard_col,value=result['data'][0])
                sheet.cell(row=row,column=new_bankname_col,value=result['data'][3])

    output_path = file_path.parent / f"{file_path.stem}_processed.xlsx"
    wb.save(output_path)
    logger.info("完成", f"处理完成！\n结果已保存至：{output_path}")


if __name__ == "__main__":
    # 创建主窗口
    root = tk.Tk()
    root.title("Excel 图片识别工具")
    root.geometry("400x200")
    root.resizable(False, False)

    # 说明标签
    label = tk.Label(
        root,
        text="点击按钮选择 Excel 文件，\n程序将自动识别其中的身份证/银行卡图片\n并将结果写入新文件。",
        justify="left",
        pady=20
    )
    label.pack()

    # 按钮直接绑定无参函数 excel_process()
    btn = tk.Button(
        root,
        text="开始处理",
        command=excel_process,   # 注意：excel_process 必须定义为无参数函数
        width=20,
        height=2,
        bg="#4CAF50",
        fg="white"
    )
    btn.pack(pady=20)

    # 运行主循环
    root.mainloop()