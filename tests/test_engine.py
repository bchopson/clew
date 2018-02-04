import pytest

from clew import *


class TestEngine():

    @pytest.fixture
    def create_engine(self):
        return Engine(self.create_game())

    def test_players_between(self):
        engine = Engine(self.create_game_sparse_players())
        between = engine.players_between('Miss Scarlett', 'Mr. Green')
        assert sorted(between) == [2]
        between = engine.players_between('Mr. Green', 'Miss Scarlett')
        assert sorted(between) == [5]
        between = engine.players_between('Mr. Green', 'Mrs. White')
        assert between == [5, 0]
        between = engine.players_between('Miss Scarlett', 'Prof. Plum')
        assert sorted(between) == [2, 3]
        between = engine.players_between('Prof. Plum', 'Miss Scarlett')
        assert sorted(between) == []
        between = engine.players_between('Mrs. White', 'Mrs. White')
        assert sorted(between) == [0, 3, 5]

    def test_human_readable_clause(self):
        engine = self.create_engine()
        clause = [1, -1]
        readable = engine.human_readable_clause(clause)
        assert readable == (
            "Miss Scarlett has Miss Scarlett "
            "|| Miss Scarlett doesn't have Miss Scarlett")
        clause = [22, 91, -97]
        readable = engine.human_readable_clause(clause)
        assert readable == (
            "Col. Mustard has Miss Scarlett || Case File has dagger "
            "|| Case File doesn't have kitchen")

    def test_suggest_discover_opponent(self):
        engine = self.create_engine()
        initial_clauses = list(engine.game.clauses)
        guess = Guess(
            index=0,
            guesser='Col. Mustard',
            answerer='Mr. Green',
            person='Mrs. White',
            weapon='dagger',
            room='ballroom',
            was_card_shown=True,
            card_shown='Mrs. White'
        )
        engine.suggest(guess)
        expected = [[-45], [-49], [-56], [66]]
        assert (
            sorted(initial_clauses + expected) == sorted(engine.game.clauses))

    def test_suggest_discover_case_file(self):
        engine = self.create_engine()
        initial_clauses = list(engine.game.clauses)
        guess = Guess(
            index=0,
            guesser='Col. Mustard',
            person='Miss Scarlett',
            weapon='dagger',
            room='billiard room',
            was_card_shown=False,
        )
        engine.suggest(guess)
        expected = [
            [-1], [-7], [-16], [-43], [-49], [-58], [-64], [-70], [-79], [100]
        ]
        assert (
            sorted(initial_clauses + expected) == sorted(engine.game.clauses))

    def test_accuse_true(self):
        engine = self.create_engine()
        initial_clauses = list(engine.game.clauses)
        accusation = Accusation(
            index=0,
            accuser='Mrs. White',
            person='Prof. Plum',
            weapon='lead pipe',
            room='lounge',
            is_correct=True
        )
        engine.accuse(accusation)
        expected = [[90], [94], [104]]
        assert (
            sorted(initial_clauses + expected) == sorted(engine.game.clauses))

    def test_accuse_false(self):
        engine = self.create_engine()
        initial_clauses = list(engine.game.clauses)
        accusation = Accusation(
            accuser='Mrs. White',
            person='Prof. Plum',
            weapon='lead pipe',
            room='lounge',
            is_correct=False
        )
        engine.accuse(accusation)
        expected = [[-90], [-94], [-104]]
        assert (
            sorted(initial_clauses + expected) == sorted(engine.game.clauses))

    def test_every_card_present(self):
        engine = self.create_engine()
        ecp = engine.every_card_present()
        assert len(ecp) == 21
        for clause in ecp:
            assert clause[0] + 4 * 21 == clause[4]

    def test_card_one_place(self):
        engine = self.create_engine()
        cop = engine.card_one_place()
        assert len(cop) == 210
        for clause in cop:
            assert len(clause) == 2
            assert clause[0] < 0
            assert clause[1] < 0

    def test_case_file_each_type(self):
        engine = self.create_engine()
        cfet = engine.case_file_each_type()
        assert len(cfet) == 3
        assert sorted([len(clause) for clause in cfet]) == [6, 6, 9]

    def test_case_file_type_exclusive(self):
        engine = self.create_engine()
        cfte = engine.case_file_type_exclusive()
        assert len(cfte) == 66
        for clause in cfte:
            assert len(clause) == 2

    def test_player_hand(self):
        engine = self.create_engine()
        ph = engine.player_hand()
        assert sorted(ph) == [
            [-98], [-96], [-91], [-85], [-77], [-75], [-70], [-64], [-56],
            [-54], [-49], [-43], [-42], [-41], [-40], [-39], [-38], [-37],
            [-36], [-34], [-32], [-31], [-30], [-29], [-27], [-26], [-25],
            [-24], [-23], [-14], [-12], [-7], [-1], [22], [28], [33], [35],]

    def test_whole_game(self):
        game = Game(
            primary_player='Miss Scarlett',
            players=[
                Player(
                    name='Miss Scarlett',
                    card_count=3,
                    people=['Mrs. White'],
                    rooms=['library', 'study']),
                Player(name='Col. Mustard', card_count=3),
                Player(name='Mrs. White', card_count=3),
                Player(name='Mr. Green', card_count=3),
                Player(name='Mrs. Peacock', card_count=3),
                Player(name='Prof. Plum', card_count=3),
            ])
        engine = Engine(game)
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Miss Scarlett',
                person='Miss Scarlett',
                weapon='rope',
                room='lounge',
                answerer='Col. Mustard',
                was_card_shown=True,
                card_shown='Miss Scarlett',
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Col. Mustard',
                person='Mrs. Peacock',
                weapon='lead pipe',
                room='dining room',
                answerer='Mrs. Peacock',
                was_card_shown=True,
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Mrs. White',
                person='Col. Mustard',
                weapon='revolver',
                room='ballroom',
                answerer='Mrs. Peacock',
                was_card_shown=True,
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Mr. Green',
                person='Mrs. White',
                weapon='dagger',
                room='ballroom',
                answerer='Prof. Plum',
                was_card_shown=True,
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Mrs. Peacock',
                person='Mr. Green',
                weapon='candlestick',
                room='dining room',
                answerer='Mrs. White',
                was_card_shown=True,
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Miss Scarlett',
                person='Prof. Plum',
                weapon='rope',
                room='ballroom',
                answerer='Col. Mustard',
                was_card_shown=True,
                card_shown='Prof. Plum',
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Col. Mustard',
                person='Mrs. Peacock',
                weapon='rope',
                room='ballroom',
                answerer='Mrs. White',
                was_card_shown=True,
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Mrs. White',
                person='Col. Mustard',
                weapon='candlestick',
                room='study',
                answerer='Mr. Green',
                was_card_shown=True,
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Mr. Green',
                person='Mrs. Peacock',
                weapon='dagger',
                room='dining room',
                answerer='Mrs. Peacock',
                was_card_shown=True,
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Mrs. Peacock',
                person='Col. Mustard',
                weapon='lead pipe',
                room='dining room',
                answerer='Prof. Plum',
                was_card_shown=True,
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Prof. Plum',
                person='Mr. Green',
                weapon='dagger',
                room='conservatory',
                answerer='Mrs. White',
                was_card_shown=True,
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Miss Scarlett',
                person='Mrs. Peacock',
                weapon='dagger',
                room='lounge',
                answerer='Col. Mustard',
                was_card_shown=True,
                card_shown='lounge',
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Col. Mustard',
                person='Mrs. Peacock',
                weapon='dagger',
                room='dining room',
                answerer='Mrs. White',
                was_card_shown=True,
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Mrs. White',
                person='Mrs. Peacock',
                weapon='wrench',
                room='hall',
                answerer='Mr. Green',
                was_card_shown=True,
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Mr. Green',
                person='Mrs. White',
                weapon='lead pipe',
                room='conservatory',
                answerer='Prof. Plum',
                was_card_shown=True,
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Mrs. Peacock',
                person='Miss Scarlett',
                weapon='lead pipe',
                room='hall',
                answerer='Col. Mustard',
                was_card_shown=True,
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Prof. Plum',
                person='Mrs. Peacock',
                weapon='lead pipe',
                room='ballroom',
                was_card_shown=False,
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Miss Scarlett',
                person='Mrs. White',
                weapon='lead pipe',
                room='hall',
                answerer='Mrs. Peacock',
                was_card_shown=True,
                card_shown='hall',
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Mrs. White',
                person='Mrs. Peacock',
                weapon='lead pipe',
                room='hall',
                answerer='Mrs. Peacock',
                was_card_shown=True,
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Mrs. Peacock',
                person='Mrs. Peacock',
                weapon='lead pipe',
                room='hall',
                was_card_shown=False,
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Miss Scarlett',
                person='Mr. Green',
                weapon='lead pipe',
                room='study',
                answerer='Mrs. White',
                was_card_shown=True,
                card_shown='Mr. Green',
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Col. Mustard',
                person='Mrs. Peacock',
                weapon='lead pipe',
                room='ballroom',
                answerer='Prof. Plum',
                was_card_shown=True,
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Mrs. White',
                person='Mrs. Peacock',
                weapon='lead pipe',
                room='study',
                answerer='Miss Scarlett',
                was_card_shown=True,
                card_shown='study',
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Mr. Green',
                person='Mrs. White',
                weapon='lead pipe',
                room='study',
                answerer='Miss Scarlett',
                was_card_shown=True,
                card_shown='Mrs. White',
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Mrs. Peacock',
                person='Mrs. White',
                weapon='lead pipe',
                room='study',
                answerer='Miss Scarlett',
                was_card_shown=True,
                card_shown='Mrs. White',
            ))
        engine.suggest(
            Guess(
                index=len(engine.game.guesses),
                guesser='Prof. Plum',
                person='Mrs. Peacock',
                weapon='lead pipe',
                room='kitchen',
                answerer='Mr. Green',
                was_card_shown=True,
            ))
        engine.accuse(
            Accusation(
                index=len(engine.game.accusations),
                accuser='Miss Scarlett',
                person='Mrs. Peacock',
                weapon='lead pipe',
                room='billiard room',
                is_correct=True,
            ))
        for entry in engine.notebook:
            assert entry['has_card'] != Engine.UNKNOWN


    def create_game_sparse_players(self):
        game = Game()
        game.primary_player = PEOPLE[0]
        game.players = [
            self.create_player('Miss Scarlett', 4),
            self.create_player('Mrs. White', 4),
            self.create_player('Mr. Green', 5),
            self.create_player('Prof. Plum', 5),
        ]
        game.players[0].people = ['Miss Scarlett']
        game.players[0].weapons = ['dagger', 'candlestick']
        game.players[0].rooms = ['ballroom']
        return game

    def create_game(self):
        game = Game()
        game.primary_player = PEOPLE[1]
        game.players = [
            self.create_player('Miss Scarlett', 4),
            self.create_player('Col. Mustard', 4),
            self.create_player('Mrs. White', 5),
            self.create_player('Mr. Green', 5),
        ]
        game.players[1].people = ['Miss Scarlett']
        game.players[1].weapons = ['dagger', 'candlestick']
        game.players[1].rooms = ['ballroom']
        return game

    def create_player(self, name, card_count):
        player = Player(name=name, card_count=card_count)
        return player


if __name__ == '__main__':
    unittest.main()
