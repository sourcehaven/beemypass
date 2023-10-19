"""
MyPass application.
"""
from types import TracebackType

import toga
from loguru import logger

from bee.globals import _cv_app


def serviceup():
    import logging
    import sys
    from service import create_app
    from threading import Thread

    app = create_app()
    logger.remove()
    host = app.config['HOST']
    port = app.config['PORT']

    if app.debug:
        logger.add(sys.stderr, level=logging.DEBUG)

        def loop():
            app.run(host=host, port=port, debug=app.debug, use_reloader=False)
    else:
        import waitress
        logger.add(sys.stderr, level=logging.ERROR)

        def loop():
            waitress.serve(app, host=host, port=port, channel_timeout=10, threads=32)

    Thread(target=loop, name='service_thread', daemon=True).start()


def hide_on_exit(toga_app):
    toga_app.main_window.hide()


class AppContext:
    def __init__(self, app):
        self.app = app
        self._cv_tokens = []

    def push(self) -> None:
        """Binds the app context to the current context."""
        self._cv_tokens.append(_cv_app.set(self))

    def pop(self) -> None:
        _cv_app.reset(self._cv_tokens.pop())

    def __enter__(self) -> 'AppContext':
        self.push()
        return self

    def __exit__(self, exc_type: type | None, exc_value: BaseException | None, tb: TracebackType | None, ) -> None:
        self.pop()


class MyPass(toga.App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        main_box = toga.Box()

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    @staticmethod
    def serviceup():
        return serviceup()

    def app_context(self):
        return AppContext(self)


def create_app():
    app = MyPass()
    app.on_exit = hide_on_exit
    return app
