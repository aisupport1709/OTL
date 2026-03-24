from app import db


class AppSetting(db.Model):
    __tablename__ = 'app_settings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String(500), nullable=False)

    @staticmethod
    def get(key, default=None):
        setting = AppSetting.query.filter_by(key=key).first()
        return setting.value if setting else default

    @staticmethod
    def set(key, value):
        setting = AppSetting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = AppSetting(key=key, value=value)
            db.session.add(setting)
        db.session.commit()
        return setting
