#!env/bin/python3

from models import *
from mongoengine import *

class Engine():

    def __init__(self, game):
        self.game = game

    def play_turn(self, guess):
        self.game.guesses.append(guess)
        self._calculate(guess)
        for guess in self.game.guesses:
            self._apply_guess_to_answerer(guess)

    def _calculate(self, guess):
        guesser = self.game.players.get(index=guess.guesser)
        answerer = self.game.players.get(index=guess.answerer)
        if answerer is None:
            if guess.person in guesser.not_cards:
                self.game.answer_person = guess.person
            if guess.weapon in guesser.not_cards:
                self.game.answer_weapon = guess.weapon
            if guess.room in guesser.not_cards:
                self.game.answer_room = guess.room

    # def _calculate(self, guess):
    #     guesser = self.game.players.get(index=guess.guesser)
    #     i = (guess.guesser + 1) % len(self.game.players)
    #     while (i != guess.answerer):
    #         player = self.game.players.get(index=i)
    #         self._add_card_unique(player.not_people, guess.person)
    #         self._add_card_unique(player.not_weapons, guess.weapon)
    #         self._add_card_unique(player.rooms, guess.room)
    #         i = (i + 1) % len(self.game.players)

    #     self._apply_guess_to_answerer(guess)

    def _apply_guess_to_answerer(self, guess):
        answerer = self.game.players.get(index=guess.answerer)
        guesser = self.game.players.get(index=guess.guesser)
        if answerer is None:
            if self._has_card(guesser.not_people, guess.person):
                self.game.answer_person = guess.person
            if self._has_card(guesser.not_weapons, guess.weapon):
                self.game.answer_weapon = guess.weapon
            if self._has_card(guesser.not_rooms, guess.room):
                self.game.answer_room = guess.room
        else:
            if (self._has_card(answerer.not_people, guess.person) and
                    self._has_card(answerer.not_weapons, guess.weapon)):
                self._add_card_unique(answerer.rooms, guess.room)
            if (self._has_card(answerer.not_people, guess.person) and
                    self._has_card(answerer.not_rooms, guess.room)):
                self._add_card_unique(answerer.weapons, guess.weapon)
            if (self._has_card(answerer.not_weapons, guess.weapon) and
                    self._has_card(answerer.not_rooms, guess.room)):
                self._add_card_unique(answerer.people, guess.person)

            if (self._has_card(guesser.people, guess.person) and
                    self._has_card(guesser.not_weapons, guess.weapon)):
                self.game.answer_room = guess.room
            if (self._has_card(guesser.not_people, guess.person) and
                    self._has_card(guesser.not_rooms, guess.room)):
                self.game.answer_weapon = guess.weapon
            if (self._has_card(guesser.not_weapons, guess.weapon) and
                    self._has_card(guesser.not_rooms, guess.room)):
                self.game.answer_person = guess.person

    def _has_card(self, card_list, card_query):
        return [card for card in card_list if card == card_query]

    def _add_card_unique(self, card_list, card):
        card_list.append(card)
        card_list = list(set(card_list))
