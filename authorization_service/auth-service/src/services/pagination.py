from enum import Enum

from fastapi.param_functions import Query
from pydantic import BaseModel


class SortEnum(Enum):
    ASC = 'asc'
    DESC = 'desc'


class Pagination(BaseModel):
    per_page: int
    page: int
    order: SortEnum

    def get_offset(self):
        if self.page == 1:
            offset = self.page - 1
        else:
            offset = (self.page - 1) * self.per_page

        return offset


def pagination_params(
        page: int = Query(ge=1, required=False, default=1, le=100),
        per_page: int = Query(ge=1, le=100, required=False, default=50),
        order: SortEnum = SortEnum.DESC):
    return Pagination(per_page=per_page, page=page, order=order.value)
