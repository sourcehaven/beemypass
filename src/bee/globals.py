from contextvars import ContextVar

from werkzeug.local import LocalProxy

_cv_app: ContextVar = ContextVar('mypass.app_ctx')
app_ctx = LocalProxy(  # type: ignore[assignment]
    _cv_app, unbound_message='No toga app configured.'
)
# noinspection PyTypeChecker
current_app = LocalProxy(_cv_app, 'app', unbound_message='No toga app configured.')
