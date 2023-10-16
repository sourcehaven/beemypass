from threading import Thread

from mypass.app import create_app

if __name__ == '__main__':
    app = create_app()
    Thread(target=app.serviceup, daemon=True).start()
    app.main_loop()
