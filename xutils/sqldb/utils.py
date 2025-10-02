# -*- coding:utf-8 -*-
"""
@Author       : xupingmao
@email        : 578749341@qq.com
@Date         : 2024-02-15 21:19:48
@LastEditors  : xupingmao
@LastEditTime : 2024-02-15 21:39:31
@FilePath     : /xnote/xutils/sqldb/utils.py
@Description  : 描述
"""

def safe_str(obj, max_length=-1):
    if obj == None:
        return ""
    value = str(obj)
    if max_length > 0:
        return value[:max_length]
    return value

    
def escape_like(value: str, escape_char: str = "!") -> str:
    """
    转义 LIKE 查询中的特殊字符
    
    :param value: 用户输入的原始字符串
    :param escape_char: 自定义转义字符（默认 '!'）
    :return: 转义后的安全字符串
    """
    # 需要转义的特殊字符
    special_chars = {'%', '_', escape_char}
    # 遍历转义
    result = []
    for ch in value:
        if ch in special_chars:
            result.append(escape_char)
        result.append(ch)
    return "".join(result)

def remove_like_wildcard(text: str):
    """移除 LIKE 查询的通配符"""
    text = text.replace("%", "")
    text = text.replace("_", "")
    return text