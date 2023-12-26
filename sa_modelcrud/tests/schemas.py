from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class SampleBase(BaseModel):
    id: Optional[UUID] = None
    token: Optional[str] = None
    describe: Optional[str] = None
    email: Optional[str] = None


class SampleCreate(SampleBase):
    ...


class SampleUpdate(SampleBase):
    ...


class SampleInDB(SampleBase):

    class Config:
        from_attributes: True


class Sample(SampleInDB):
    ...
