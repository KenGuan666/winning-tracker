
class GameName:
    TEXAS_HOLDEM = "Texas Hold'em"
    AOE4 = 'Age of Empires IV'
    PLO = 'Pot Limit Omaha'

class FieldType:
    NUMBER = 'number'
    DATE = 'date'
    TEXT = 'text'
    LIST = 'list'

class DefaultFieldNames:
    NET_EARN = 'Net Earn'
    DATE = 'Date'
    LENGTH = 'Length'
    TAGS = 'Tags'
    NOTE = 'Note'

class DatabaseKeys:
    SCHEMA_KEY = 'SCHEMA_DEFINITION'
    SCHEMA_TYPE_KEY = 'SCHEMA_TYPE'
    SCHEMA_REQUIRED_KEY = 'SCHEMA_REQUIRED'
    ROWS_KEY = 'ROWS'

DISALLOWED_NUMBER_INPUTS = [
    'nan',
    'inf',
    'infinity',
]
