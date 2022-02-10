import json
import uuid
from typing import List, Dict, Any

from .abstract_database import Database
from definitions import FieldDefinition, DatabaseKeys


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
    
    DEFAULT_DB_FILENAME = 'json_database.json'

    def reset_database(self):
        self.write_data_to_disk({})

    def read_data_to_memory(self) -> Dict[str, Dict]:
        try:
            with open(self.DEFAULT_DB_FILENAME) as f:
                return json.load(f)
        except:
            return {}

    def write_data_to_disk(self, data: Dict[str, Dict]):
        with open(self.DEFAULT_DB_FILENAME, 'w') as f:
            json.dump(data, f)

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
    or None if tableName doesn't exist
    """
    def get_all_rows(self, tableName: str) -> Dict[str, Dict[str, Any]]:
        data = self.read_data_to_memory()
        if tableName not in data:
            return
        return data[tableName][DatabaseKeys.ROWS_KEY]
