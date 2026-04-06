from app import db
from datetime import datetime


class PLSDCK(db.Model):
    """
    SDCK (Số dư cuối kỳ) - Ending balance of account
    For tracking opening/closing balances of specific accounts (e.g., 1541)
    """
    __tablename__ = 'pl_sdck'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    source_file = db.Column(db.String(255))
    account_target = db.Column(db.String(10))  # e.g., '1541' (the target account)
    month = db.Column(db.Integer)              # 1-12
    year = db.Column(db.Integer)

    account_code = db.Column(db.String(20), index=True)  # Sub-account code
    account_name = db.Column(db.String(255))

    balance = db.Column(db.Float, default=0)   # Ending balance (Ps Nợ, converted to negative if needed)

    imported_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PLSDCK {self.account_target} {self.month}/{self.year} {self.account_code}: {self.balance}>'
