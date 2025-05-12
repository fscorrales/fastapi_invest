__all__ = ["safe_get", "safe_list_get"]


# -------------------------------------------------
def safe_get(d, path, default=None):
    for key in path:
        if d is None or not isinstance(d, dict):
            return default
        d = d.get(key)
    return d if d is not None else default


# -------------------------------------------------
def safe_list_get(lst, index, key, default=None):
    if (
        lst
        and isinstance(lst, list)
        and len(lst) > index
        and isinstance(lst[index], dict)
    ):
        return lst[index].get(key, default)
    return default
