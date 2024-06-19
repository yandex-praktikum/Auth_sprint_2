from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class UUIDMixin(BaseModel):
    uuid: UUID = Field(primary_key=True, default_factory=uuid4, alias='id')
