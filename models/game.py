from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
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
