import os
import json

import mongoengine
from flask import abort, g, jsonify, Flask, request

from models import *
from engine import Engine


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

@app.route(f'{api_prefix}/games', methods=['POST'])
def create_game():
    game = Game(**request.get_json(force=True))
    if (len(game.players) < 3 or len(game.players) > 6):
        abort(400)
    return _to_wrapped_json(game.save())

@app.route(f'{api_prefix}/games', methods=['GET'])
def get_games():
    return _to_wrapped_json(Game.objects())

def _to_wrapped_json(mongo_object):
    return jsonify({ 'data': json.loads(mongo_object.to_json()) })

if __name__ == '__main__':
    app.run()
