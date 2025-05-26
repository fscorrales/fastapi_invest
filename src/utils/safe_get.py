__all__ = ["safe_get_dict", "safe_list_get_dict", "safe_json_df"]

import numpy as np
import pandas as pd


# -------------------------------------------------
def safe_get_dict(d, path, default=None):
    for key in path:
        if d is None or not isinstance(d, dict):
            return default
        d = d.get(key)
    return d if d is not None else default


# -------------------------------------------------
def safe_list_get_dict(lst, index, key, default=None):
    if (
        lst
        and isinstance(lst, list)
        and len(lst) > index
        and isinstance(lst[index], dict)
    ):
        return lst[index].get(key, default)
    return default


# -------------------------------------------------
def safe_json_df(df: pd.DataFrame):
    return df.replace({np.nan: None, np.inf: None, -np.inf: None})
