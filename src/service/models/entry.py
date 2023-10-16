from datetime import datetime
from typing import Optional, Mapping

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from service import crypto
from service.db import db
from service.functional import querymap
from .base import Model

VaultTag = db.Table(
    'vault_tag',
    db.Column('vault_id', db.ForeignKey('vault.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True),
    db.Column('tag_id', db.ForeignKey('tag.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True),
)


class VaultEntry(Model):
    __tablename__ = 'vault'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey('user.id', ondelete='CASCADE'))
    parent_id: Mapped[Optional[int]] = mapped_column(sa.ForeignKey('vault.id', ondelete='CASCADE'))
    username: Mapped[str] = mapped_column(sa.String(255))
    salt: Mapped[str] = mapped_column(sa.String(255))
    title: Mapped[Optional[str]] = mapped_column(sa.String(255))
    website: Mapped[Optional[str]] = mapped_column(sa.String(255))
    notes: Mapped[Optional[str]] = mapped_column(sa.String(2048))
    folder: Mapped[Optional[str]] = mapped_column(sa.String(255))
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True))
    active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    deleted: Mapped[bool] = mapped_column(sa.Boolean, default=False)

    _password: Mapped[str] = mapped_column(sa.String(255), name='password')

    parent: Mapped[Optional['VaultEntry']] = relationship(
        remote_side='VaultEntry.id', single_parent=True, cascade='all, delete-orphan')
    tags: Mapped[list['Tag']] = relationship(secondary='vault_tag', back_populates='entries')

    # noinspection PyShadowingBuiltins
    def __init__(
            self,
            id=None,
            *,
            user_id=None,
            username=None,
            password=None,
            salt=None,
            title=None,
            website=None,
            notes=None,
            folder=None,
            active=None,
            deleted=None,
            created_at=None,
            deleted_at=None,
            stfu=False,
            _encryptionkey=None,
    ):
        """
        Model class representing a vault entry.

        Parameters:
            id (int | None):
            user_id (int | None):
            username (str | None):
            password (str | None):
            salt (str | None):
            title (str | None):
            website (str | None):
            notes (str | None):
            folder (str | None):
            active (bool | None):
            deleted (bool | None):
            created_at (datetime | None):
            deleted_at (datetime | None):
            stfu (bool):
            _encryptionkey (str | None):

        Raises:
            TypeError: if called without setting the stfu=True parameter
        """

        if not stfu:
            raise TypeError('You dont know what you are doing! Use create classmethod instead.')

        if active is None:
            active = True
        if deleted is None:
            deleted = False

        # noinspection PyTypeChecker
        self.id = id
        # noinspection PyTypeChecker
        self.user_id = user_id
        # noinspection PyTypeChecker
        self.username = username
        # noinspection PyTypeChecker
        self._password = password
        # noinspection PyTypeChecker
        self.salt = salt
        # noinspection PyTypeChecker
        self.title = title
        # noinspection PyTypeChecker
        self.website = website
        # noinspection PyTypeChecker
        self.notes = notes
        # noinspection PyTypeChecker
        self.folder = folder
        # noinspection PyTypeChecker
        self.active = active
        # noinspection PyTypeChecker
        self.deleted = deleted
        # noinspection PyTypeChecker
        self.created_at = created_at
        # noinspection PyTypeChecker
        self.deleted_at = deleted_at
        self._encryptionkey = _encryptionkey

    @classmethod
    def create(
            cls,
            id=None,
            *,
            user_id=None,
            username=None,
            password=None,
            title=None,
            website=None,
            notes=None,
            folder=None,
            encryptionkey=None,
    ):
        """
        Use this for the creation of a vault entry model.

        Parameters:
            id (int):
            user_id (int):
            username (str):
            password (str):
            title (str):
            website (str):
            notes (str):
            folder (str):
            encryptionkey (str):
        """

        if user_id is None or encryptionkey is None:
            from flask_jwt_extended import get_jwt_identity
            from service.api.com import IDENTITY_UID, IDENTITY_TOK
            identity = get_jwt_identity()
            if user_id is None:
                try:
                    user_id = identity[IDENTITY_UID]
                except RuntimeError:
                    pass
            if encryptionkey is None:
                try:
                    encryptionkey = identity[IDENTITY_TOK]
                except RuntimeError:
                    pass

        obj = cls(
            id=id, user_id=user_id, username=username, password=None, salt=None, title=title, website=website,
            notes=notes, folder=folder, _encryptionkey=encryptionkey, stfu=True)
        obj.salt = crypto.gensalt()
        obj.password = password
        return obj

    @classmethod
    def copy(cls, obj):
        """
        Copies a vault entry without id.

        Parameters:
            obj (VaultEntry):
        """
        kwargs = {
            'user_id': obj.user_id,
            'username': obj.username,
            'password': obj._password,
            'salt': obj.salt,
            'title': obj.title,
            'website': obj.website,
            'notes': obj.notes,
            'folder': obj.folder,
            'active': obj.active,
            'deleted': obj.deleted,
            'stfu': True,
        }
        if hasattr(obj, '_encryptionkey'):
            kwargs['_encryptionkey'] = obj._encryptionkey

        return VaultEntry(**kwargs)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return (f'{self.__class__.__name__}(id={self.id}, '
                f'user_id={self.user_id}, '
                f'username={self.username}, '
                f'title={self.title}, '
                f'website={self.website}), '
                f'folder={self.folder}, '
                f'active={self.active}')

    @property
    def password(self):
        if not hasattr(self, '_encryptionkey') or self._encryptionkey is None:
            raise RuntimeError(
                f'{self.__class__.__name__} object at {id(self)} does not have an encryption key.\n'
                f'Set the object\'s password attribute')
        return crypto.decryptsecret(self._password, pw=self._encryptionkey, salt=self.salt)

    @password.setter
    def password(self, __value):
        """
        Parameters:
            __value (str): the value that will be salted and hashed to create a password
        """

        if not hasattr(self, '_encryptionkey') or self._encryptionkey is None:
            raise RuntimeError(f'{self.__class__.__name__} object at {id(self)} is not unlocked.')
        self._password: str = crypto.encryptsecret(__value, pw=self._encryptionkey, salt=self.salt)

    @property
    def encryptedpassword(self):
        return self._password

    @property
    def encryptionkey(self):
        if hasattr(self, '_encryptionkey'):
            return self._encryptionkey
        return None

    @encryptionkey.setter
    def encryptionkey(self, __value):
        """

        Parameters:
            __value (str): sets the secret key for password encryption (usually user token)
        """

        self._encryptionkey = __value

    _crit_whitelist = {
        'id', 'user_id', 'username', 'title', 'website', 'notes', 'folder', 'create_time', 'active', 'deleted'}

    _update_whitelist = {
        'username', 'password', 'title', 'website', 'notes', 'folder'}

    @staticmethod
    def map_criterion(crit: Mapping):
        q = querymap(crit)
        q = {key: q[key] for key in q if key in VaultEntry._crit_whitelist}
        return q

    @staticmethod
    def map_update(fields: Mapping):
        q = querymap(fields)
        q = {key: q[key] for key in q if key in VaultEntry._update_whitelist}
        return q


class Tag(Model):
    __tablename__ = 'tag'
    __table_args__ = sa.UniqueConstraint('name', 'user_id'), {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey('user.id', ondelete='CASCADE'))

    name: Mapped[int] = mapped_column(sa.String(255))
    description: Mapped[Optional[str]] = mapped_column(sa.String(255))
    create_time: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())

    entries: Mapped[Optional[list['VaultEntry']]] = relationship(
        secondary='vault_tag', back_populates='tags', lazy='joined', innerjoin=True)

    def __repr__(self):
        return (f'{self.__class__.__name__}(id={self.id}, '
                f'user_id={self.user_id}'
                f'name={self.name}, '
                f'description={self.description}, '
                f'create_time={self.create_time})')
