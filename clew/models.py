from mongoengine import *


PEOPLE = [
    'Miss Scarlett',
    'Col. Mustard',
    'Mrs. White',
    'Mr. Green',
    'Mrs. Peacock',
    'Prof. Plum',
]
T_PEOPLE = tuple(PEOPLE)
WEAPONS = [
    'dagger',
    'revolver',
    'wrench',
    'lead pipe',
    'rope',
    'candlestick',
]
T_WEAPONS = tuple(WEAPONS)
ROOMS = [
    'kitchen',
    'ballroom',
    'conservatory',
    'billiard room',
    'library',
    'study',
    'hall',
    'lounge',
    'dining room',
]
T_ROOMS = tuple(ROOMS)

class Player(EmbeddedDocument):

    def __init__(self, *args, **kwargs):
        EmbeddedDocument.__init__(self, *args, **kwargs)
        self.index = PEOPLE.index(kwargs['name']) if kwargs['name'] else -1

    name = StringField(required=True, choices=T_PEOPLE)
    card_count = IntField(required=True)
    people = ListField(StringField(choices=T_PEOPLE))
    weapons = ListField(StringField(choices=T_WEAPONS))
    rooms = ListField(StringField(choices=T_ROOMS))
    index = IntField()

    @property
    def cards(self):
        return self.people + self.weapons + self.rooms


class Suggestion(EmbeddedDocument):
    index = IntField(required=True)
    suggester = StringField(required=True, choices=T_PEOPLE)
    answerer = StringField(choices=T_PEOPLE)
    person = StringField(required=True, choices=T_PEOPLE)
    weapon = StringField(required=True, choices=T_WEAPONS)
    room = StringField(required=True, choices=T_ROOMS)
    was_card_shown = BooleanField(required=True)
    card_shown = StringField(choices=T_PEOPLE+T_WEAPONS+T_ROOMS)

    @property
    def all_cards(self):
        return [self.person, self.weapon, self.room]


class Accusation(EmbeddedDocument):
    index = IntField(required=True)
    accuser = StringField(required=True, choices=T_PEOPLE)
    person = StringField(required=True, choices=T_PEOPLE)
    weapon = StringField(required=True, choices=T_WEAPONS)
    room = StringField(required=True, choices=T_ROOMS)
    is_correct = BooleanField(required=True)


class Game(Document):
    primary_player = StringField(choices=T_PEOPLE)
    players = SortedListField(EmbeddedDocumentField(Player), ordering="index")
    suggestions = SortedListField(EmbeddedDocumentField(Suggestion), ordering="index")
    accusations = SortedListField(
        EmbeddedDocumentField(Accusation), ordering="index")
    clauses = ListField(ListField(IntField()))
