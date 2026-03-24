import hashlib
import os
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    salt = db.Column(db.String(64), nullable=False)
    display_name = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)

    @staticmethod
    def hash_password(password, salt=None):
        if salt is None:
            salt = os.urandom(16).hex()
        hashed = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
        return hashed, salt

    def set_password(self, password):
        self.password_hash, self.salt = User.hash_password(password)

    def check_password(self, password):
        hashed, _ = User.hash_password(password, self.salt)
        return hashed == self.password_hash
