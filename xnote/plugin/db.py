from xnote.core import xconfig
from xnote.core import xtables

def create_plugin_table(table_name="", pk_name="id", pk_type="bigint", is_backup = False):
    return xtables.create_default_table_manager(
        table_name=table_name, pk_name=pk_name, pk_type=pk_type, is_backup=is_backup)

get_plugin_table = xtables.get_table_by_name