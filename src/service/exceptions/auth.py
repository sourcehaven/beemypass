class AuthException(RuntimeError):
    pass


class WrongPasswordException(AuthException):
    pass


class UserUpdateException(AuthException):
    pass
