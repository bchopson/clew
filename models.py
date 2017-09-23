from mongoengine import *


PEOPLE = ( 'Prof. Plum', 'Mr. Green', 'Mrs. White', 'Mrs. Peacock', 'Miss Scarlett', 'Col. Mustard' )
WEAPONS = ( 'dagger', 'revolver', 'wrench', 'lead pipe', 'rope', 'candlestick' )
ROOMS = ( 'kitchen', 'ballroom', 'conservatory', 'billiard room', 'library', 'study', 'hall', 'lounge', 'dining room' )


class Player(EmbeddedDocument):
    index = IntField(required=True)
    card_count = IntField(required=True)
    people = ListField(StringField(choices=PEOPLE))
    weapons = ListField(StringField(choices=WEAPONS))
    rooms = ListField(StringField(choices=ROOMS))
    not_people = ListField(StringField(choices=PEOPLE))
    not_weapons = ListField(StringField(choices=WEAPONS))
    not_rooms = ListField(StringField(choices=ROOMS))

    @property
    def cards(self):
        return self.people + self.weapons + self.rooms

    @property
    def not_cards(self):
        return self.not_people + self.not_weapons + self.not_rooms


class Guess(EmbeddedDocument):
    index = IntField()
    guesser = IntField(required=True)
    answerer = IntField()
    person = StringField(required=True, choices=PEOPLE)
    weapon = StringField(required=True, choices=WEAPONS)
    room = StringField(required=True, choices=ROOMS)


class Guess(EmbeddedDocument):
    index = IntField()
    guesser = IntField(required=True)
    answerer = IntField()
    person = StringField(required=True, choices=PEOPLE)
    weapon = StringField(required=True, choices=WEAPONS)
    room = StringField(required=True, choices=ROOMS)
    card = StringField(required=True, choices=PEOPLE+WEAPONS+ROOMS)


class Game(Document):
    primary_index = IntField(required=True)
    players = EmbeddedDocumentListField(Player)
    guesses = EmbeddedDocumentListField(Guess)

    answer_person = StringField(choices=PEOPLE)
    answer_weapon = StringField(choices=WEAPONS)
    answer_room = StringField(choices=ROOMS)

    def known_cards(self):
        cards = []
        for player in self.players:
            cards += player.people + player.weapons + player.rooms
        return set(cards)
