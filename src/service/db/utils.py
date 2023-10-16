from datetime import datetime
from typing import Iterable

import sqlalchemy as sa
from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from service.crypto import checkpw
from service.exceptions import WrongPasswordException
from service.models import User, VaultEntry, TokenBlacklist
from .db import db


def get_user_login(username, password):
    """
    Fetches the user from the db only if username and password is correct.

    Parameters:
        username (str): Username to check against in the db.
        password (str): Password for the username provided.

    Returns:
        (User): The user with the corresponding password if found,
        otherwise None.

    Raises:
        WrongPasswordException: If password does not match username.
    """

    try:
        user = db.session.query(User).filter_by(username=username).one()
        if checkpw(pw=password, salt=user.salt, hashedpw=user.hashedpassword):
            return user
    except (NoResultFound, MultipleResultsFound):
        pass
    raise WrongPasswordException('Could not found user with matching password.')


def is_blacklisted_token(token):
    return db.session.query(TokenBlacklist.token).filter_by(token=token).first() is not None


def revoke_token(jti: str, exp_dt: datetime):
    tbl = TokenBlacklist(token=jti, expiration=exp_dt)
    db.session.add(tbl)
    db.session.commit()
    return tbl


def revoke_tokens(acc_jti: str, ref_jti: str, acc_exp_dt: datetime, ref_exp_dt: datetime):
    acc_tbl = TokenBlacklist(token=acc_jti, expiration=acc_exp_dt)
    ref_tbl = TokenBlacklist(token=ref_jti, expiration=ref_exp_dt)
    db.session.add_all([acc_tbl, ref_tbl])
    db.session.commit()


def insert_user(username: str, password: str, firstname: str = None, lastname: str = None, email: str = None):
    user = User.create(username=username, password=password, firstname=firstname, lastname=lastname, email=email)
    db.session.add(user)
    db.session.commit()
    return user


def update_user_data(id: int, new_firstname: str = ..., new_lastname: str = ..., new_email: str = ...):
    crit = {'id': id}
    fields = User.map_update({'firstname': new_firstname, 'lastname': new_lastname, 'email': new_email})
    db.session.query(User).filter_by(**crit).update(values=fields)
    db.session.commit()


def update_user_pw(id: int, old_password: str, new_password: str):
    crit = {'id': id}
    user = db.session.query(User).filter_by(**crit).one()
    user = user.unlock(old_password)
    user.password = new_password
    db.session.query(User).filter_by(**crit).update(
        values={'_password': user.hashedpassword, '_token': user.encryptedtoken, 'salt': user.salt})
    db.session.commit()
    return user


def insert_vault_entry(
        username: str = None,
        password: str = None,
        title: str = None,
        website: str = None,
        notes: str = None,
        folder: str = None
):
    entry = VaultEntry.create(
        username=username, password=password, title=title, website=website, notes=notes, folder=folder)
    db.session.add(entry)
    db.session.commit()
    return entry


def _vault_query(
        id: int = ...,
        user_id: int = ...,
        username: str = ...,
        title: str = ...,
        website: str = ...,
        notes: str = ...,
        folder: str = ...,
        created_at: datetime | str = ...,
        deleted_at: datetime | str = ...,
        active: bool = ...,
        deleted: bool = ...
):
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)
    if isinstance(deleted_at, str):
        deleted_at = datetime.fromisoformat(deleted_at)
    crit = VaultEntry.map_criterion({
        'user_id': user_id, 'username': username, 'title': title, 'website': website,
        'notes': notes, 'folder': folder, 'created_at': created_at, 'deleted_at': deleted_at,
        'active': active, 'deleted': deleted})
    query = db.session.query(VaultEntry)
    if id is not ...:
        if isinstance(id, Iterable) and not isinstance(id, (bytes, str)):
            expr = VaultEntry.id.in_(set(id))
        else:
            expr = VaultEntry.id == id
        query = query.filter(expr)

    return query.filter_by(**crit)


def get_vault_entry(
        id: int,
        user_id: int = ...,
        username: str = ...,
        title: str = ...,
        website: str = ...,
        notes: str = ...,
        folder: str = ...,
        created_at: datetime | str = ...,
        deleted_at: datetime | str = ...,
        active: bool = ...,
        deleted: bool = ...
):
    return _vault_query(
        id=id, user_id=user_id, username=username, title=title, website=website, notes=notes, folder=folder,
        created_at=created_at, deleted_at=deleted_at, active=active, deleted=deleted).one()


def select_vault_entry(
        id: int | Iterable[int] = ...,
        user_id: int = ...,
        username: str = ...,
        title: str = ...,
        website: str = ...,
        notes: str = ...,
        folder: str = ...,
        created_at: datetime | str = ...,
        deleted_at: datetime | str = ...,
        active: bool = ...,
        deleted: bool = ...
):
    return _vault_query(
        id=id, user_id=user_id, username=username, title=title, website=website, notes=notes, folder=folder,
        created_at=created_at, deleted_at=deleted_at, active=active, deleted=deleted).all()


def unlock_vault_entry(entry: VaultEntry | list[VaultEntry], enckey: str):
    try:
        for e in entry:
            e.encryptionkey = enckey
    except TypeError:
        entry.encryptionkey = enckey
    return entry


def update_vault_entry(
        id: int | Iterable[int] = ...,
        user_id: int = ...,
        username: str = ...,
        title: str = ...,
        website: str = ...,
        notes: str = ...,
        folder: str = ...,
        active: bool = ...,
        deleted: bool = ...,
        created_at: datetime | str = ...,
        deleted_at: datetime | str = ...,
        new_username: str = ...,
        new_title: str = ...,
        new_website: str = ...,
        new_notes: str = ...,
        new_folder: str = ...,
):
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)
    if isinstance(deleted_at, str):
        deleted_at = datetime.fromisoformat(deleted_at)
    crit = VaultEntry.map_criterion({
        'user_id': user_id, 'username': username, 'title': title, 'website': website,
        'notes': notes, 'folder': folder, 'created_at': created_at, 'deleted_at': deleted_at,
        'active': active, 'deleted': deleted})
    fields = VaultEntry.map_update({
        'username': new_username, 'title': new_title, 'website': new_website,
        'notes': new_notes, 'folder': new_folder})

    if len(fields) == 0:
        return 0

    query = db.session.query(VaultEntry)
    if id is not ...:
        if isinstance(id, Iterable) and not isinstance(id, (bytes, str)):
            expr = VaultEntry.id.in_(set(id))
        else:
            expr = VaultEntry.id == id
        query = query.filter(expr)

    entries = query.filter_by(**crit).all()
    new_entries = [VaultEntry.copy(entry) for entry in entries]
    db.session.add_all(new_entries)
    # we need to get the ids of newly added items
    db.session.flush()
    affected_rows = 0
    for entry, new_entry in zip(entries, new_entries):
        affected_rows += db.session.query(VaultEntry).filter_by(id=entry.id).update(
            values={'active': False})
        affected_rows += db.session.query(VaultEntry).filter_by(id=new_entry.id).update(
            values={'parent_id': entry.id, **fields})

    db.session.commit()
    return affected_rows


def delete_vault_entry(
        id: int | Iterable[int] = ...,
        user_id: int = ...,
        username: str = ...,
        title: str = ...,
        website: str = ...,
        notes: str = ...,
        folder: str = ...,
        created_at: datetime | str = ...,
        active: bool = ...,
        deleted: bool = ...
):
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)
    crit = VaultEntry.map_criterion({
        'user_id': user_id, 'username': username, 'title': title, 'website': website,
        'notes': notes, 'folder': folder, 'created_at': created_at, 'active': active, 'deleted': deleted})

    query = db.session.query(VaultEntry)
    if id is not ...:
        if isinstance(id, Iterable) and not isinstance(id, (bytes, str)):
            expr = VaultEntry.id.in_(set(id))
        else:
            expr = VaultEntry.id == id
        query = query.filter(expr)

    affected_rows = query.filter_by(**crit).update(
        values={'deleted': True, 'active': False, 'deleted_at': sa.func.now()})
    db.session.commit()
    return affected_rows
