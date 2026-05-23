import os
from .base import Config
from .dev import DevelopmentConfig
from .prd import ProductionConfig

_config_map: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}


def get_config() -> type[Config]:
    env = os.environ.get("FLASK_ENV", "development").lower()
    return _config_map.get(env, DevelopmentConfig)
