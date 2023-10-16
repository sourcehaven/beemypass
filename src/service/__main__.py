import logging
import sys

import waitress
from loguru import logger

from service import create_app

if __name__ == '__main__':
    app = create_app()
    logger.remove()
    host = app.config['HOST']
    port = app.config['PORT']
    if app.debug:
        logger.add(sys.stderr, level=logging.DEBUG)
        app.run(host=host, port=port, debug=app.debug)
    else:
        logger.add(sys.stderr, level=logging.ERROR)
        waitress.serve(app, host=host, port=port, channel_timeout=10, threads=32)
