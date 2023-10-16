"""
BeeMyPass application.
"""
import toga
from loguru import logger


class MyPass(toga.App):
    def serviceup(self):
        import logging
        import sys
        from service import create_app

        app = create_app()
        logger.remove()
        host = app.config['HOST']
        port = app.config['PORT']
        if app.debug:
            logger.add(sys.stderr, level=logging.DEBUG)
            app.run(host=host, port=port, debug=app.debug, use_reloader=False)
        else:
            import waitress
            logger.add(sys.stderr, level=logging.ERROR)
            waitress.serve(app, host=host, port=port, channel_timeout=10, threads=32)

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


def create_app():
    app = MyPass()
    return app
