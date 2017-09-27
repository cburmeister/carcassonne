import os

MAIL_SERVER = os.environ['MAILCATCHER_PORT_1025_TCP_ADDR']
MAIL_PORT = os.environ['MAILCATCHER_PORT_1025_TCP_PORT']

REDIS_HOST = os.environ['REDIS_PORT_6379_TCP_ADDR']
REDIS_PORT = int(os.environ['REDIS_PORT_6379_TCP_PORT'])

SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(
    'postgres',
    'postgres',
    os.environ['DB_PORT_5432_TCP_ADDR'],
    os.environ['DB_PORT_5432_TCP_PORT'],
    'postgres',
)

SQLALCHEMY_TRACK_MODIFICATIONS = True

SERIALIZER = 'something secret'
