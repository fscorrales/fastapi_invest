__all__ = [
    "safe_get_dict",
    "safe_list_get_dict",
    "safe_json_df",
    "sanitize_dataframe_for_json",
]

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
    # return df.replace([np.inf, -np.inf], pd.NA).where(pd.notnull(df), None)


# -------------------------------------------------
def sanitize_dataframe_for_json(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia un DataFrame para que sea seguro convertirlo a JSON o subirlo a Google Sheets.

    Reemplaza:
    - np.nan, np.inf, -np.inf con None
    - np.* types con sus equivalentes nativos
    """
    with pd.option_context("future.no_silent_downcasting", True):
        # Reemplazar NaN e infinitos por None
        # df_clean = df.replace([np.nan, np.inf, -np.inf], None)
        df_clean = df.replace([np.nan, np.inf, -np.inf, None], "").infer_objects(
            copy=False
        )
        df_clean = df_clean.astype(object).where(pd.notnull(df_clean), None)
        # df_clean = df_clean.astype(object)

        # Convertir a object donde haya valores nulos para asegurar compatibilidad

        # Convertir np.* types (como np.int64, np.float64) a sus tipos nativos
        df_clean = df_clean.apply(
            lambda col: col.map(lambda x: x.item() if hasattr(x, "item") else x)
        )
        # df_clean = df_clean.applymap(lambda x: x.item() if hasattr(x, "item") else x)

        # Convertir todo a string para evitar problemas con tipos
        # df_clean = df_clean.astype(str)

        return df_clean
