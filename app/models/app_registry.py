from app import db


class App(db.Model):
    __tablename__ = 'apps'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'description': self.description,
        }
