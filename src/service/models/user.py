from datetime import datetime
from typing import Optional, Mapping

import sqlalchemy as sa
import sqlalchemy_utils as sau
from sqlalchemy.orm import Mapped, mapped_column, relationship

from service import crypto
from service.functional import querymap
from .base import Model
from .entry import VaultEntry, Tag


class User(Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(255), unique=True)
    firstname: Mapped[Optional[str]] = mapped_column(sa.Unicode(255))
    lastname: Mapped[Optional[str]] = mapped_column(sa.Unicode(255))
    email: Mapped[Optional[str]] = mapped_column(sau.EmailType(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    salt: Mapped[str] = mapped_column(sa.String(255))

    _password: Mapped[str] = mapped_column(sa.String(255), name='password')
    _token: Mapped[str] = mapped_column(sa.String(255), name='token')

    vault_entries: Mapped[list[VaultEntry]] = relationship(cascade='all, delete-orphan')
    tags: Mapped[list[Tag]] = relationship(cascade='all, delete-orphan')

    # noinspection PyShadowingBuiltins
    def __init__(
            self,
            id=None,
            *,
            username=None,
            password=None,
            secretpw=None,
            token=None,
            salt=None,
            firstname=None,
            lastname=None,
            email=None,
            create_time=None,
            stfu=False
    ):
        """
        Model class representing an application user.

        Parameters:
            id (int | None): primary key (not passed directly)
            username (str): the username
            password (str): master password which will be hashed
            token (str): one time given, secret token
            salt (str): salt used for password hashing and token encryption
            firstname (str | None): forename
            lastname (str | None): family name
            email (str | None): email address of the user
            create_time (datetime | None): registration time
            stfu (bool): silence error messages explicitly
        """

        if not stfu:
            raise TypeError('You dont know what you are doing! Use create classmethod instead.')

        # noinspection PyTypeChecker
        self.id = id
        # noinspection PyTypeChecker
        self.username = username
        # noinspection PyTypeChecker
        self._password = password
        # noinspection PyTypeChecker
        self._token = token
        # noinspection PyTypeChecker
        self.salt = salt
        # noinspection PyTypeChecker
        self.firstname = firstname
        # noinspection PyTypeChecker
        self.lastname = lastname
        # noinspection PyTypeChecker
        self.email = email
        # noinspection PyTypeChecker
        self.created_at = create_time
        self._secretpw = secretpw

    @classmethod
    def create(cls, *, username=None, password=None, firstname=None, lastname=None, email=None):
        """
        Model class representing an application user.

        Parameters:
            username (str | None): the username
            password (str | None): master password which will be hashed
            firstname (str | None): forename
            lastname (str | None): family name
            email (str | None): email address of the user
        """

        salt = None
        secret_token = None
        hashed_pw = None
        if password is not None:
            salt = crypto.gensalt()
            token = crypto.initpw(256)
            secret_token = crypto.encryptsecret(token, pw=password, salt=salt)
            hashed_pw = crypto.hashpw(password, salt)
        return cls(
            username=username, password=hashed_pw, secretpw=password, token=secret_token, salt=salt,
            firstname=firstname, lastname=lastname, email=email, stfu=True)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return (f'{self.__class__.__name__}(id={self.id}, '
                f'username={self.username}, '
                f'firstname={self.firstname}, '
                f'lastname={self.lastname}, '
                f'email={self.email}')

    def unlock(self, pw):
        """
        Unlocks a queried object.

        Parameters:
            pw (str): the password for unlocking the object

        Returns:
            (User): the unlocked user object
        """

        return User(
            id=self.id, username=self.username, password=self._password, secretpw=pw, token=self._token,
            salt=self.salt, firstname=self.firstname, lastname=self.lastname, email=self.email,
            create_time=self.created_at, stfu=True)

    @property
    def token(self):
        if not hasattr(self, '_secretpw') or self._secretpw is None:
            raise RuntimeError(f'{self.__class__.__name__} object at {id(self)} is not unlocked.')
        return crypto.decryptsecret(self._token, pw=self._secretpw, salt=self.salt)

    @token.setter
    def token(self, __value):
        """
        Parameters:
            __value (str): the value that will be salted and encrypted to create the secret token
        """

        if not hasattr(self, '_secretpw') or self._secretpw is None:
            raise RuntimeError(
                f'{self.__class__.__name__} object at {id(self)} does not have an encryption key.\n'
                f'Set the object\'s password attribute')
        self._token: str = crypto.encryptsecret(__value, pw=self._secretpw, salt=self.salt)

    @property
    def password(self):
        if not hasattr(self, '_secretpw') or self._secretpw is None:
            raise RuntimeError(f'{self.__class__.__name__} object at {id(self)} is not unlocked.')
        return self._secretpw

    @password.setter
    def password(self, __value):
        """
        Parameters:
            __value (str): the value that will be salted and hashed to create a password
        """

        salt = crypto.gensalt()
        token = self.token
        self._secretpw = __value
        self._password: str = crypto.hashpw(__value, salt)
        self.salt = salt
        self.token = token

    @property
    def hashedpassword(self):
        return self._password

    @property
    def encryptedtoken(self):
        return self._token

    _update_whitelist = {'firstname', 'lastname', 'email'}

    @staticmethod
    def map_update(fields: Mapping):
        q = querymap(fields)
        q = {key: q[key] for key in q if key in User._update_whitelist}
        return q
