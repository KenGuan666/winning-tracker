from .configs import useExchangeRatesAPI

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

class CustomFieldNames:
    CURRENCY = 'Currency'
    OCCASION = 'Occasion'
    PEOPLE = 'People'

class DatabaseKeys:
    SCHEMA_KEY = 'SCHEMA_DEFINITION'
    SCHEMA_TYPE_KEY = 'SCHEMA_TYPE'
    SCHEMA_REQUIRED_KEY = 'SCHEMA_REQUIRED'
    ROWS_KEY = 'ROWS'

class ConversionRateFieldNames:
    RMB_CONVERSION_RATE = 'RMB_CONVERSION_RATE'
    RATE = 'RATE'
    COLLECTION_TIME = 'COLLECTION_TIME'

class Currencies:
    CNY = 'CNY'
    USD = 'USD'

DISALLOWED_NUMBER_INPUTS = [
    'nan',
    'inf',
    'infinity',
]

if useExchangeRatesAPI:
    from .api_key import exchangeRatesAPIKey
    EXCHANGE_RATE_URL = f'http://api.exchangeratesapi.io/v1/latest?access_key={exchangeRatesAPIKey}'
DEFAULT_RMB_EXCHANGE_RATE = 6.4
