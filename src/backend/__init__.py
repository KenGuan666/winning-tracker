from typing import List

from database import Database, JSONDatabase
from definitions import Game, FieldDefinition

class Backend:

    def __init__(self, db: Database=JSONDatabase):
        self.db = db()

    def add_game(self, name: str, fields: List[FieldDefinition]) -> Game:
        # Game init may throw error on incorrect field type
        game = Game(name, fields)
        self.db.create_table(name, game.all_fields_as_dict())
        return game

    def get_all_games(self) -> List[Game]:
        return self.db.get_all_table_names()
