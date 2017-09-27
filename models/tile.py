from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()


class Tile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(120))
    side_1 = db.Column(db.Integer, nullable=False)
    side_2 = db.Column(db.Integer, nullable=False)
    side_3 = db.Column(db.Integer, nullable=False)
    side_4 = db.Column(db.Integer, nullable=False)
    special = db.Column(db.Boolean, default=False)

    turns = db.relationship('Turn', backref='tile', lazy='dynamic')

    @classmethod
    def get_random(cls, exclude_ids=[]):
        """Return a random tile row not in the excluded ids."""
        return cls.query\
            .filter(~cls.id.in_(exclude_ids))\
            .order_by(func.random())\
            .first()
