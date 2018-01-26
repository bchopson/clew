import os
import json

import mongoengine
from flask import abort, g, jsonify, Flask, request
from flask_cors import CORS

from .models import *
from .engine import Engine


app = Flask(__name__)
CORS(app)

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


@app.route(f'{api_prefix}/people', methods=['GET'])
def get_people():
    return jsonify({'data': PEOPLE})


@app.route(f'{api_prefix}/weapons', methods=['GET'])
def get_weapons():
    return jsonify({'data': WEAPONS})


@app.route(f'{api_prefix}/rooms', methods=['GET'])
def get_rooms():
    return jsonify({'data': ROOMS})


@app.route(f'{api_prefix}/games', methods=['GET'])
@app.route(f'{api_prefix}/games/<string:game_id>', methods=['GET'])
def get_game(game_id=None):
    if game_id is None:
        return _to_wrapped_json(Game.objects.exclude('clauses'))
    else:
        game = Game.objects.exclude('clauses').get(id=game_id)
        if game is None:
            abort(404)
        return _to_wrapped_json(game)


@app.route(f'{api_prefix}/games', methods=['POST'])
def create_game():
    game = Game(**request.get_json(force=True))
    if (len(game.players) < 3 or len(game.players) > 6):
        abort(400)
    engine = Engine(game)
    engine.add_initial_clauses()
    game.save()
    return _to_wrapped_json(Game.objects.exclude('clauses').get(id=game.id))


@app.route(f'{api_prefix}/games/<string:game_id>/guesses', methods=['GET'])
@app.route(f'{api_prefix}/games/<string:game_id>/guesses/<int:index>',
           methods=['GET'])
def get_guess(game_id, index=None):
    game = Game.objects.get(id=game_id)
    if game is None:
        abort(404)

    if index is None:
        return jsonify(
            {'data': [json.loads(guess.to_json()) for guess in game.guesses]})
    else:
        try:
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
    engine.suggest(guess)
    game.save()
    return _to_wrapped_json(guess)


@app.route(f'{api_prefix}/games/<string:game_id>/accusations', methods=['GET'])
@app.route(f'{api_prefix}/games/<string:game_id>/accusations/<int:index>',
           methods=['GET'])
def get_accusation(game_id, index=None):
    game = Game.objects.get(id=game_id)
    if game is None:
        abort(404)

    if index is None:
        return jsonify(
            {'data': [
                json.loads(accusation.to_json())
                for accusation in game.accusations]})
    else:
        try:
            return _to_wrapped_json(game.accusations.get(index=index))
        except DoesNotExist:
            abort(404)


@app.route(f'{api_prefix}/games/<string:game_id>/accusations',
           methods=['POST'])
def add_accusation(game_id):
    game = Game.objects.get(id=game_id)
    if game is None:
        abort(404)

    accusation = Accusation(**request.get_json(force=True))
    accusation.index = len(game.accusations)
    engine = Engine(game)
    engine.accuse(accusation)
    game.save()
    return _to_wrapped_json(accusation)


@app.route(f'{api_prefix}/games/<string:game_id>/notebook', methods=['GET'])
def get_notebook(game_id):
    game = Game.objects.get(id=game_id)
    engine = Engine(game)
    return jsonify({'data': engine.notebook})


def _to_wrapped_json(mongo_object):
    return jsonify({'data': json.loads(mongo_object.to_json())})


if __name__ == '__main__':
    app.run()
