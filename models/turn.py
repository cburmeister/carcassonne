from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Turn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    played = db.Column(db.DateTime)
    tile_id = db.Column(db.Integer, db.ForeignKey('tile.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    x_idx = db.Column(db.Integer)
    y_idx = db.Column(db.Integer)

    def __repr__(self):
        return '<Turn %s, %sx>' % (self.x_idx, self.y_idx)
