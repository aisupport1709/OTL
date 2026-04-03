from app import db
from datetime import datetime


class PLEntry(db.Model):
    __tablename__ = 'pl_entry'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    source_file = db.Column(db.String(255))
    file_type = db.Column(db.String(10))    # '911' or '154'
    month = db.Column(db.Integer)            # 1-12
    year = db.Column(db.Integer)

    account_code = db.Column(db.String(20), index=True)
    account_name = db.Column(db.String(255))

    debit = db.Column(db.Float, default=0)   # Ps Nợ
    credit = db.Column(db.Float, default=0)  # Ps Có

    imported_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PLEntry {self.file_type} {self.month}/{self.year} {self.account_code}>'
