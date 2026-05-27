import logging
import os
from flask import Flask
from .config import get_config
from .extensions import db, login_manager, csrf
from .errors import register_error_handlers


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config())
    app.config["UPLOAD_FOLDER"] = os.path.join(app.instance_path, "uploads")

    _configure_logging(app)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        from . import models  # noqa: F401 — ensure models are registered before create_all
        db.create_all()
        from .seeds import seed_db
        seed_db()
        from .excel_imports.service import load_domain_config
        load_domain_config(app)

    _register_blueprints(app)
    register_error_handlers(app)
    _register_context_processors(app)

    return app


def _configure_logging(app: Flask) -> None:
    level = logging.DEBUG if app.config.get("DEBUG") else logging.INFO
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(level)


def _register_context_processors(app: Flask) -> None:
    from .excel_imports.service import get_domain_config

    @app.context_processor
    def inject_excel_domains():
        return {"excel_domain_config": get_domain_config()}


def _register_blueprints(app: Flask) -> None:
    from .auth import auth_bp
    from .home import main_bp
    from .files import files_bp, files_api_bp
    from .excel_imports import excel_imports_bp, excel_imports_api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(files_bp, url_prefix="/files")
    app.register_blueprint(files_api_bp, url_prefix="/api/files")
    app.register_blueprint(excel_imports_bp, url_prefix="/excel-imports")
    app.register_blueprint(excel_imports_api_bp, url_prefix="/api/excel-imports")
