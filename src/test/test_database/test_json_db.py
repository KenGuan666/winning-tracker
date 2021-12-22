import unittest
import os
import json

from database import JSONDatabase
from definitions import FieldDefinition, GameName, FieldType, DatabaseKeys


test_filename = 'test_filename.json'

class JSONDatabaseTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.json_db = JSONDatabase()
        cls.json_db.DEFAULT_DB_FILENAME = test_filename
    
    @classmethod
    def tearDownClass(cls):
        os.remove(test_filename)

class TestDBSanity(JSONDatabaseTests):

    # Test Case: db.read_data_to_memory
    def test_read_data_to_memory(self):
        payload_txt = """{ "key": "value" }"""
        
        with open(test_filename, 'w') as f:
            f.write(payload_txt)

        loaded_data = self.json_db.read_data_to_memory()
        self.assertEqual(loaded_data, { 'key': 'value' })

    # Test Case: db.write_data_to_disk
    def test_write_data_to_disk(self):
        payload_json = { 'key': 'value' }
        self.json_db.write_data_to_disk(payload_json)
        with open(test_filename) as f:
            self.assertEqual(json.load(f), payload_json)

    # Test Case: db.reset_database
    def test_reset_database(self):
        self.json_db.reset_database()
        self.assertDictEqual(self.json_db.read_data_to_memory(), {})


class TestTableAPI(JSONDatabaseTests):

    # Test Case: db.get_all_table_names
    def test_get_all_table_names(self):
        db_state_text = """{ 
            "Texas Hold'em": {},
            "Age of Empires IV": {}
        }"""
        with open(test_filename, 'w') as f:
            f.write(db_state_text)

        all_games = self.json_db.get_all_table_names()
        self.assertCountEqual(all_games, [GameName.TEXAS_HOLDEM, GameName.AOE4])

    # Test Case:db.create_table
    def test_create_table(self):
        before_state_text = """{ 
            "Texas Hold'em": {},
            "Age of Empires IV": {}
        }"""
        with open(test_filename, 'w') as f:
            f.write(before_state_text)

        schema = {
            'people': {
                DatabaseKeys.SCHEMA_TYPE_KEY: FieldType.LIST,
                DatabaseKeys.SCHEMA_REQUIRED_KEY: False
            }
        }
        success = self.json_db.create_table(GameName.PLO, schema)
        self.assertTrue(success)
        expected_state_json = {
            GameName.TEXAS_HOLDEM: {},
            GameName.AOE4: {},
            GameName.PLO: { DatabaseKeys.SCHEMA_KEY: schema }
        }
        self.assertDictEqual(self.json_db.read_data_to_memory(), expected_state_json)

        # Cannot create duplicate Games
        success =  self.json_db.create_table(GameName.PLO, schema)
        self.assertFalse(success)
        self.assertDictEqual(self.json_db.read_data_to_memory(), expected_state_json)

    # Test Case: db.get_table_schema
    def test_get_table_schema(self):
        schema = {
            'people': {
                DatabaseKeys.SCHEMA_TYPE_KEY: FieldType.LIST,
                DatabaseKeys.SCHEMA_REQUIRED_KEY: False
            }
        }
        self.json_db.create_table(GameName.PLO, schema)

        self.assertRaises(ValueError, self.json_db.get_table_schema, "non-existing table")
        fieldDefinitions = self.json_db.get_table_schema(GameName.PLO)
        self.assertEqual(len(fieldDefinitions), 1)

        self.assertDictEqual(fieldDefinitions[0].as_dict(), schema)


class TestRowAPI(JSONDatabaseTests):

    # Test Case:db.insert_row
    def test_insert_row(self):

        # Set up state before db.insert_row
        schema = { 
            'Net Earn': {
                DatabaseKeys.SCHEMA_TYPE_KEY: FieldType.NUMBER,
                DatabaseKeys.SCHEMA_REQUIRED_KEY: True
            },
            'Length': {
                DatabaseKeys.SCHEMA_TYPE_KEY: FieldType.NUMBER,
                DatabaseKeys.SCHEMA_REQUIRED_KEY: True
            },
            'Notes': {
                DatabaseKeys.SCHEMA_TYPE_KEY: FieldType.TEXT,
                DatabaseKeys.SCHEMA_REQUIRED_KEY: False
            }
        }
        before_state_json = { 
            GameName.TEXAS_HOLDEM: {
                DatabaseKeys.SCHEMA_KEY: schema,
                DatabaseKeys.ROWS_KEY: {
                    '00dde7a1f1fd4be99d4a5c252b035811': [10, 2]
                }
            },
            GameName.PLO: {
                DatabaseKeys.SCHEMA_KEY: schema,
                DatabaseKeys.ROWS_KEY: {
                    'd459a6d3b1c9479488e48f51470cf0ff': [-3, 1]
                }
            }
        }
        self.json_db.write_data_to_disk(before_state_json)

        # db.insert_row
        uuidTexas = self.json_db.insert_row(GameName.TEXAS_HOLDEM, {
            'Net Earn': 7,
            'Length': 0.5
        })
        self.assertTrue(uuidTexas)
        uuidPLO = self.json_db.insert_row(GameName.PLO, {
            'Net Earn': 8,
            'Length': 3
        })
        self.assertTrue(uuidPLO)

        # Should reach expected state after db.insert_row
        expected_state_json = { 
            GameName.TEXAS_HOLDEM: {
                DatabaseKeys.SCHEMA_KEY: schema,
                DatabaseKeys.ROWS_KEY: {
                    '00dde7a1f1fd4be99d4a5c252b035811': [10, 2],
                    uuidTexas: [7, 0.5]
                }
            },
            GameName.PLO: {
                DatabaseKeys.SCHEMA_KEY: schema,
                DatabaseKeys.ROWS_KEY: {
                    'd459a6d3b1c9479488e48f51470cf0ff': [-3, 1],
                    uuidPLO: [8, 3]
                }
            }
        }
        self.assertDictEqual(self.json_db.read_data_to_memory(), expected_state_json)

        self.assertRaises(TypeError, self.json_db.insert_row, GameName.TEXAS_HOLDEM, { 'Net Earn': '7', 'Length': 0.5 })
        self.assertRaises(TypeError, self.json_db.insert_row, GameName.TEXAS_HOLDEM, { 'Net Earn': 7, 'Length': "1:00" })
        self.assertRaises(ValueError, self.json_db.insert_row, GameName.TEXAS_HOLDEM, { 'Net Earn': 7 })
        self.assertDictEqual(self.json_db.read_data_to_memory(), expected_state_json)

        # Should fail db.insert_row with invalid value schema
        self.assertFalse(self.json_db.insert_row(GameName.AOE4, {}))
        self.assertFalse(self.json_db.insert_row(GameName.AOE4, {
            'Net Earn': '8',
            'Length': 3
        }))

    # Test Case:db.delete_row
    def test_delete_row(self):

        # Set up state before db.delete_row
        schema = { 
            'Net Earn': {
                DatabaseKeys.SCHEMA_TYPE_KEY: FieldType.NUMBER,
                DatabaseKeys.SCHEMA_REQUIRED_KEY: True
            },
            'Length': {
                DatabaseKeys.SCHEMA_TYPE_KEY: FieldType.NUMBER,
                DatabaseKeys.SCHEMA_REQUIRED_KEY: True
            }
        }
        uuid_hex = 'bdd5e2dadef144c5807cca942c6c0be7'
        before_state_json = { 
            GameName.TEXAS_HOLDEM: {
                DatabaseKeys.SCHEMA_KEY: schema,
                DatabaseKeys.ROWS_KEY: {
                    uuid_hex: [11, 2],
                    '00dde7a1f1fd4be99d4a5c252b035811': [10, 2]
                }
            }
        }
        self.json_db.write_data_to_disk(before_state_json)

        # db.delete_row
        success =  self.json_db.delete_row(GameName.TEXAS_HOLDEM, uuid_hex)
        self.assertTrue(success)

        # Should reach expected state after db.delete_row
        expected_state_json = { 
            GameName.TEXAS_HOLDEM: {
                DatabaseKeys.SCHEMA_KEY: schema,
                DatabaseKeys.ROWS_KEY: {
                    '00dde7a1f1fd4be99d4a5c252b035811': [10, 2]
                }
            }
        }
        self.assertDictEqual(self.json_db.read_data_to_memory(), expected_state_json)

        # Should fail db.delete_row with incorrect Game name or uuid
        self.assertFalse(self.json_db.delete_row(GameName.PLO, uuid_hex))
        self.assertFalse(self.json_db.delete_row(GameName.TEXAS_HOLDEM, 'df3b813ef8364bee8468612c95bf6b0f'))
        self.assertDictEqual(self.json_db.read_data_to_memory(), expected_state_json)


if __name__ == '__main__':
    unittest.main()