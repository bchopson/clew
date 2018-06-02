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

    def undo_last_turn(self):
        if (self.game.suggestions or self.game.accusations) and self.game.last_turn_clauses:
            if self.game.suggestions and self.game.accusations:
                recent_suggestion = self.game.suggestions[-1]
                recent_accusation = self.game.accusations[-1]

                if recent_suggestion.insert_date > recent_accusation.insert_date:
                    self.game.suggestions = self.game.suggestions[:-1]
                else:
                    self.game.accusations = self.game.accusations[:-1]
            elif self.game.suggestions:
                self.game.suggestions = self.game.suggestions[:-1]
            elif self.game.accusations:
                self.game.accusations = self.game.accusations[:-1]

            self.game.clauses = [
                clause for clause in self.game.clauses
                if clause not in self.game.last_turn_clauses
            ]
            return True
        return False

    def suggest(self, suggestion):
        suggester_idx = PEOPLE.index(suggestion.suggester)
        clauses = []
        if suggestion.answerer:
            answerer_idx = PEOPLE.index(suggestion.answerer)
            for pIdx in self.players_between(suggestion.suggester, suggestion.answerer):
                for card in suggestion.all_cards:
                    cIdx = self.CARDS.index(card)
                    clauses.append(
                        [-self.index_pair_number(cIdx, pIdx)])

            if suggestion.card_shown is None:
                clauses.append(
                    [self.index_pair_number(
                        self.CARDS.index(card), answerer_idx)
                     for card in suggestion.all_cards]
                )
            else:
                cIdx = self.CARDS.index(suggestion.card_shown)
                clauses.append(
                    [self.index_pair_number(cIdx, answerer_idx)])
        else:
            for pIdx in self.players_between(suggestion.suggester, suggestion.suggester):
                for card in suggestion.all_cards:
                    cIdx = self.CARDS.index(card)
                    clauses.append(
                        [-self.index_pair_number(cIdx, pIdx)])
            if suggestion.suggester == self.game.primary_player:
                for card in suggestion.all_cards:
                    if card not in self.primary_player.cards:
                        cIdx = self.CARDS.index(card)
                        clauses.append(
                            [self.index_pair_number(
                                cIdx, self.case_file_index)])
            else:
                for card in suggestion.all_cards:
                    cIdx = self.CARDS.index(card)
                    clauses.append([
                        self.index_pair_number(cIdx, self.case_file_index),
                        self.index_pair_number(cIdx, suggester_idx)
                    ])
        self.game.clauses += clauses
        self.game.last_turn_clauses = clauses
        self.game.suggestions.append(suggestion)

    def accuse(self, accusation):
        clauses = []
        if (accusation.is_correct):
            clauses += [
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
            clauses += [
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
        self.game.clauses += clauses
        self.game.last_turn_clauses = clauses
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
