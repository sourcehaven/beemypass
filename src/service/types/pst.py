from typing import Callable

from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.types import TypeDecorator, String

from service import crypto

_SALT_SEP = '-<(|:|)>-'


class StringSaltedEncryptedType(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, type_in: type | TypeEngine, key: str | Callable[[], str] = None, **kwargs):
        super().__init__(**kwargs)
        if type_in is None:
            type_in = String()
        elif isinstance(type_in, type):
            type_in = type_in()
        self.underlying_type = type_in
        self._key = key

    def get_key(self) -> str | None:
        return self._key() if callable(self._key) else self._key

    def process_bind_param(self, value, dialect):
        if value is not None:
            secret, salt = crypto.encryptsecret(value, key=self.get_key())
            composite = _SALT_SEP.join([secret, salt])
            return composite

    def process_result_value(self, value, dialect):
        if value is not None:
            value, salt = value.rsplit(_SALT_SEP, 1)
            secret = crypto.decryptsecret(value, key=self.get_key(), salt=salt)
            return secret
