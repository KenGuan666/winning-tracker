# Note: DO NOT directly modify any attributes of any objects
# If no getter/setter is provided, consider the attribute as Private

from typing import Dict, Any
from .Game import Game


"""
    Session represents the values user enters into a Session record
    Performs type check on user values entered
    DO NOT directly modify any attributes after init

    Attributes:
    - game: Game : The Game user records Session for
    - values: Dict[str, <expectedType>] : The field values user enters
"""
class Session:

    def __init__(self, game: Game, values: Dict[str, Any]):
        self.game = game
        self.fieldValues = game.parse_field_values(values)

    def get_game(self):
        return self.game

    def get_values(self):
        return self.fieldValues

    def equals(self, otherSession: 'Session'):
        if isinstance(otherSession, Session):
            return self.game.get_name() == otherSession.game.get_name() and \
                self.fieldValues == otherSession.fieldValues
        return False
