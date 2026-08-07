import openpyxl


def find_data_start_row(sheet: openpyxl.worksheet.worksheet.Worksheet) -> int | None:
    """
    找到第一条数据行（A列值为数字且不为空的行）。
    若找不到则返回 None。
    """
    for row in range(1, sheet.max_row + 1):
        cell_value = sheet.cell(row=row, column=1).value
        if cell_value is not None and isinstance(cell_value, (int, float)):
            return row
    return None