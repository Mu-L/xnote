# encoding=utf-8
from BaseHandler import *
from FileDB import FileDO

"""FileDB cache"""
import copy

def file_dict(id, name, related):
    return dict(id = id, name = name, related = related)

class FileFilter:

    def __init__(self, file_list = None):
        # self.name_list = name_list
        # self.related_list = related_list
        self._files = {}
        if file_list:
            self._sync_list(file_list)

    def init(self, file_list):
        self._sync_list(file_list)

    def _sync_list(self, file_list):
        for file in file_list:
            self._files[file["id"]] = file

    def _sync(self, id, name, related):
        self._files[id] = [name, related]

    def sync(self, id, file):
        self._files[id] = file

    def search(self, words, hide=True):
        """search file with words"""
        result = []
        for id in self._files:
            file = self._files[id]
            related = file.get("related")
            if hide and textutil.contains(related, "HIDE"):
                continue
            if textutil.contains(related, words):
                result.append(copy.copy(file))
        return result

    def filter(self, fnc):
        result = []
        for id in self._files:
            file = self._files[id]
            if fnc(file):
                result.append(copy.copy(file))
        return result

def do_search(words, key=None):
    context = {}
    context["key"] = key
    context["search_result"] = []
    name_results = FileDB.search_name(words)
    FileDB.full_search(context, words)
    # files = self._service.search(words)
    content_results = context['files']

    nameset = set()
    for item in name_results:
        nameset.add(item.name)

    files = name_results

    for item in content_results:
        if item.name not in nameset:
            files.append(item)
    return files

def do_calc(words, key):
    exp = " ".join(words[1:])
    try:
        value = eval(exp)
        f = FileDO("计算结果")
        f.content = str(value)
        return [f]
    except Exception as e:
        print(e)
        return []

class handler(BaseHandler):

    def search_models(self, words):
        modelManager = config.get("modelManager")
        if modelManager is not None:
            return modelManager.search(words)
        return []

    def py_execute(self, exp):

        try:
            value = eval(exp)
            rule = Storage()
            rule.html = "<p>计算结果: %s</p>" % value
            return rule
        except Exception as e:
            print_exception(e)


    def full_search(self):
        key = self.get_argument("key", "").strip()
        if key is None or key == "":
            result = {}
            files = []
        else:
            words = textutil.split_words(key)
            op = words[0]
            if op == "calc":
                files = do_calc(words, key)
            else:
                files = do_search(words, key)

        self.render("file-list.html", key = key, 
            files = files, count=len(files), full_search="on")


    """ search files by name and tags """
    def default_request(self):
        key = self.get_argument("key", None)
        full_search = self.get_argument("full_search", None)
        # if full_search == "on":
        #     return self.full_search();
        if key is None or key == "":
            raise web.seeother("/")
        else:
            return self.full_search()
            words = textutil.split_words(key)
            context = {}
            context["key"] = key
            context["search_result"] = []
            # result = event.fire_with_context("search", context, words)
            # files = self._service.search(words)
            tools = self.search_models(words)
            # context["search_result"].insert(0, link_rule)
            files = FileDB.search_name(words)

            search_result = []

            #rule1 = self.py_execute(key)
            #if rule1 is not None:
            #    search_result.append(rule1)

            # if len(files) == 0:
            #     event.fire("search-miss", words)
        self.render("file-list.html", key = key, 
            files = files, count=len(files), 
            tools = tools,
            search_result = search_result)

name = "搜索"
description = "xnote搜索，可以搜索笔记、工具"