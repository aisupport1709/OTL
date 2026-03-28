import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class SharedKey(db.Model):
    __tablename__ = 'shared_keys'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key_hash = db.Column(db.String(256), nullable=False)
    allowed_apps = db.Column(db.Text, nullable=False, default='[]')
    expires_at = db.Column(db.DateTime, nullable=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def check_key(self, raw_key):
        return check_password_hash(self.key_hash, raw_key)

    def is_valid(self):
        if not self.active:
            return False
        if self.expires_at:
            return self.expires_at > datetime.utcnow()
        return True

    def get_allowed_apps(self):
        return json.loads(self.allowed_apps or '[]')

    def set_allowed_apps(self, apps_list):
        self.allowed_apps = json.dumps(apps_list)
