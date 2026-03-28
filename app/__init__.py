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

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(apps_bp)

    with app.app_context():
        db.create_all()
        seed_data()

    return app


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

    db.session.commit()
