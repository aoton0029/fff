import os
from flask import Flask, render_template
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
    from .views import main_bp
    from .views import main
    from .views import salary
    from .views import allocation
    from .views import labor
    from .views import maintenance
    from .views import ouen
    from .api import salary
    from .api import allocation
    from .api import labor
    from .api import maintenance
    from .api import ouen
    from .views.auth import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # Error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('errors/500.html'), 500

    # Create tables + SQLite migration
    with app.app_context():
        db.create_all()
        # Add year_month column to upload_batches if it doesn't exist yet (SQLite has no IF NOT EXISTS for ADD COLUMN)
        with db.engine.connect() as conn:
            try:
                conn.execute(db.text("ALTER TABLE upload_batches ADD COLUMN year_month VARCHAR(7)"))
                conn.commit()
            except Exception:
                pass  # Column already exists

    # Context processor: inject current processing year_month into all templates
    @app.context_processor
    def inject_processing_month():
        try:
            from .models.processing_month import ProcessingMonth
            setting = ProcessingMonth.query.first()
            return {'current_year_month': setting.year_month if setting else None}
        except Exception:
            return {'current_year_month': None}

    from .utils.logger import setup_logging
    setup_logging(app)

    return app
