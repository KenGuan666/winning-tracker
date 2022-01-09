from typing import List, Dict, Any

from database import Database, JSONDatabase
from definitions import Game, FieldDefinition, Session

class Backend:

    def __init__(self, db: Database=JSONDatabase):
        self.db = db()

    def add_game(self, name: str, fields: List[FieldDefinition]) -> Game:
        # Game init may throw error on incorrect field type
        game = Game(name, fields)
        created = self.db.create_table(name, game.all_fields_as_dict())
        return created and game

    def get_all_games(self) -> List[Game]:
        return self.db.get_all_table_names()

    def add_session(self, session: Session, _id=None) -> str:
        # Game must already exists in db
        return self.db.insert_row(session.game.get_name(), session.get_values(), _id=_id)

    def construct_game_from_db(self, gameName: str) -> Game:
        dbSchema = self.db.get_table_schema(gameName)
        return Game(gameName, dbSchema)

    def get_sessions(self, gameName: str, filter) -> Dict[str, Session]:
        if filter:
            raise NotImplementedError()

        game = self.construct_game_from_db(gameName)
        dbRows = self.db.get_all_rows(gameName)
        return {
            _id: Session(game, fieldValues) for _id, fieldValues in dbRows.items()
        }

    def get_session_by_id(self, gameName: str, sessionId: str):
        sessions = self.get_sessions(gameName, filter=None)
        return sessionId in sessions and sessions[sessionId]

    def edit_session(self, gameName: str, sessionId: str, newValues: Dict[str, Any]):
        session = self.get_session_by_id(gameName, sessionId)
        if not session:
            return
        game = self.construct_game_from_db(gameName)

        updatedNewValues = dict(session.get_values())
        updatedNewValues.update(newValues)
        newSession = Session(game, updatedNewValues)
        return self.add_session(newSession, _id=sessionId)

    def delete_session(self, gameName: str, sessionId: str):
        return self.db.delete_row(gameName, sessionId)
