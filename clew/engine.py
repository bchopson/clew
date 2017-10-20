#!env/bin/python3

import itertools
from mongoengine import *

from .models import PEOPLE, WEAPONS, ROOMS


class Engine():

    CARDS = PEOPLE + WEAPONS + ROOMS
    clauses = []

    def __init__(self, game):
        self.game = game
        self.add_initial_clauses()

    @property
    def places(self):
        return len(self.game.players) + 1

    @property
    def case_file_index(self):
        return self.places - 1

    def card_player_pair_number(self, card, player):
        return self.index_pair_number(self.CARDS.index(card), player.index)

    def index_pair_number(self, card_index, player_index):
        return player_index * len(self.CARDS) + card_index + 1

    def add_initial_clauses(self):
        self.clauses = (
            self.every_card_present() +
            self.card_one_place() +
            self.case_file_each_type() +
            self.case_file_type_exclusive() +
            self.player_hand()
        )

    # Each card is in at least one place, including the case file
    def every_card_present(self):
        return [[self.index_pair_number(c, p)
                for p in range(self.places)]
               for c in range(len(self.CARDS))]

    # Each card is in exactly one place
    def card_one_place(self):
        return [[-self.index_pair_number(self.CARDS.index(card), pair[0]),
                 -self.index_pair_number(self.CARDS.index(card), pair[1])]
                for pair in itertools.combinations(range(self.places), 2)
               for card in self.CARDS]

    # At least one card of each category is in the case file
    def case_file_each_type(self):
        return (
            [[self.index_pair_number(self.CARDS.index(card), self.case_file_index)
            for card in PEOPLE]] +

            [[self.index_pair_number(self.CARDS.index(card), self.case_file_index)
            for card in WEAPONS]] +

            [[self.index_pair_number(self.CARDS.index(card), self.case_file_index)
            for card in ROOMS]]
        )

    def case_file_type_exclusive(self):
        return (
            [[-self.index_pair_number(self.CARDS.index(pair[0]), self.case_file_index),
              -self.index_pair_number(self.CARDS.index(pair[1]), self.case_file_index)]
            for pair in itertools.combinations(PEOPLE, 2)] +

            [[-self.index_pair_number(self.CARDS.index(pair[0]), self.case_file_index),
              -self.index_pair_number(self.CARDS.index(pair[1]), self.case_file_index)]
            for pair in itertools.combinations(WEAPONS, 2)] +

            [[-self.index_pair_number(self.CARDS.index(pair[0]), self.case_file_index),
              -self.index_pair_number(self.CARDS.index(pair[1]), self.case_file_index)]
            for pair in itertools.combinations(ROOMS, 2)]
        )

    def player_hand(self):
        player = next((p for p in self.game.players if p.name == self.game.primary_player), None)
        return [[self.index_pair_number(self.CARDS.index(card), player.index)]
               for card in player.cards]
