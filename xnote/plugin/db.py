from xnote.core import xconfig
from xnote.core import xtables

def create_plugin_table(table_name="", pk_name="id", pk_type="bigint"):
    return xtables.create_default_table_manager(
        table_name=table_name, pk_name=pk_name, pk_type=pk_type, 
        is_plugin = True, check_table_define = False)

get_plugin_table = xtables.get_table_by_name