from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from service.db import utils as db_utils
from service.types.const import IDENTITY_UID

VaultApi = Blueprint('vault', __name__)


@VaultApi.route('/api/db/vault/add', methods=['POST'])
@jwt_required()
def vault_add():
    req = request.json
    fields = req.get('fields', {})
    entry = db_utils.insert_vault_entry(**fields)
    return {'entry': entry}, 200


@VaultApi.route('/api/db/vault/select', methods=['POST'])
@jwt_required()
def vault_select():
    req = request.json
    id = req.get('id')
    ids = req.get('ids')
    crit = req.get('crit', {})
    identity = get_jwt_identity()
    # if either id or ids is given, overwrite crit dictionary
    # as there is no reason to have any criteria if the id is given
    if id is not None:
        crit = {'id': id}
    elif ids is not None:
        crit = {'id': ids}
    crit['user_id'] = identity[IDENTITY_UID]
    crit['active'] = True
    crit['deleted'] = False
    entries = db_utils.select_vault_entry(**crit)
    return entries, 200


@VaultApi.route('/api/db/vault/history', methods=['POST'])
@jwt_required()
def vault_history():
    # TODO: test this method
    req = request.json
    id = req['id']
    crit = {}
    identity = get_jwt_identity()
    crit['id'] = id
    crit['user_id'] = identity[IDENTITY_UID]
    entry = db_utils.get_vault_entry(**crit)
    entries = [entry]
    while entry.parent is not None:
        entry = entry.parent
        entries.append(entry)
    return entries, 200


@VaultApi.route('/api/db/vault/update', methods=['POST'])
@jwt_required()
def vault_update():
    req = request.json
    id = req.get('id')
    ids = req.get('ids')
    crit = req.get('crit', {})
    fields = req.get('fields', {})
    # if either id or ids is given, overwrite crit dictionary
    # as there is no reason to have any criteria if the id is given
    if id is not None:
        crit = {'id': id}
    elif ids is not None:
        crit = {'id': ids}
    fields = {f'new_{k}': fields[k] for k in fields}
    identity = get_jwt_identity()
    crit['user_id'] = identity[IDENTITY_UID]
    crit['active'] = True
    crit['deleted'] = False
    updates = db_utils.update_vault_entry(**crit, **fields)
    return {'affected_rows': updates}, 200


@VaultApi.route('/api/db/vault/delete', methods=['POST'])
@jwt_required()
def vault_delete():
    req = request.json
    id = req.get('id')
    ids = req.get('ids')
    crit = req.get('crit', {})
    # if either id or ids is given, overwrite crit dictionary
    # as there is no reason to have any criteria if the id is given
    if id is not None:
        crit = {'id': id}
    elif ids is not None:
        crit = {'id': ids}
    identity = get_jwt_identity()
    crit['user_id'] = identity[IDENTITY_UID]
    crit['active'] = True
    crit['deleted'] = False
    deletes = db_utils.delete_vault_entry(**crit)
    return {'affected_rows': deletes}, 200
