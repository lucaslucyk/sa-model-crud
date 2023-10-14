from uuid import uuid1, UUID
from sqlalchemy.orm import Mapped, mapped_column
from secrets import token_urlsafe
from ..models import ModelBase, Timestamp


class Sample(Timestamp, ModelBase):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    uid: Mapped[UUID] = mapped_column(index=True, unique=True, default=uuid1)
    token: Mapped[str] = mapped_column(default=token_urlsafe)
    describe: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=True, unique=True)