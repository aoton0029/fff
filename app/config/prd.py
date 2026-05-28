from .base import Config

class ProductionConfig(Config):
	DEBUG: bool = False