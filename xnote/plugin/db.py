from xnote.core import xconfig
from xnote.core import xtables

def create_plugin_table(table_name="", comment="", pk_name="id", **kw):
    kw["comment"] = comment
    return xtables.create_default_table_manager(
        table_name=table_name, pk_name=pk_name,
        is_plugin = True, check_table_define = False, **kw)

get_plugin_table = xtables.get_table_by_name