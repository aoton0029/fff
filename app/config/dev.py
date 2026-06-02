from .base import Config


class DevelopmentConfig(Config):
	DEBUG: bool = True
	SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
	SQLALCHEMY_BINDS = {'master_db': 'sqlite:///app.db'}
