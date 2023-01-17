import json
import uuid
from typing import List, Dict, Any

from .abstract_database import Database
from definitions import FilterOperator, FilterCondition, VisualizeFilters, \
    FieldDefinition, DatabaseKeys


DEFAULT_DB_FILENAME = 'json_database.json'

"""
A JSON-based Database implementation
Representation:
{
    TableName1: {
        DatabaseKeys.SCHEMA_KEY: {
            columnName1: {
                SCHEMA_TYPE_KEY: number,
                SCHEMA_REQUIRED_KEY: True
            },
            columnName2: { ... }
            ...
        },
        ROWS_KEY: {
            uuid1.hex: {
                columnName1: ...,
                columnName2: ...,
            },
            uuid2.hex: { ... }
            ...
        }
    },
    TableName2: {
        ...
    }, ...
}
"""
class JSONDatabase(Database):

    def __init__(self, filename=None):
        self.filename = filename or DEFAULT_DB_FILENAME

    def reset_database(self):
        self.write_data_to_disk({})

    def read_data_to_memory(self) -> Dict[str, Dict]:
        try:
            with open(self.filename) as f:
                return json.load(f)
        except:
            return {}

    def write_data_to_disk(self, data: Dict[str, Dict]):
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)

    def get_all_table_names(self):
        data = self.read_data_to_memory()
        return list(data.keys())

    """
    Creates a new table in the db
    Returns True if successful
    """
    def create_table(self, tableName: str, columns: Dict[str, Dict[str, str]]) -> bool:
        data = self.read_data_to_memory()
        if tableName in data:
            return False
        data[tableName] = { 
            DatabaseKeys.SCHEMA_KEY: dict(columns),
            DatabaseKeys.ROWS_KEY: {},
        }
        self.write_data_to_disk(data)
        return True

    def get_table_schema(self, tableName: str) -> List[FieldDefinition]:
        data = self.read_data_to_memory()
        if tableName not in data:
            raise ValueError(f'table {tableName} does not exist')
        schema = data[tableName][DatabaseKeys.SCHEMA_KEY]

        return [
            FieldDefinition(fieldName, 
                            fieldType=schemaDict[DatabaseKeys.SCHEMA_TYPE_KEY], 
                            required=schemaDict[DatabaseKeys.SCHEMA_REQUIRED_KEY]
            ) for (fieldName, schemaDict) in schema.items()
        ]

    """
    Verify whether the input value against schema
    Raises exception if illegal
    """
    def verify_schema(self, tableSchema: Dict[str, Dict[str, str]], values: Dict[str, Any]) -> None:

        for fieldName, properties in tableSchema.items():
            if fieldName in values and values[fieldName] is not None:
                passedType = type(values[fieldName])
                requiredTypes = FieldDefinition.CommonNameToAcceptedTypes[properties[DatabaseKeys.SCHEMA_TYPE_KEY]]
                if passedType not in requiredTypes:
                    raise TypeError(f'field {fieldName} is not in {str(requiredTypes)}')
            elif properties[DatabaseKeys.SCHEMA_REQUIRED_KEY]:
                raise ValueError(f'required field {fieldName} is not present')

    """
    Creates a new entry under tableName
    Caller may specify a uuid for the entry
    Returns uuid if successful
    """
    def insert_row(self, tableName: str, values: Dict[str, Any], _id=None) -> bool:
        data = self.read_data_to_memory()
        if tableName not in data:
            return
        schema = data[tableName][DatabaseKeys.SCHEMA_KEY]
        self.verify_schema(schema, values)

        if not _id:
            _id = uuid.uuid4().hex
            while _id in data[tableName][DatabaseKeys.ROWS_KEY]:
                _id = uuid.uuid4().hex
        data[tableName][DatabaseKeys.ROWS_KEY][_id] = values
        self.write_data_to_disk(data)
        return _id

    """
    Deletes an entry under tableName
    Returns True if successful
    """
    def delete_row(self, tableName: str, _id: str) -> bool:
        data = self.read_data_to_memory()
        if tableName not in data:
            return
        rows = data[tableName][DatabaseKeys.ROWS_KEY]
        if _id not in rows:
            return
        del rows[_id]
        self.write_data_to_disk(data)
        return True

    """
    Returns all entries under tableName
    Returns None if tableName doesn't exist
    """
    def get_all_rows(self, tableName: str) -> Dict[str, Dict[str, Any]]:
        data = self.read_data_to_memory()
        if tableName not in data:
            return
        return data[tableName][DatabaseKeys.ROWS_KEY]

    """
    Constructs a filter function which returns True
        when applied to rows satisfying a FilterCondition

    Example: func = self.get_filter_function(_filter: NET_EARN GREATER than 5)
    func(row WHERE NET_EARN = 6)
    >>> True
    func(row WHERE NET_EARN = 4)
    >>> False
    """
    def get_single_filter_function(self, columnKey: str, filterCondition: FilterCondition):
        if filterCondition.operator == FilterOperator.EQUAL:
            f = lambda entry: \
                filterCondition.operand is None and columnKey not in entry or \
                columnKey in entry and entry[columnKey] == filterCondition.operand
        elif filterCondition.operator == FilterOperator.GREATER:
            f = lambda entry: \
                columnKey in entry and entry[columnKey] > filterCondition.operand
        elif filterCondition.operator == FilterOperator.LESS:
            f = lambda entry: \
                columnKey in entry and entry[columnKey] < filterCondition.operand
        else: #filterCondition.operator == FilterOperator.CONTAINS
            f = lambda entry: \
                columnKey in entry and filterCondition.operand in entry[columnKey]

        return lambda entry: filterCondition.negate != f(entry)

    """
    Constructs a filter function which returns True
        when applied to rows which satisfy all FilterConditions in VisualizeFilter
    """
    def get_filter_function(self, _filter: VisualizeFilters):
        filterFuncs = [lambda _: True]
        if _filter:
            for columnKey, filterConditions in _filter.filters.items():
                for filterCondition in filterConditions:
                    filterFuncs.append(self.get_single_filter_function(columnKey, filterCondition))
        return lambda entry: all([f(entry) for f in filterFuncs])


    """
    Returns all entries under tableName which satisfy the filter conditions
    """
    def get_rows_with_filter(self, tableName: str, _filter: VisualizeFilters):
        allRows = self.get_all_rows(tableName)
        if not allRows:
            return
        filterFunction = self.get_filter_function(_filter)
        return {
            _id: entry for _id, entry in allRows.items() \
                if filterFunction(entry)
        }
