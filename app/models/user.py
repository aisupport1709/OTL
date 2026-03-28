import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(200))
    role = db.Column(db.String(20), nullable=False, default='user')
    allowed_apps = db.Column(db.Text, nullable=False, default='[]')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_allowed_apps(self):
        return json.loads(self.allowed_apps or '[]')

    def set_allowed_apps(self, apps_list):
        self.allowed_apps = json.dumps(apps_list)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'allowed_apps': self.allowed_apps,
            'active': self.active,
        }
