from database import db, User, Side, Tile, Game, Turn
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request
from itsdangerous import URLSafeSerializer
from mail import mail
from redis import Redis

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
mail.init_app(app)
redis = Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'])
serializer = URLSafeSerializer(app.config['SERIALIZER'])


@app.route('/games')
def games():
    """Display active games."""
    return render_template('games.html', games=Game.query.all())


@app.route('/games/start')
def start():
    """Create a game."""
    game = Game()

    # Add users to the game
    game.users = User.query.all()

    # Fetch the starting piece and add it to the board
    tile = Tile.query.filter_by(id=55).first()
    turn = Turn(
        tile_id=tile.id,
        user_id=game.users[0].id,
        x_idx=0,
        y_idx=0,
        played=datetime.utcnow(),
    )
    game.turns.append(turn)

    # Sample data
    for x, y, id in [
        (0, 2, 66),
        (1, 2, 3),
        (2, 2, 31),
        (0, 1, 18),
        (2, 1, 18),
        (1, 0, 18),
        (2, 0, 2),
        (0, 3, 1),
        (3, 1, 53),
        (4, 1, 1),
        (5, 1, 22),
        (4, 0, 56),
    ]:
        tile = Tile.query.filter_by(id=id).first()
        turn = Turn(
            tile_id=tile.id,
            user_id=game.users[0].id,
            x_idx=x,
            y_idx=y,
            played=datetime.utcnow(),
        )
        game.turns.append(turn)

    # Fetch the next user in turn
    user = game.users[1]

    # Create a turn for the user
    tile_ids_in_use = [x.tile_id for x in game.turns]
    tile = Tile.get_random(exclude_ids=tile_ids_in_use)
    turn = Turn(tile_id=tile.id, user_id=user.id)
    game.turns.append(turn)

    # Commit it all to the db
    db.session.add(game)
    db.session.commit()

    # Send the next user their turn
    user.send_email(
        'Your turn!',
        'turn.html',
        url=url_for(
            'game',
            id=game.id,
            signature=serializer.dumps([turn.id]),
            _external=True
        )
    )

    # Redirect the user to the game board
    return redirect(url_for('game', id=game.id))


@app.route('/games/<int:id>')
def game(id):
    """Display an active game with the given id."""
    game = Game.query.filter_by(id=id).first()
    if not game:
        return 'You seem lost...', 404

    # Assume it is not the users turn
    is_players_turn = False

    # If there is a signature in the request it may be them...
    signature = request.values.get('signature')
    if signature:
        try:
            turn_id = serializer.loads(signature)  # TODO: This is dumb V

            # Now see if it's actually their turn...
            turn = Turn.query.filter_by(id=turn_id[0], played=None).first()
            if turn:
                is_players_turn = True
        except:
            pass

    # Render the game board
    return render_template(
        'game.html',
        game=game,
        is_players_turn=is_players_turn
    )


@app.route('/tiles')
def tiles():
    """Lists all tiles."""
    return render_template('tiles.html', tiles=Tile.query.all())


@app.cli.command()
def initdb():
    """Recreates and populates the database."""
    db.reflect()
    db.drop_all()
    db.create_all()

    def init_users():
        users = [
            ('bluetickk', 'burmeister.corey@gmail.com'),
            ('junglist88', 'junglist88@gmail.com'),
            ('drfeelgood', 'doctor.feelgood89@gmail.com'),
            ('beanz', 'abihner@gmail.com'),
        ]
        for values in users:
            user = User(username=values[0], email=values[1])
            db.session.add(user)
        db.session.commit()

    def init_sides():
        sides = ['castle', 'land', 'road']
        for value in sides:
            side = Side(name=value)
            db.session.add(side)
        db.session.commit()

    def init_tiles():
        castle = Side.query.filter_by(name='castle').first()
        land = Side.query.filter_by(name='land').first()
        road = Side.query.filter_by(name='road').first()

        piece = Tile(
            path='city4.png',
            side_1=castle.id,
            side_2=castle.id,
            side_3=castle.id,
            side_4=castle.id,
            special=True,
        )

        db.session.add(piece)
        piece = Tile(
            path='road4.png',
            side_1=road.id,
            side_2=road.id,
            side_3=road.id,
            side_4=road.id,
        )
        db.session.add(piece)

        for _ in range(0, 4):
            piece = Tile(
                path='road3.png',
                side_1=land.id,
                side_2=road.id,
                side_3=road.id,
                side_4=road.id,
            )
            db.session.add(piece)

        for _ in range(0, 2):
            piece = Tile(
                path='city3sr.png',
                side_1=castle.id,
                side_2=castle.id,
                side_3=road.id,
                side_4=castle.id,
                special=True,
            )
            db.session.add(piece)

        piece = Tile(
            path='city3r.png',
            side_1=castle.id,
            side_2=castle.id,
            side_3=road.id,
            side_4=castle.id,
        )
        db.session.add(piece)

        piece = Tile(
            path='city3s.png',
            side_1=castle.id,
            side_2=castle.id,
            side_3=road.id,
            side_4=castle.id,
        )
        db.session.add(piece)

        for _ in range(0, 3):
            piece = Tile(
                path='city3.png',
                side_1=castle.id,
                side_2=castle.id,
                side_3=road.id,
                side_4=castle.id,
                special=True,
            )
            db.session.add(piece)

        for _ in range(0, 8):
            piece = Tile(
                path='road2ns.png',
                side_1=road.id,
                side_2=land.id,
                side_3=road.id,
                side_4=land.id,
            )
            db.session.add(piece)

        for _ in range(0, 2):
            piece = Tile(
                path='city2wes.png',
                side_1=land.id,
                side_2=castle.id,
                side_3=land.id,
                side_4=castle.id,
                special=True,
            )
            db.session.add(piece)

        piece = Tile(
            path='city2we.png',
            side_1=land.id,
            side_2=castle.id,
            side_3=land.id,
            side_4=castle.id,
        )
        db.session.add(piece)

        for _ in range(0, 9):
            piece = Tile(
                path='road2sw.png',
                side_1=land.id,
                side_2=land.id,
                side_3=road.id,
                side_4=road.id,
            )
            db.session.add(piece)

        for _ in range(0, 2):
            piece = Tile(
                path='city2nwsr.png',
                side_1=castle.id,
                side_2=road.id,
                side_3=road.id,
                side_4=castle.id,
                special=True,
            )
            db.session.add(piece)

        for _ in range(0, 3):
            piece = Tile(
                path='city2nwr.png',
                side_1=castle.id,
                side_2=road.id,
                side_3=road.id,
                side_4=castle.id,
            )
            db.session.add(piece)

        for _ in range(0, 2):
            piece = Tile(
                path='city2nws.png',
                side_1=castle.id,
                side_2=land.id,
                side_3=land.id,
                side_4=castle.id,
                special=True,
            )
            db.session.add(piece)

        for _ in range(0, 3):
            piece = Tile(
                path='city2nw.png',
                side_1=castle.id,
                side_2=land.id,
                side_3=land.id,
                side_4=castle.id,
            )
            db.session.add(piece)

        # Cloisters
        for _ in range(0, 4):
            piece = Tile(
                path='cloister.png',
                side_1=land.id,
                side_2=land.id,
                side_3=land.id,
                side_4=land.id,
            )
            db.session.add(piece)

        for _ in range(0, 2):
            piece = Tile(
                path='cloisterr.png',
                side_1=land.id,
                side_2=land.id,
                side_3=road.id,
                side_4=land.id,
            )
            db.session.add(piece)

        for _ in range(0, 3):
            piece = Tile(
                path='city11we.png',
                side_1=land.id,
                side_2=castle.id,
                side_3=land.id,
                side_4=castle.id,
            )
            db.session.add(piece)

        for _ in range(0, 2):
            piece = Tile(
                path='city11ne.png',
                side_1=castle.id,
                side_2=castle.id,
                side_3=land.id,
                side_4=land.id,
            )
            db.session.add(piece)

        for _ in range(0, 3):
            piece = Tile(
                path='city1rwe.png',
                side_1=castle.id,
                side_2=road.id,
                side_3=land.id,
                side_4=road.id,
            )
            db.session.add(piece)

        # Start
        piece = Tile(
            path='city1rwe.png',
            side_1=castle.id,
            side_2=road.id,
            side_3=land.id,
            side_4=road.id,
        )
        db.session.add(piece)

        for _ in range(0, 3):
            piece = Tile(
                path='city1rswe.png',
                side_1=castle.id,
                side_2=road.id,
                side_3=road.id,
                side_4=road.id,
            )
            db.session.add(piece)

        for _ in range(0, 3):
            piece = Tile(
                path='city1rsw.png',
                side_1=castle.id,
                side_2=land.id,
                side_3=road.id,
                side_4=road.id,
            )
            db.session.add(piece)

        for _ in range(0, 3):
            piece = Tile(
                path='city1rse.png',
                side_1=castle.id,
                side_2=road.id,
                side_3=road.id,
                side_4=land.id,
            )
            db.session.add(piece)

        for _ in range(0, 5):
            piece = Tile(
                path='city1.png',
                side_1=castle.id,
                side_2=land.id,
                side_3=land.id,
                side_4=land.id,
            )
            db.session.add(piece)

        db.session.commit()

    init_users()
    init_sides()
    init_tiles()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
