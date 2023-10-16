from datetime import datetime

from flask import Blueprint, make_response, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token, get_jwt, \
    decode_token

from service.db import utils as db_utils
from .com import IDENTITY_UID, IDENTITY_PW, IDENTITY_TOK

UserApi = Blueprint('user', __name__)


@UserApi.route('/api/user/update', methods=['POST'])
@jwt_required(fresh=True)
def user_update():
    req = request.json
    fields = req.get('fields', {})
    identity = get_jwt_identity()
    fields = {f'new_{k}': fields[k] for k in fields}
    db_utils.update_user_data(id=identity[IDENTITY_UID], **fields)
    resp = make_response('', 204)
    if 'new_email' in fields:
        resp.set_cookie('email', fields['new_email'])
    if 'new_firstname' in fields:
        resp.set_cookie('firstname', fields['new_firstname'])
    if 'new_lastname' in fields:
        resp.set_cookie('lastname', fields['new_lastname'])
    return resp


@UserApi.route('/api/user/update/pw', methods=['POST'])
@jwt_required()
def user_updatepw():
    req = request.json
    identity = get_jwt_identity()
    acc_jwt = get_jwt()
    acc_jti = acc_jwt['jti']
    acc_exp_dt = datetime.fromtimestamp(acc_jwt['exp'])
    ref_jwt = decode_token(req.pop('refresh_token'))
    ref_jti = ref_jwt['jti']
    ref_exp_dt = datetime.fromtimestamp(ref_jwt['exp'])
    user = db_utils.update_user_pw(id=identity[IDENTITY_UID], **req)
    # token blacklisting
    db_utils.revoke_tokens(acc_jti=acc_jti, ref_jti=ref_jti, acc_exp_dt=acc_exp_dt, ref_exp_dt=ref_exp_dt)
    identity[IDENTITY_PW] = user.password
    identity[IDENTITY_TOK] = user.token
    access_token = create_access_token(identity=identity, fresh=True)
    refresh_token = create_refresh_token(identity=identity)
    tokens = {'access_token': access_token, 'refresh_token': refresh_token}
    return tokens, 201
