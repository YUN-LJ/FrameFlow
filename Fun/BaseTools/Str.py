"""字符串操作"""


def del_part_str(org_str: str, del_str: str) -> str:
    """
    删除字符串中部分字符串

    :param org_str:原字符串
    :param del_str:需要删除的字符串内容
    如果能找到需要删除的字符串内容则返回删除后的字符串
    否则返回原字符串
    """
    index_find = org_str.find(del_str)
    if index_find != -1:
        org_str = org_str[:index_find] + org_str[index_find + len(del_str):]
    return org_str


def char_auto_line_break(text: str, limit_width: int) -> str:
    # 根据列宽自动调整文本换行符
    text_split = []
    weight = 0  # 权重,一个汉字的权重为21,其余字符权重为7
    for char in text:
        if weight > limit_width:
            text_split.append('\n')
            weight = 0
        weight += 21 if '\u4e00' <= char <= '\u9fff' else 7
        text_split.append(char)
    return ''.join(text_split)
