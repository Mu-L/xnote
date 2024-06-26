# -*- coding:utf-8 -*-
# @author xupingmao <578749341@qq.com>
# @since 2020/11/28 23:23:13
# @modified 2022/04/16 22:47:23
import copy
import sys
import traceback

IS_PY2 = sys.version_info[0] == 2

if IS_PY2:
    string_types = (basestring,)
else:
    string_types = (str,)


class Storage(dict):
    """
    A Storage object is like a dictionary except `obj.foo` can be used
    in addition to `obj['foo']`. (This class is modified from web.py)
    
        >>> o = storage(a=1)
        >>> o.a
        1
        >>> o['a']
        1
        >>> o.a = 2
        >>> o['a']
        2
        >>> o.noSuchKey
        None
    """
    def __init__(self, **kw):
        # default_value会导致items等函数出问题
        # self.default_value = default_value
        super(Storage, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            return None
    
    def __setattr__(self, key, value): 
        self[key] = value
    
    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __deepcopy__(self, memo):
        if memo is None:
            memo = {}
        old_value = memo.get(id(self))
        if old_value != None:
            return old_value

        result = Storage()
        for key in self:
            value = self[key]
            result[key] = copy.deepcopy(value)
        return result
    
    def __repr__(self):     
        return '<MyStorage ' + dict.__repr__(self) + '>'


class XnoteException(Exception):
    def __init__(self, code="500", message=""):
        super(XnoteException, self).__init__(message)
        self.code = code
        self.message = message


def print_exc():
    """打印系统异常堆栈"""
    exc_info = traceback.format_exc()
    print(exc_info)
    return exc_info

def print_stacktrace():
    print_exc()

def is_str(s):
    return isinstance(s, string_types)
