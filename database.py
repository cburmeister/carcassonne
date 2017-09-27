from datetime import datetime
from flask import render_template
from flask_mail import Message
from flask_sqlalchemy import SQLAlchemy
from mail import mail
from sqlalchemy.sql import func
from collections import defaultdict

db = SQLAlchemy()

game_users = db.Table(
    'game_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('game_id', db.Integer, db.ForeignKey('game.id')),
)

game_turns = db.Table(
    'game_turns',
    db.Column('turn_id', db.Integer, db.ForeignKey('turn.id')),
    db.Column('game_id', db.Integer, db.ForeignKey('game.id')),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    email = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(80), unique=True)

    turns = db.relationship('Turn', backref='user', lazy='dynamic')

    def send_email(self, subject, template, *args, **kwargs):
        """Sends the user an email."""
        msg = Message(
            subject,
            sender='noreply@carcassonne.io',
            recipients=[self.email]
        )
        msg.html = render_template(template, *args, **kwargs)
        mail.send(msg)


class Side(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)


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


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    turns = db.relationship(
        'Turn',
        secondary=game_turns,
        order_by='Turn.x_idx, Turn.y_idx',
    )
    users = db.relationship('User', secondary=game_users)

    def board(self):
        """Returns a nested list representating the game board."""
        turns = self.turns  # These should be sorted correctly...

        played_turns = [x for x in turns if x.played]

        # Build a mapping of y-axis indexes to tiles
        turns_by_y_idx = defaultdict(dict)
        for turn in played_turns:
            turns_by_y_idx[turn.y_idx][turn.x_idx] = turn

        class UnplayedTile(object):
            def __init__(self, x_idx, y_idx):
                self.x_idx = x_idx
                self.y_idx = y_idx

        max_height = max([x.y_idx for x in played_turns]) + 1
        min_height = min([x.y_idx for x in played_turns]) - 1
        max_width = max([x.x_idx for x in played_turns]) + 1
        min_width = min([x.x_idx for x in played_turns]) - 1

        wtf = defaultdict(dict)
        for y_idx in range(min_height, max_height + 1):
            for x_idx in range(min_width, max_width + 1):
                wtf[y_idx][x_idx] = turns_by_y_idx[y_idx].get(
                    x_idx, UnplayedTile(x_idx, y_idx)
                )

        rows = []
        for _, turns_by_x_idx in sorted(wtf.items(), reverse=True):
            cols = []
            for _, turn in sorted(turns_by_x_idx.items()):
                cols.append(turn)
            rows.append(cols)

        return rows


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
