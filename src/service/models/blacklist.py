from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .base import Model


class TokenBlacklist(Model):
    __tablename__ = 'token_blacklist'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(sa.String(255), unique=True)
    expiration: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True))
    created_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())

    def __repr__(self):
        return str(self)

    def __str__(self):
        return (f'{self.__class__.__name__}('
                f'id={self.id}, '
                f'token={self.token}, '
                f'expiration={self.expiration} '
                f'created_at={self.created_at})')
