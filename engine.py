#!env/bin/python3

from models import *
from mongoengine import *

class Engine():

    def __init__(self, game):
        self.game = game

    def play_turn(self, guess):
        self.game.guesses.add(guess)
        # for each guess (most recent first)
        self.calculate(guess)
        for guess in self.game.guesses.order_by('index'):
            self.apply_guess_to_answerer(guess)

    def calculate(self, guess):
        i = guess.guesser.index + 1;
        while (i != guess.answerer.index):
            self.game.players[i].not_people.add(guess.person)
            self.game.players[i].not_weapons.add(guess.weapon)
            self.game.players[i].not_rooms.add(guess.room)
            i = (i + 1) % game.players.count

        apply_guess_to_answerer(guess)

    def apply_guess_to_answerer(guess):
        answerer = guess.answerer
        if answerer is None:
            guesser = guess.guesser
            if guesser.not_people.contains(guess.person):
                self.game.answer_person = guess.person
            if guesser.not_weapons.contains(guess.weapon):
                self.game.answer_weapon = guess.weapon
            if guesser.not_rooms.contains(guess.room):
                self.game.answer_room = guess.room
        else:
            if (answerer.not_people.contains(guess.person) and
                    answerer.not_weapons.contains(guess.weapon)):
                answerer.rooms.add(guess.room)
            if (answerer.not_people.contains(guess.person) and
                    answerer.not_rooms.contains(guess.room)):
                answerer.weapons.add(guess.weapon)
            if (answerer.not_weapons.contains(guess.weapon) and
                    answerer.not_rooms.contains(guess.room)):
                answerer.people.add(guess.person)
