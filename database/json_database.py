from .abstract_database import Database
from typing import List, Dict, Any
from definitions import FieldDefinition

import json
import uuid


"""
A JSON-based Database implementation
Representation:
{
    TableName1: {
        SCHEMA_KEY: {
            columnName: {
                'type': number,
                'required': True
            },
            columnName: { ... }
            ...
        },
        ROWS_KEY: {
            uuid1.hex: [column1, column2, ...],
            uuid2.hex: [column1, column2, ...]
        }
    },
    TableName2: {
        ...
    }, ...
}
"""
class JSONDatabase(Database):
    
    DEFAULT_DB = 'json_database.json'
    SCHEMA_KEY = 'TABLE_SCHEMA_DEFINITION'
    ROWS_KEY = 'ROWS'

    def read_data_to_memory(self) -> Dict[str, Dict]:
        try:
            with open(self.DEFAULT_DB) as f:
                return json.load(f)
        except:
            return {}

    def write_data_to_disk(self, data: Dict[str, Dict]):
        with open(self.DEFAULT_DB, 'w') as f:
            json.dump(data, f)

    def get_all_table_names(self):
        data = self.read_data_to_memory()
        return list(data.keys())

    """
    Creates a new key-value pair in the db
    Check response to see if successful
    """
    def create_table(self, tableName: str, columns: Dict[str, Dict[str, str]]) -> bool:
        data = self.read_data_to_memory()
        if tableName in data:
            return False
        data[tableName] = { self.SCHEMA_KEY: dict(columns) }
        self.write_data_to_disk(data)
        return True

    """
    Verify whether the input value against schema
    Raises exception if illegal
    """
    def verify_schema(self, tableSchema: Dict[str, Dict[str, str]], values: Dict[str, Any]):
        return

    """
    Creates a new entry under tableName
    Check response to see if successful
    """
    def insert_row(self, tableName: str, values: Dict[str, Any]):
        data = self.read_data_to_memory()
        if tableName not in data:
            return
        schema = data[tableName][self.SCHEMA_KEY]
        self.verify_schema(schema, values)

        _id = uuid.uuid4().hex
        data[tableName][self.ROWS_KEY][_id] = list(values.values())
        self.write_data_to_disk(data)
        return _id

    """
    Deletes a new key-value pair in the db
    Check response to see if successful
    """
    def delete_row(self, tableName: str, _id: str):
        data = self.read_data_to_memory()
        if tableName not in data:
            return
        rows = data[tableName][self.ROWS_KEY]
        if _id not in rows:
            return
        del rows[_id]
        self.write_data_to_disk(data)
        return True
