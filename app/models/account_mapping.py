from app import db
from datetime import datetime


class AccountMapping(db.Model):
    """
    Account Code Mapping - Maps local account codes to HQ account codes
    """
    __tablename__ = 'account_mappings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    local_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    hq_code = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AccountMapping {self.local_code} -> {self.hq_code}>'
