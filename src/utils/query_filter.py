__all__ = ["BaseFilterParams"]

from bson import ObjectId
from pydantic import BaseModel, Field, PrivateAttr
from typing import Literal, Optional


op_map = {
    ">=": "$gte",
    "<=": "$lte",
    "!=": "$ne",
    ">": "$gt",
    "<": "$lt",
    "=": "$eq",
    "~": "$regex",
}

# -------------------------------------------------
def data_filter(
    filter_params: str,
    get_deleted: Optional[bool] = None,
    extra_filter: Optional[dict] = None,
):
    filter_dict = {}
    filter_item_list = filter_params.split(",")

    for filter_item in filter_item_list:
        filter_dict.update(get_filter_query(filter_item))

    if get_deleted:
        filter_dict.update(
            deactivated_at={"$ne": None} if get_deleted else {"$eq": None}
        )

    if extra_filter:
        filter_dict.update(extra_filter)

    return filter_dict

# -------------------------------------------------
def get_filter_query(f):
    op = ""
    for o in op_map:
        if o in f:
            op = o
            break
    if not op:
        return {}

    k, v = f.split(op)
    return {k.strip(): {op_map[op]: format_value(v)}}

# -------------------------------------------------
def format_value(v):
    return (
        int(v)
        if v.strip().isdigit()
        else (
            float(v)
            if v.strip().isdecimal()
            else ObjectId(v.strip()) if len(v.strip()) == 24 else v.strip()
        )
    )

# -------------------------------------------------
class BaseFilterParams(BaseModel):
    query_filter: str = ""
    limit: int = Field(20, gt=0, le=100)
    offset: int = Field(0, ge=0)
    sort_by: str = "_id"
    sort_dir: Literal["asc", "desc"] = "asc"

    # Campo interno, no forma parte de la query
    _extra_filter: Optional[dict] = PrivateAttr(default=None)

    def set_extra_filter(self, extra: Optional[dict]):
        self._extra_filter = extra

    def get_full_filter(self):
        return data_filter(self.query_filter, extra_filter=self._extra_filter)