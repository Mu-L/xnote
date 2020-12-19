# encoding=utf-8
# @author xupingmao
# @since 2016/12/09
# @modified 2020/12/19 19:58:42
import logging
import time
import inspect
import os
from xutils import fsutil
from xutils.dateutil import format_time
from xutils.imports import u

# def get_prefix():
#     return time.strftime("%Y-%m-%d %H:%M:%S")

# def debug(fmt, *argv):
#     msg = fmt.format(*argv)
#     prefix = get_prefix()
#     print(prefix, msg)

# def info(fmt, *argv):
#     msg = fmt.format(*argv)
#     prefix = get_prefix()
#     print(prefix, msg)

# def warn(fmt, *argv):
#     msg = fmt.format(*argv)
#     prefix = get_prefix()
#     print(prefix, msg)

# def error(fmt, *argv):
#     msg = fmt.format(*argv)
#     prefix = get_prefix()
#     print(prefix, msg)

# def fatal(fmt, *argv):
#     msg = fmt.format(*argv)
#     prefix = get_prefix()
#     print(prefix, msg)

def async_func_deco():
    """同步调用转化成异步调用的装饰器"""
    def deco(func):
        def handle(*args, **kw):
            import xmanager
            xmanager.put_task(func, *args, **kw)
        return handle
    return deco

logger = None
def init_logger():
    global logger
    # filename = os.path.join(xconfig.LOG_DIR, "xnote.log")
    # fmt_str  = '%(asctime)s %(levelname)s %(message)s'
    # fileshandle = logging.handlers.TimedRotatingFileHandler(filename, when='MIDNIGHT', interval=1, backupCount=0)
    # fileshandle.suffix = "%Y-%m-%d"
    # fileshandle.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(fmt_str)
    # fileshandle.setFormatter(formatter)
    # logger = logging.getLogger('')
    # logger.setLevel(logging.INFO)
    # logger.addHandler(fileshandle)

    # logger.info("logger inited!")

def get_log_path():
    import xconfig
    date_time = time.strftime("%Y-%m")
    dirname = os.path.join(xconfig.LOG_DIR, date_time)
    fsutil.makedirs(dirname)
    fname = time.strftime("xnote.%Y-%m-%d.log")
    return os.path.join(dirname, fname)

def log(fmt, show_logger = False, fpath = None, *argv):
    fmt = u(fmt)
    if len(argv) > 0:
        message = fmt.format(*argv)
    else:
        message = fmt
    if show_logger:
        f_back    = inspect.currentframe().f_back
        f_code    = f_back.f_code
        f_modname = f_back.f_globals.get("__name__")
        f_name    = f_code.co_name
        f_lineno  = f_back.f_lineno
        message = "%s %s.%s:%s %s" % (format_time(), f_modname, f_name, f_lineno, message)
    else:
        message = "%s %s" % (format_time(), message)
    print(message)
    if fpath is None:
        fpath = get_log_path()
    log_async(fpath, message)

def _write_log(level, metric, message, cost):
    import xauth
    fpath = get_log_path()
    user_name = xauth.current_name()
    if user_name is None:
        user_name = "-"
    full_message = "%s|%s|%s|%s|%sms|%s" % (format_time(), level, user_name, metric, cost, message)
    # print(full_message)
    # 同步写在SAE上面有巨大的性能损耗
    log_async(fpath, full_message)

def trace(metric, message, cost=0):
    _write_log("TRACE", metric, message, cost)
    

def info(metric, message, cost=0):
    _write_log("INFO", metric, message, cost)

def warn(metric, message, cost=0):
    _write_log("WARN", metric, message, cost)

def error(metric, message, cost=0):
    _write_log("ERROR", metric, message, cost)

@async_func_deco()
def log_async(fpath, full_message):
    with open(fpath, "ab") as fp:
        fp.write((full_message+"\n").encode("utf-8"))


def log_init_deco(message):
    """日志装饰器"""
    def deco(func):
        def handle(*args, **kw):
            log(message + " starting ...")
            try:
                result = func(*args, **kw)
                log(message + " finished")
                return result
            except Exception as e:
                log(message + " failed")
                raise e
        return handle
    return deco


