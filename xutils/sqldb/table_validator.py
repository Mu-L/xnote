
def validate_index_name(index_name="", is_unique=False):
    if index_name == "":
        return
    if is_unique:
        assert index_name.startswith("uk_")
    else:
        assert index_name.startswith("idx_")
        