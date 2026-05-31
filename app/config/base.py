import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
	DEBUG: bool = False
	TESTING: bool = False
	SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
	SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
	PERMISSION_SESSION_LIFETIME: timedelta = timedelta(hours=1)


class TestingConfig(Config):
	TESTING: bool = True
	DEBUG: bool = True
	SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
	WTF_CSRF_ENABLED = False
	SECRET_KEY = 'test-secret'
