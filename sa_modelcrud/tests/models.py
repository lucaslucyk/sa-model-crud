from sqlalchemy.orm import Mapped, mapped_column
from secrets import token_urlsafe
from ..models import ModelBase, Timestamp


class Sample(Timestamp, ModelBase):
    token: Mapped[str] = mapped_column(default=token_urlsafe)
    describe: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=True, unique=True)