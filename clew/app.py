import os
import json

import mongoengine
from flask import abort, g, jsonify, Flask, request

from .models import *
from .engine import Engine


app = Flask(__name__)

api_prefix = '/api/v1'

def connect_db():
    return mongoengine.connect(os.environ['DATABASE'])

@app.before_request
def before_request():
    if not hasattr(g, 'db'):
        g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route(f'{api_prefix}/games', methods=['GET'])
@app.route(f'{api_prefix}/games/<string:game_id>', methods=['GET'])
def get_game(game_id=None):
    if game_id is None:
        return _to_wrapped_json(Game.objects())
    else:
        game = Game.objects.get(id=game_id)
        if game is None:
            abort(404)
        return _to_wrapped_json(game)

@app.route(f'{api_prefix}/games', methods=['POST'])
def create_game():
    game = Game(**request.get_json(force=True))
    if (len(game.players) < 3 or len(game.players) > 6):
        abort(400)
    return _to_wrapped_json(game.save())

@app.route(f'{api_prefix}/games/<string:game_id>/guesses', methods=['GET'])
@app.route(f'{api_prefix}/games/<string:game_id>/guesses/<int:index>', methods=['GET'])
def get_guess(game_id, index=None):
    game = Game.objects.get(id=game_id)
    if game is None:
        abort(404)

    if index is None:
        return jsonify({ 'data': [json.loads(guess.to_json()) for guess in game.guesses] })
    else:
        try:
            # return jsonify({ 'data': game.guesses.get(index=index) })
            return _to_wrapped_json(game.guesses.get(index=index))
        except DoesNotExist:
            abort(404)

@app.route(f'{api_prefix}/games/<string:game_id>/guesses', methods=['POST'])
def add_guess(game_id):
    game = Game.objects.get(id=game_id)
    if game is None:
        abort(404)

    guess = Guess(**request.get_json(force=True))
    guess.index = len(game.guesses)
    engine = Engine(game)
    engine.play_turn(guess)
    game.save()
    return _to_wrapped_json(guess)

def _to_wrapped_json(mongo_object):
    return jsonify({ 'data': json.loads(mongo_object.to_json()) })

if __name__ == '__main__':
    app.run()
