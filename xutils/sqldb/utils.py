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

import typing
from web.db import SqliteDB
from xutils.base import BaseDataRecord
from typing import Optional

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

class SqliteColumnInfo(BaseDataRecord):
    def __init__(self):
        self.cid = 0
        self.name = ""
        self.type = ""
        self.notnull = 0
        self.dflt_value = None
        self.pk = 0

class SqliteTableStruct:
    def __init__(self) -> None:
        self.pk_column: Optional[SqliteColumnInfo] = None
        self.columns: typing.List[SqliteColumnInfo] = []

def get_sqlite_table_struct(db_path: str, table_name: str):
    db = SqliteDB(db = db_path)
    rows = db.query(f"pragma table_info({table_name})")
    column_info_list = SqliteColumnInfo.from_dict_list(rows)

    result = SqliteTableStruct()
    result.columns = column_info_list

    for item in column_info_list:
        if item.pk:
            result.pk_column = item
            break
    return result


