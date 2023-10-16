from service.db.utils import is_blacklisted_token


# noinspection PyUnusedLocal
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return is_blacklisted_token(jti)
