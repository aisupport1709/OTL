from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config

db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    limiter.init_app(app)

    from app.routes_auth import auth_bp
    from app.routes import main_bp, api_bp
    from app.routes_admin import admin_bp
    from app.routes_apps import apps_bp
    from app.routes_seo import seo_bp, seo_api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(apps_bp)
    app.register_blueprint(seo_bp)
    app.register_blueprint(seo_api_bp)

    with app.app_context():
        migrate_db()
        db.create_all()
        seed_data()

    return app


def migrate_db():
    """Add columns that were added after the initial schema was created.
    Works for both SQLite (local) and PostgreSQL (production).
    """
    from sqlalchemy import text, inspect

    is_postgres = db.engine.dialect.name == 'postgresql'

    with db.engine.connect() as conn:
        if is_postgres:
            stmts = [
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'user'",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS allowed_apps TEXT NOT NULL DEFAULT '[]'",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS active BOOLEAN NOT NULL DEFAULT TRUE",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW()",
                "ALTER TABLE users DROP COLUMN IF EXISTS salt",
            ]
            for stmt in stmts:
                conn.execute(text(stmt))
        else:
            # SQLite: check existing columns via inspector, only add if missing
            inspector = inspect(db.engine)
            try:
                existing = {col['name'] for col in inspector.get_columns('users')}
            except Exception:
                existing = set()

            sqlite_additions = [
                ("role", "ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'"),
                ("allowed_apps", "ALTER TABLE users ADD COLUMN allowed_apps TEXT NOT NULL DEFAULT '[]'"),
                ("active", "ALTER TABLE users ADD COLUMN active BOOLEAN NOT NULL DEFAULT 1"),
                ("created_at", "ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ]
            for col_name, stmt in sqlite_additions:
                if col_name not in existing:
                    conn.execute(text(stmt))

        conn.commit()


def seed_data():
    from app.models.user import User
    from app.models.app_registry import App

    if not User.query.filter_by(username='nguyenanhlinh').first():
        u = User(username='nguyenanhlinh', role='admin', active=True)
        u.set_password('123456@abc')
        u.set_allowed_apps(['otl'])
        db.session.add(u)

    if not App.query.get('otl'):
        db.session.add(App(id='otl', name='OTL App', path='/otl/'))

    if not App.query.get('seo'):
        db.session.add(App(id='seo', name='SEO Scan', path='/seo/'))

    db.session.commit()
