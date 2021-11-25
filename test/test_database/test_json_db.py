import unittest
import os
import json
from database import JSONDatabase
from definitions import *

test_filename = 'test_filename.json'

class JSONDatabaseTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.json_db = JSONDatabase()
        cls.json_db.DEFAULT_DB = test_filename
        with open(test_filename, 'w') as f:
            f.write('{}')
    
    @classmethod
    def tearDownClass(cls):
        os.remove(test_filename)

class TestDBSanity(JSONDatabaseTests):

    def test_load(self):
        payload_txt = """{ "key": "value" }"""
        
        with open(test_filename, 'w') as f:
            f.write(payload_txt)

        loaded_data = self.json_db.read_data_to_memory()
        self.assertEqual(loaded_data, {
            'key': 'value'
        })

    def test_dump(self):
        payload_json = { 'key': 'value' }
        self.json_db.write_data_to_disk(payload_json)
        with open(test_filename) as f:
            self.assertEqual(json.load(f), payload_json)


class TestTableAPI(JSONDatabaseTests):
    
    def test_get_all_table_names(self):
        db_state_text = """{ 
            "Texas Hold'em": {},
            "Age of Empires IV": {}
        }"""
        with open(test_filename, 'w') as f:
            f.write(db_state_text)

        all_games = self.json_db.get_all_table_names()
        self.assertCountEqual(all_games, [TEXAS_HOLDEM, AOE4])

    def test_create_table(self):
        before_state_text = """{ 
            "Texas Hold'em": {},
            "Age of Empires IV": {}
        }"""
        with open(test_filename, 'w') as f:
            f.write(before_state_text)

        schema = {
            'people': {
                'type': 'list',
                'required': False
            }
        }
        success =  self.json_db.create_table(PLO, schema)
        self.assertTrue(success)
        expected_state_json = {
            TEXAS_HOLDEM: {},
            AOE4: {},
            PLO: {
                self.json_db.SCHEMA_KEY: schema
            }
        }
        self.assertDictEqual(self.json_db.read_data_to_memory(), expected_state_json)

        # Cannot create duplicate Games
        success =  self.json_db.create_table(PLO, schema)
        self.assertFalse(success)
        self.assertDictEqual(self.json_db.read_data_to_memory(), expected_state_json)


class TestRowAPI(JSONDatabaseTests):
    
    def test_insert_row_standard(self):
        schema = { 
            'Net Earn': {
                'type': 'number',
                'required': True
            },
            'Length': {
                'type': 'number',
                'required': True
            }
        }
        before_state_json = { 
            TEXAS_HOLDEM: {
                self.json_db.SCHEMA_KEY: schema,
                self.json_db.ROWS_KEY: {
                    '00dde7a1f1fd4be99d4a5c252b035811': [10, 2]
                }
            },
            PLO: {
                self.json_db.SCHEMA_KEY: schema,
                self.json_db.ROWS_KEY: {
                    'd459a6d3b1c9479488e48f51470cf0ff': [-3, 1]
                }
            }
        }
        self.json_db.write_data_to_disk(before_state_json)

        uuidTexas = self.json_db.insert_row(TEXAS_HOLDEM, {
            'Net Earn': 7,
            'Length': 0.5
        })
        self.assertTrue(uuidTexas)
        uuidPLO = self.json_db.insert_row(PLO, {
            'Net Earn': 8,
            'Length': 3
        })
        self.assertTrue(uuidPLO)
        self.assertFalse(self.json_db.insert_row(AOE4, {}))

        expected_state_json = { 
            TEXAS_HOLDEM: {
                self.json_db.SCHEMA_KEY: schema,
                self.json_db.ROWS_KEY: {
                    '00dde7a1f1fd4be99d4a5c252b035811': [10, 2],
                    uuidTexas: [7, 0.5]
                }
            },
            PLO: {
                self.json_db.SCHEMA_KEY: schema,
                self.json_db.ROWS_KEY: {
                    'd459a6d3b1c9479488e48f51470cf0ff': [-3, 1],
                    uuidPLO: [8, 3]
                }
            }
        }
        self.assertDictEqual(self.json_db.read_data_to_memory(), expected_state_json)

    def test_insert_row_schema(self):
        pass

    def test_delete_row(self):
        schema = { 
            'Net Earn': {
                'type': 'number',
                'required': True
            },
            'Length': {
                'type': 'number',
                'required': True
            }
        }
        uuid_hex = 'bdd5e2dadef144c5807cca942c6c0be7'
        before_state_json = { 
            TEXAS_HOLDEM: {
                self.json_db.SCHEMA_KEY: schema,
                self.json_db.ROWS_KEY: {
                    uuid_hex: [11, 2],
                    '00dde7a1f1fd4be99d4a5c252b035811': [10, 2]
                }
            }
        }
        self.json_db.write_data_to_disk(before_state_json)

        success =  self.json_db.delete_row(TEXAS_HOLDEM, uuid_hex)
        self.assertTrue(success)
        expected_state_json = { 
            TEXAS_HOLDEM: {
                self.json_db.SCHEMA_KEY: schema,
                self.json_db.ROWS_KEY: {
                    '00dde7a1f1fd4be99d4a5c252b035811': [10, 2]
                }
            }
        }
        self.assertDictEqual(self.json_db.read_data_to_memory(), expected_state_json)

        # No effect if provided incorrect Game name or uuid
        success =  self.json_db.delete_row(PLO, uuid_hex)
        self.assertFalse(success)
        success =  self.json_db.delete_row(TEXAS_HOLDEM, 'df3b813ef8364bee8468612c95bf6b0f')
        self.assertFalse(success)
        self.assertDictEqual(self.json_db.read_data_to_memory(), expected_state_json)


if __name__ == '__main__':
    unittest.main()
