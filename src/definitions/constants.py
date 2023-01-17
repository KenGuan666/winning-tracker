from .configs import useExchangeRatesAPI

class GameName:
    TEXAS_HOLDEM = "TEXAS HOLD'EM"
    AOE4 = 'AOE4'
    PLO = 'PLO'

class FieldType:
    NUMBER = 'NUMBER'
    DATE = 'DATE'
    TEXT = 'TEXT'
    LIST = 'LIST'

class DefaultFieldNames:
    NET_EARN = 'NET EARN'
    DATE = 'DATE'
    LENGTH = 'LENGTH'
    TAGS = 'TAGS'
    NOTE = 'NOTE'

class CustomFieldNames:
    CURRENCY = 'CURRENCY'
    OCCASION = 'OCCASION'
    PEOPLE = 'PEOPLE'

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
