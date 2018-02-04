#!env/bin/python3

import itertools
import pycosat
from mongoengine import *

from .models import PEOPLE, WEAPONS, ROOMS


class Engine():

    CARDS = PEOPLE + WEAPONS + ROOMS
    UNKNOWN = 'unknown'
    FALSE = 'false'
    TRUE = 'true'

    def __init__(self, game):
        self.game = game

    @property
    def case_file_index(self):
        return max([player.index for player in self.game.players]) + 1

    @property
    def all_indices(self):
        player_indices = [player.index for player in self.game.players]
        player_indices.append(self.case_file_index)
        return player_indices

    @property
    def primary_player(self):
        return next(
            (p for p in self.game.players
             if p.name == self.game.primary_player),
            None
        )

    @property
    def notebook(self):
        literals = [
            {
                'player': 'Case File' if p == self.case_file_index
                          else PEOPLE[p],
                'card': self.CARDS[c],
                'index': self.index_pair_number(c, p)
            }
            for p in self.all_indices
            for c in range(len(self.CARDS))
        ]
        return [{
                    'player': literal['player'],
                    'card': literal['card'],
                    'has_card': self.test_literal(literal['index']),
                } for literal in literals]

    def test_literal(self, literal):
        result = self.UNKNOWN
        if pycosat.solve(self.game.clauses + [[literal]]) == 'UNSAT':
            result = self.FALSE
        elif pycosat.solve(self.game.clauses + [[-literal]]) == 'UNSAT':
            result = self.TRUE
        return result

    def players_between(self, player1, player2):
        playerIndices = [player.index for player in self.game.players]
        playerIndices.sort()
        player1_index = PEOPLE.index(player1)
        player2_index = PEOPLE.index(player2)
        between = []
        currentIdx = ((playerIndices.index(player1_index) + 1)
                      % len(playerIndices))
        while playerIndices[currentIdx] != player2_index:
            between.append(playerIndices[currentIdx])
            currentIdx = (currentIdx + 1) % len(playerIndices)
        return between

    def index_pair_number(self, card_index, player_index):
        return player_index * len(self.CARDS) + card_index + 1

    @property
    def human_readable_clauses(self):
        readable = ''
        for clause in self.game.clauses:
            readable += '{}\n'.format(self.human_readable_clause(clause))
        return readable

    def human_readable_clause(self, clause):
        readable = ''
        for i in range(len(clause)):
            prop = clause[i]
            player_index = (abs(prop) - 1) // len(self.CARDS)
            card_index = abs(prop) - (player_index * len(self.CARDS)) - 1
            sep = ' || ' if i < len(clause) - 1 else ''
            output = '{} has {}{}' if prop >= 0 else "{} doesn't have {}{}"
            player = (
                'Case File'
                if player_index == self.case_file_index
                else PEOPLE[player_index])
            readable += output.format(player, self.CARDS[card_index], sep)
        return readable

    def suggest(self, guess):
        guesser_idx = PEOPLE.index(guess.guesser)
        if guess.answerer:
            answerer_idx = PEOPLE.index(guess.answerer)
            for pIdx in self.players_between(guess.guesser, guess.answerer):
                for card in guess.all_cards:
                    cIdx = self.CARDS.index(card)
                    self.game.clauses.append(
                        [-self.index_pair_number(cIdx, pIdx)])

            if guess.card_shown is None:
                self.game.clauses.append(
                    [self.index_pair_number(
                        self.CARDS.index(card), answerer_idx)
                     for card in guess.all_cards]
                )
            else:
                cIdx = self.CARDS.index(guess.card_shown)
                self.game.clauses.append(
                    [self.index_pair_number(cIdx, answerer_idx)])
        else:
            for pIdx in self.players_between(guess.guesser, guess.guesser):
                for card in guess.all_cards:
                    cIdx = self.CARDS.index(card)
                    self.game.clauses.append(
                        [-self.index_pair_number(cIdx, pIdx)])
            if guess.guesser == self.game.primary_player:
                for card in guess.all_cards:
                    if card not in self.primary_player.cards:
                        cIdx = self.CARDS.index(card)
                        self.game.clauses.append(
                            [self.index_pair_number(
                                cIdx, self.case_file_index)])
            else:
                for card in guess.all_cards:
                    cIdx = self.CARDS.index(card)
                    self.game.clauses.append([
                        self.index_pair_number(cIdx, self.case_file_index),
                        self.index_pair_number(cIdx, guesser_idx)
                    ])
        self.game.guesses.append(guess)

    def accuse(self, accusation):
        if (accusation.is_correct):
            self.game.clauses += [
                [self.index_pair_number(
                    self.CARDS.index(accusation.person),
                    self.case_file_index)],
                [self.index_pair_number(
                    self.CARDS.index(accusation.weapon),
                    self.case_file_index)],
                [self.index_pair_number(
                    self.CARDS.index(accusation.room),
                    self.case_file_index)]
            ]
        else:
            self.game.clauses += [
                [-self.index_pair_number(
                    self.CARDS.index(accusation.person),
                    self.case_file_index)],
                [-self.index_pair_number(
                    self.CARDS.index(accusation.weapon),
                    self.case_file_index)],
                [-self.index_pair_number(
                    self.CARDS.index(accusation.room),
                    self.case_file_index)]
            ]
        self.game.accusations.append(accusation)

    def add_initial_clauses(self):
        self.game.clauses = (
            self.every_card_present() +
            self.card_one_place() +
            self.case_file_each_type() +
            self.case_file_type_exclusive() +
            self.player_hand()
        )

    # Each card is in at least one place, including the case file
    def every_card_present(self):
        return [[self.index_pair_number(c, p)
                for p in self.all_indices]
                for c in range(len(self.CARDS))]

    # Each card is in exactly one place
    def card_one_place(self):
        return [[-self.index_pair_number(self.CARDS.index(card), pair[0]),
                 -self.index_pair_number(self.CARDS.index(card), pair[1])]
                for pair in itertools.combinations(self.all_indices, 2)
                for card in self.CARDS]

    # At least one card of each category is in the case file
    def case_file_each_type(self):
        return (
            [[self.index_pair_number(
                self.CARDS.index(card), self.case_file_index)
             for card in PEOPLE]] +

            [[self.index_pair_number(
                self.CARDS.index(card), self.case_file_index)
             for card in WEAPONS]] +

            [[self.index_pair_number(
                self.CARDS.index(card), self.case_file_index)
             for card in ROOMS]]
        )

    # Only one card of each category is in the case file
    def case_file_type_exclusive(self):
        return (
            [[-self.index_pair_number(
                self.CARDS.index(pair[0]), self.case_file_index),
              -self.index_pair_number(
                  self.CARDS.index(pair[1]), self.case_file_index)]
             for pair in itertools.combinations(PEOPLE, 2)] +

            [[-self.index_pair_number(
                self.CARDS.index(pair[0]), self.case_file_index),
              -self.index_pair_number(
                  self.CARDS.index(pair[1]), self.case_file_index)]
             for pair in itertools.combinations(WEAPONS, 2)] +

            [[-self.index_pair_number(
                self.CARDS.index(pair[0]), self.case_file_index),
              -self.index_pair_number(
                  self.CARDS.index(pair[1]), self.case_file_index)]
             for pair in itertools.combinations(ROOMS, 2)]
        )

    # The player's hand
    def player_hand(self):
        player = next(
            (p for p in self.game.players
             if p.name == self.game.primary_player), None)
        other_players = [
            index for index in self.all_indices if index != player.index]
        clauses = []
        for card in self.CARDS:
            cIndex = self.CARDS.index(card)
            if card in player.cards:
                clauses.append([self.index_pair_number(cIndex, player.index)])
                clauses += [
                    [-self.index_pair_number(cIndex, pIndex)]
                    for pIndex in other_players]
            else:
                clauses.append([-self.index_pair_number(cIndex, player.index)])
        return clauses
