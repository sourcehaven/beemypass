from flask_sqlalchemy import SQLAlchemy

from service.models import User, VaultEntry


def init_db(db: SQLAlchemy):
    user1 = User.create(username='master', password='super-secret', firstname='John', lastname='Doe')
    user1.token = 'blaahnUurrREenktExbF7Q'
    user2 = User.create(username='god', password='pls-dont-look', firstname='Lucky', lastname='Luke')
    user2.token = '6yW8hoD24w76ET9IWZUF_Q'
    db.session.add_all([user1, user2])

    db.session.add_all([
        VaultEntry.create(
            user_id=1, username='John', password='Has$MeifYouCAN555', title='pwstore',
            website='https://mypwstore.com', notes='Some notes here ...', folder='vaults',
            encryptionkey='blaahnUurrREenktExbF7Q'),
        VaultEntry.create(
            user_id=1, username='Doe', password='516dsawdJSWłđ', title='fakebook',
            website='https://fakebook.com', notes=':)', folder='social',
            encryptionkey='blaahnUurrREenktExbF7Q'),
        VaultEntry.create(
            user_id=1, username='Missimp', password='54d6waŁđäĐw5', title='slype',
            website='https://slype.com', notes=':)', folder='social',
            encryptionkey='blaahnUurrREenktExbF7Q'),
    ])

    db.session.commit()
