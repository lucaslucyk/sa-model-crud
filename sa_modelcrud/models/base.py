from typing import Any
from uuid import uuid1, UUID
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column


class ModelBase(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    uid: Mapped[UUID] = mapped_column(index=True, unique=True, default=uuid1)
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
