import os
from flask import Flask
from .extensions import db, login_manager, htmx, csrf
from .config.dev import DevelopmentConfig
from .config.prd import ProductionConfig

config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_map.get(config_name, DevelopmentConfig))

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    htmx.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'ログインが必要です。'
    login_manager.login_message_category = 'warning'

    # Register blueprints
    from .views.auth import auth_bp
    from .views.salary import salary_bp
    from .views.allocation import allocation_bp
    from .views.labor import labor_bp
    from .views.maintenance import maintenance_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(salary_bp, url_prefix='/salary')
    app.register_blueprint(allocation_bp, url_prefix='/allocation')
    app.register_blueprint(labor_bp, url_prefix='/labor')
    app.register_blueprint(maintenance_bp, url_prefix='/maintenance')

    # Create tables
    with app.app_context():
        db.create_all()

    from .utils.logger import setup_logging
    setup_logging(app)

    return app
