# encoding=utf-8
# @author xupingmao
# @since 2016/12/09
# @modified 2018/10/29 23:04:15
import time
import os
""" 
Commonly used format codes:

%Y  Year with century as a decimal number.
%m  Month as a decimal number [01,12].
%d  Day of the month as a decimal number [01,31].
%H  Hour (24-hour clock) as a decimal number [00,23].
%M  Minute as a decimal number [00,59].
%S  Second as a decimal number [00,61].
%z  Time zone offset from UTC.
%a  Locale's abbreviated weekday name.
%A  Locale's full weekday name.
%b  Locale's abbreviated month name.
%B  Locale's full month name.
%c  Locale's appropriate date and time representation.
%I  Hour (12-hour clock) as a decimal number [01,12].
%p  Locale's equivalent of either AM or PM.
"""


_DAY = 3600 * 24
FORMAT = '%Y-%m-%d %H:%M:%S'

def get_seconds(date = None):
    if date is None:
        return int(time.time())
    st = time.strptime(date, '%Y-%m-%d %H:%M:%S')
    return time.mktime(st)

def before(days=None, month=None, format=False):
    if days is not None:
        fasttime = time.time() - days * _DAY
        if format:
            return format_time(fasttime)
        return fasttime
    return None

def getyyyyMMdd(seconds=None):
    if seconds is None:
        return time.strftime("%Y%m%d")
    else:
        st = time.localtime(seconds)
        return time.strftime("%Y%m%d", st)

def get_date(seconds=None):
    return getyyyyMMdd(seconds)

def format_datetime(seconds=None):
    if seconds == None:
        return time.strftime('%Y-%m-%d %H:%M:%S')
    else:
        st = time.localtime(seconds)
        return time.strftime('%Y-%m-%d %H:%M:%S', st)

format_time = format_datetime


def format_time_only(seconds=None):
    if seconds == None:
        return time.strftime('%H:%M:%S')
    else:
        st = time.localtime(seconds)
        return time.strftime('%H:%M:%S', st)


def format_date(seconds=None, fmt = None):
    if fmt is None:
        fmt = "%Y-%m-%d"
    if seconds == None:
        return time.strftime(fmt)
    else:
        st = time.localtime(seconds)
        return time.strftime(fmt, st)

def parse_time(time_str):
    return get_seconds(time_str)

def format_millis(mills):
    return format_time(mills / 1000)

def get_current_year():
    return time.strftime("%Y")

def get_days_of_month(y, month):
    """get days of a month
        >>> get_days_of_month(2000, 2)
        29
        >>> get_days_of_month(2001, 2)
        28
        >>> get_days_of_month(2002, 1)
        31
    """
    days = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]
    if 2 == month:
        if (0 == y % 4) and (0 != y % 100) or (0 == y % 400):
            d = 29
        else:
            d = 28
    else:
        d = days[month-1]
    return d;

class Timer:

    def __init__(self, name = "[unknown]"):
        self.name = name

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.stop_time = time.time()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        import xutils
        self.stop()
        xutils.log("%s cost time: %s" % (self.name, self.cost()))


    def cost(self):
        return "%s ms" % int((self.stop_time - self.start_time) * 1000)

