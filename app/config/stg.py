import os
import urllib.parse
from .base import Config


def _build_mssql_uri(trust_cert: str) -> str:
	server = os.getenv('DB_SERVER', '')
	database = os.getenv('DB_NAME', '')
	username = os.getenv('DB_USERNAME', '')
	password = urllib.parse.quote_plus(os.getenv('DB_PASSWORD', ''))
	driver = urllib.parse.quote_plus('ODBC Driver 18 for SQL Server')
	return (
		f'mssql+pyodbc://{username}:{password}@{server}/{database}'
		f'?driver={driver}&Encrypt=yes&TrustServerCertificate=yes'
	)


def _build_master_mssql_uri(trust_cert: str) -> str:
	server = os.getenv('MASTER_DB_SERVER', '')
	database = os.getenv('MASTER_DB_NAME', '')
	username = os.getenv('MASTER_DB_USERNAME', '')
	password = urllib.parse.quote_plus(os.getenv('MASTER_DB_PASSWORD', ''))
	driver = urllib.parse.quote_plus('ODBC Driver 18 for SQL Server')
	return (
		f'mssql+pyodbc://{username}:{password}@{server}/{database}'
		f'?driver={driver}&Encrypt=yes&TrustServerCertificate={trust_cert}'
	)


class StagingConfig(Config):
	DEBUG: bool = True
	SQLALCHEMY_DATABASE_URI = _build_mssql_uri(trust_cert='yes')
	SQLALCHEMY_BINDS = {'master_db': _build_master_mssql_uri(trust_cert='yes')}
	SQLALCHEMY_ENGINE_OPTIONS = {
		'pool_pre_ping': True,
		'pool_recycle': 1800,
		'connect_args': {'fast_executemany': True},
	}
	MASTER_DB_READONLY: bool = True
