import datetime
from typing import List, Dict, Any

from database import Database, JSONDatabase
from definitions import Game, FieldDefinition, Session, \
    DatabaseKeys, FieldType, ConversionRateFieldNames, Currencies, \
    useExchangeRatesAPI, EXCHANGE_RATE_URL, DEFAULT_RMB_EXCHANGE_RATE

from .utils import get_json_from_url

class Backend:

    def __init__(self, db: Database=JSONDatabase, dbFileName=None):
        self.db = db(filename=dbFileName)
        self.init_conversion_rate_cache()

    def reset_database(self):
        self.db.reset_database()
        self.init_conversion_rate_cache()

    def init_conversion_rate_cache(self):
        # No-op if the table already exists
        self.db.create_table(ConversionRateFieldNames.RMB_CONVERSION_RATE, {
            ConversionRateFieldNames.RATE: {
                DatabaseKeys.SCHEMA_TYPE_KEY: FieldType.NUMBER,
                DatabaseKeys.SCHEMA_REQUIRED_KEY: True
            },
            ConversionRateFieldNames.COLLECTION_TIME: {
                DatabaseKeys.SCHEMA_TYPE_KEY: FieldType.DATE,
                DatabaseKeys.SCHEMA_REQUIRED_KEY: True
            }
        })

    def add_game(self, name: str, fields: List[FieldDefinition]) -> Game:
        # Game init may throw error on incorrect field type
        game = Game(name, fields)
        created = self.db.create_table(name, game.all_fields_as_dict())
        return created and game

    def get_all_games(self) -> List[str]:
        allTables = self.db.get_all_table_names()
        allTables.remove(ConversionRateFieldNames.RMB_CONVERSION_RATE)
        return allTables

    def add_session(self, session: Session, _id=None) -> str:
        # Game must already exists in db
        return self.db.insert_row(session.game.get_name(), session.get_values(), _id=_id)

    def construct_game_from_db(self, gameName: str) -> Game:
        dbSchema = self.db.get_table_schema(gameName)
        return Game(gameName, dbSchema)

    def get_sessions(self, gameName: str, _filter) -> Dict[str, Session]:

        game = self.construct_game_from_db(gameName)
        dbRows = self.db.get_rows_with_filter(gameName, _filter)
        return {
            _id: Session(game, fieldValues) for _id, fieldValues in dbRows.items()
        }

    def get_session_by_id(self, gameName: str, sessionId: str):
        sessions = self.get_sessions(gameName, _filter=None)
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

    def get_conversion_rate_from_cache(self):
        cachedDbRows = self.db.get_all_rows(ConversionRateFieldNames.RMB_CONVERSION_RATE).values()
        if len(cachedDbRows):
            cachedDbEntry = list(cachedDbRows)[0]
            rate, date = cachedDbEntry[ConversionRateFieldNames.RATE], cachedDbEntry[ConversionRateFieldNames.COLLECTION_TIME]
            if date == str(datetime.date.today()):
                return rate

    def get_conversion_rate_from_api(self):
        res = get_json_from_url(EXCHANGE_RATE_URL)
        if res:
            CNYRate = res['rates'][Currencies.CNY]
            USDRate = res['rates'][Currencies.USD]
            return CNYRate / USDRate

    def cache_exchange_rate(self, rate):
        cachedDbRows = self.db.get_all_rows(ConversionRateFieldNames.RMB_CONVERSION_RATE)
        for uuid in cachedDbRows:
            self.db.delete_row(ConversionRateFieldNames.RMB_CONVERSION_RATE, uuid)
        self.db.insert_row(ConversionRateFieldNames.RMB_CONVERSION_RATE, {
            ConversionRateFieldNames.RATE: rate,
            ConversionRateFieldNames.COLLECTION_TIME: str(datetime.date.today())
        })

    def get_rmb_conversion_rate(self):
        cachedRate = self.get_conversion_rate_from_cache()
        urlRate = None
        if cachedRate:
            return cachedRate
        if useExchangeRatesAPI:
            urlRate = self.get_conversion_rate_from_api()
        returnRate = urlRate if urlRate else DEFAULT_RMB_EXCHANGE_RATE
        self.cache_exchange_rate(returnRate)
        return returnRate
