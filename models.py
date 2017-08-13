from mongoengine import *


PEOPLE = ( 'Prof. Plum', 'Mr. Green', 'Mrs. White', 'Mrs. Peacock', 'Miss Scarlett', 'Col. Mustard' )
WEAPONS = ( 'dagger', 'revolver', 'wrench', 'lead pipe', 'rope', 'candlestick' )
ROOMS = ( 'kitchen', 'ballroom', 'conservatory', 'billiard room', 'library', 'study', 'hall', 'lounge', 'dining room' )


class Player(EmbeddedDocument):
    index = IntField(required=True)
    people = ListField(StringField(choices=PEOPLE))
    weapons = ListField(StringField(choices=WEAPONS))
    rooms = ListField(StringField(choices=ROOMS))
    not_people = ListField(StringField(choices=PEOPLE))
    not_weapons = ListField(StringField(choices=WEAPONS))
    not_rooms = ListField(StringField(choices=ROOMS))


class Guess(EmbeddedDocument):
    index = IntField(required=True)
    guesser = IntField(required=True)
    answerer = IntField(required=True)
    person = StringField(required=True, choices=PEOPLE)
    weapon = StringField(required=True, choices=WEAPONS)
    room = StringField(required=True, choices=ROOMS)


class Game(Document):
    players = EmbeddedDocumentListField(Player)
    guesses = EmbeddedDocumentListField(Guess)

    answer_person = StringField(choices=PEOPLE)
    answer_weapon = StringField(choices=WEAPONS)
    answer_room = StringField(choices=ROOMS)
