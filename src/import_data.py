import openpyxl
import string

from backend import Backend
from definitions import GameName, FieldDefinition, FieldType, Session, DefaultFieldNames, CustomFieldNames

backend = None
dataSheet = None
game = None


def read_sheet_from_excel(filePath: str=''):
    filePath = filePath or 'C:/Users/17gua/Desktop/poker stuff/Lifetime Winning.xlsx'
    wb = openpyxl.load_workbook(filePath, data_only=True)
    return wb.active

def read_data_sheet(column: str, row: int):
    return dataSheet[column + str(row)].value

def get_neighbor_column(column: str, _dir: int) -> str:
    if _dir not in (1, -1):
        raise NotImplementedError('can only fetch neighbor one column away')
    if len(column) == 2:
        neighbor = column[0] + chr(ord(column[1]) + _dir)
    else:
        neighbor = chr(ord(column) + _dir)
    specialCaseDict = {
        chr(ord('Z') + 1): 'AA',
        'A' + chr(ord('A') - 1): 'Z'
    }
    return specialCaseDict[neighbor] if neighbor in specialCaseDict else neighbor

def get_column_occasion(column: str):
    return read_data_sheet(column, 1)

def parse_global_entries(column: str) -> None:
    occasion = get_column_occasion(column)
    currency = 'USD'
    prevCol = get_neighbor_column(column, -1)
    nextCol = get_neighbor_column(column, 1)
    nextNextCol = get_neighbor_column(nextCol, 1)

    # Add row for unrecorded sessions
    backend.add_session(Session(
        game,
        {
            DefaultFieldNames.NET_EARN: read_data_sheet(column, 7) + read_data_sheet(nextCol, 7),
            DefaultFieldNames.NOTE: 'Unrecorded sessions',
            CustomFieldNames.CURRENCY: currency,
            CustomFieldNames.OCCASION: occasion
        }
    ))
    row = 8
    date = None
    while read_data_sheet(nextCol, row) is not None:
        withdrawnDiff = read_data_sheet(column, row)
        accountDiff = read_data_sheet(nextCol, row)
        netEarn = (withdrawnDiff or 0) + accountDiff
        date = read_data_sheet(prevCol, row) or date
        note = read_data_sheet(nextNextCol, row)

        tags = []
        if withdrawnDiff is not None:
            if withdrawnDiff > 0 and accountDiff < 0:
                tags.append('Withdraw')
            elif withdrawnDiff < 0 and accountDiff > 0:
                tags.append('Purchase')
            else:
                raise ValueError(f'incorrect data at row {row}')
        backend.add_session(Session(
            game,
            {
                DefaultFieldNames.NET_EARN: netEarn,
                DefaultFieldNames.DATE: date,
                DefaultFieldNames.NOTE: note,
                DefaultFieldNames.TAGS: tags,
                CustomFieldNames.CURRENCY: currency,
                CustomFieldNames.OCCASION: occasion
            }
        ))
        row += 1

def parse_normal_entries(column: str) -> None:
    occasion = get_column_occasion(column)
    currency = 'RMB' if 'RMB' in occasion else 'USD'
    prevCol = get_neighbor_column(column, -1)
    nextCol = get_neighbor_column(column, 1)
    
    row = 5
    while read_data_sheet(column, row) is not None:
        netEarn = read_data_sheet(column, row)
        date = read_data_sheet(prevCol, row)
        note = read_data_sheet(nextCol, row)
        backend.add_session(Session(
            game,
            {
                DefaultFieldNames.NET_EARN: netEarn,
                DefaultFieldNames.DATE: date,
                DefaultFieldNames.NOTE: note,
                CustomFieldNames.CURRENCY: currency,
                CustomFieldNames.OCCASION: occasion
            }
        ))
        row += 1


def import_data_to_db():
    global dataSheet
    dataSheet = read_sheet_from_excel()

    parse_global_entries('F')
    normalEntryColumn = 'J'
    while get_column_occasion(normalEntryColumn):
        parse_normal_entries(normalEntryColumn)
        for _ in range(3):
            normalEntryColumn = get_neighbor_column(normalEntryColumn, 1)


# Overwrites default database with imported data
def import_legacy_data():
    global backend, game
    backend = Backend()
    backend.reset_database()

    fields = [
        FieldDefinition(CustomFieldNames.OCCASION, FieldType.TEXT, required=True),
        FieldDefinition(CustomFieldNames.PEOPLE, FieldType.LIST),
        FieldDefinition(CustomFieldNames.CURRENCY, FieldType.TEXT, required=True)
    ]
    game = backend.add_game(GameName.TEXAS_HOLDEM, fields)
    import_data_to_db()

if __name__ == '__main__':
    import_legacy_data()
