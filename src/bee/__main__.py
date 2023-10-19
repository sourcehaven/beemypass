import pystray
from PIL import Image

from service.app import create_app, serviceup


def on_open(icon, query):
    app.main_window.show()


def on_exit(icon, query):
    # noinspection PyProtectedMember
    app._impl.exit()
    icon.stop()


if __name__ == '__main__':
    app = create_app()
    menu = pystray.Menu(pystray.MenuItem('Open', on_open), pystray.MenuItem('Exit', on_exit))
    with Image.open(app.paths.app / 'resources' / 'mypass.ico') as image:
        icon = pystray.Icon('mypass', image, "MyPass", menu=menu)
    with app.app_context():
        serviceup()
    icon.run_detached()
    app.main_loop()
