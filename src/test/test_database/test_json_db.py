import unittest
import os
import json

from database import JSONDatabase
from definitions import FieldDefinition, GameName, FieldType, \
    DatabaseKeys, DefaultFieldNames, \
    VisualizeFilters, FilterCondition, FilterOperator


test_filename = 'test_filename.json'

class JSONDatabaseTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.json_db = JSONDatabase(filename=test_filename)

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
        before_state_text = "{}"
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
        expectedStateJson = {
            GameName.PLO: {
                DatabaseKeys.SCHEMA_KEY: schema,
                DatabaseKeys.ROWS_KEY: {},
            }
        }
        self.assertDictEqual(self.json_db.read_data_to_memory(), expectedStateJson)

        # Cannot create duplicate Games
        success =  self.json_db.create_table(GameName.PLO, schema)
        self.assertFalse(success)
        self.assertDictEqual(self.json_db.read_data_to_memory(), expectedStateJson)

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

    def setUp(self):
        self.schema = {
            DefaultFieldNames.NET_EARN: {
                DatabaseKeys.SCHEMA_TYPE_KEY: FieldType.NUMBER,
                DatabaseKeys.SCHEMA_REQUIRED_KEY: True
            },
            DefaultFieldNames.LENGTH: {
                DatabaseKeys.SCHEMA_TYPE_KEY: FieldType.NUMBER,
                DatabaseKeys.SCHEMA_REQUIRED_KEY: True
            },
            DefaultFieldNames.NOTE: {
                DatabaseKeys.SCHEMA_TYPE_KEY: FieldType.TEXT,
                DatabaseKeys.SCHEMA_REQUIRED_KEY: False
            },
            DefaultFieldNames.TAGS: {
                DatabaseKeys.SCHEMA_TYPE_KEY: FieldType.LIST,
                DatabaseKeys.SCHEMA_REQUIRED_KEY: False
            }
        }
        self.texasHoldemHex = '00dde7a1f1fd4be99d4a5c252b035811'
        self.ploHex = 'd459a6d3b1c9479488e48f51470cf0ff'
        beforeStateJson = {
            GameName.TEXAS_HOLDEM: {
                DatabaseKeys.SCHEMA_KEY: self.schema,
                DatabaseKeys.ROWS_KEY: {
                    self.texasHoldemHex: {
                        DefaultFieldNames.NET_EARN: 10,
                        DefaultFieldNames.LENGTH: 2,
                    }
                }
            },
            GameName.PLO: {
                DatabaseKeys.SCHEMA_KEY: self.schema,
                DatabaseKeys.ROWS_KEY: {
                    self.ploHex: {
                        DefaultFieldNames.NET_EARN: -3,
                        DefaultFieldNames.LENGTH: 1,
                    }
                }
            }
        }
        self.json_db.write_data_to_disk(beforeStateJson)

    # Test Case:db.insert_row
    def test_insert_row(self):

        # db.insert_row
        uuidTexas = self.json_db.insert_row(GameName.TEXAS_HOLDEM, {
            DefaultFieldNames.NET_EARN: 7,
            DefaultFieldNames.LENGTH: 0.5
        })
        self.assertTrue(uuidTexas)
        uuidPLO = self.json_db.insert_row(GameName.PLO, {
            DefaultFieldNames.NET_EARN: 8,
            DefaultFieldNames.LENGTH: 3
        })
        self.assertTrue(uuidPLO)

        # Should reach expected state after db.insert_row
        expectedStateJson = {
            GameName.TEXAS_HOLDEM: {
                DatabaseKeys.SCHEMA_KEY: self.schema,
                DatabaseKeys.ROWS_KEY: {
                    self.texasHoldemHex: {
                        DefaultFieldNames.NET_EARN: 10,
                        DefaultFieldNames.LENGTH: 2,
                    },
                    uuidTexas: {
                        DefaultFieldNames.NET_EARN: 7,
                        DefaultFieldNames.LENGTH: 0.5,
                    }
                }
            },
            GameName.PLO: {
                DatabaseKeys.SCHEMA_KEY: self.schema,
                DatabaseKeys.ROWS_KEY: {
                    self.ploHex: {
                        DefaultFieldNames.NET_EARN: -3,
                        DefaultFieldNames.LENGTH: 1,
                    },
                    uuidPLO: {
                        DefaultFieldNames.NET_EARN: 8,
                        DefaultFieldNames.LENGTH: 3,
                    }
                }
            }
        }
        self.assertDictEqual(self.json_db.read_data_to_memory(), expectedStateJson)

        # Should fail db.insert_row with invalid value schema
        self.assertRaises(TypeError, self.json_db.insert_row, GameName.TEXAS_HOLDEM, { DefaultFieldNames.NET_EARN: '7', DefaultFieldNames.LENGTH: 0.5 })
        self.assertRaises(TypeError, self.json_db.insert_row, GameName.TEXAS_HOLDEM, { DefaultFieldNames.NET_EARN: 7, DefaultFieldNames.LENGTH: "1:00" })
        self.assertRaises(ValueError, self.json_db.insert_row, GameName.TEXAS_HOLDEM, { DefaultFieldNames.NET_EARN: 7 })
        self.assertDictEqual(self.json_db.read_data_to_memory(), expectedStateJson)

        # Should fail db.insert_row with incorrect table name
        self.assertFalse(self.json_db.insert_row(GameName.AOE4, {}))
        self.assertFalse(self.json_db.insert_row(GameName.AOE4, {
            DefaultFieldNames.NET_EARN: '8',
            DefaultFieldNames.LENGTH: 3
        }))

    # Test Case:db.delete_row
    def test_delete_row(self):

        # db.delete_row
        success = self.json_db.delete_row(GameName.TEXAS_HOLDEM, self.texasHoldemHex)
        self.assertTrue(success)

        # Should reach expected state after db.delete_row
        expectedStateJson = {
            GameName.TEXAS_HOLDEM: {
                DatabaseKeys.SCHEMA_KEY: self.schema,
                DatabaseKeys.ROWS_KEY: {}
            },
            GameName.PLO: {
                DatabaseKeys.SCHEMA_KEY: self.schema,
                DatabaseKeys.ROWS_KEY: {
                    self.ploHex: {
                        DefaultFieldNames.NET_EARN: -3,
                        DefaultFieldNames.LENGTH: 1,
                    }
                }
            }
        }
        self.assertDictEqual(self.json_db.read_data_to_memory(), expectedStateJson)

        # Should fail db.delete_row with incorrect Game name or uuid
        self.assertFalse(self.json_db.delete_row(GameName.PLO, self.texasHoldemHex))
        self.assertFalse(self.json_db.delete_row(GameName.TEXAS_HOLDEM, 'd459a6d3b1c9479488e48f51470cf0ff'))
        self.assertDictEqual(self.json_db.read_data_to_memory(), expectedStateJson)

    # Test Case: db.get_all_rows
    def test_get_all_rows(self):

        # insert a few more rows
        uuid1 = self.json_db.insert_row(GameName.TEXAS_HOLDEM, {
            DefaultFieldNames.NET_EARN: 7,
            DefaultFieldNames.LENGTH: 0.5
        })
        uuid2 = self.json_db.insert_row(GameName.TEXAS_HOLDEM, {
            DefaultFieldNames.NET_EARN: 8,
            DefaultFieldNames.LENGTH: 3
        })

        expectedAllRows = {
            self.texasHoldemHex: {
                DefaultFieldNames.NET_EARN: 10,
                DefaultFieldNames.LENGTH: 2,
            },
            uuid1: {
                DefaultFieldNames.NET_EARN: 7,
                DefaultFieldNames.LENGTH: 0.5,
            },
            uuid2: {
                DefaultFieldNames.NET_EARN: 8,
                DefaultFieldNames.LENGTH: 3,
            }
        }

        self.assertDictEqual(self.json_db.get_all_rows(GameName.TEXAS_HOLDEM), expectedAllRows)

        # should fail db.get_all_rows on incorrect Game
        self.assertFalse(self.json_db.get_all_rows(GameName.AOE4))

    # Test Case: db.get_rows_with_filter
    def test_get_rows_with_filter(self):

        # insert a few more rows
        uuid1 = self.json_db.insert_row(GameName.TEXAS_HOLDEM, {
            DefaultFieldNames.NET_EARN: 9,
            DefaultFieldNames.LENGTH: 2,
            DefaultFieldNames.NOTE: 'note1',
            DefaultFieldNames.TAGS: ['tag1', 'tag2']
        })
        uuid2 = self.json_db.insert_row(GameName.TEXAS_HOLDEM, {
            DefaultFieldNames.NET_EARN: 8,
            DefaultFieldNames.LENGTH: 1,
            DefaultFieldNames.NOTE: 'note2',
            DefaultFieldNames.TAGS: ['tag2', 'tag3']
        })
        uuid3 = self.json_db.insert_row(GameName.TEXAS_HOLDEM, {
            DefaultFieldNames.NET_EARN: 7,
            DefaultFieldNames.LENGTH: 1,
            DefaultFieldNames.NOTE: 'note3',
            DefaultFieldNames.TAGS: ['tag3', 'tag4']
        })
        uuid4 = self.json_db.insert_row(GameName.TEXAS_HOLDEM, {
            DefaultFieldNames.NET_EARN: -1,
            DefaultFieldNames.LENGTH: 1,
            DefaultFieldNames.NOTE: 'note1',
            DefaultFieldNames.TAGS: ['tag1', 'tag2', 'tag4']
        })

        # should act like get_all_rows if no filter provided
        expectedKeys = [self.texasHoldemHex, uuid1, uuid2, uuid3, uuid4]
        self.assertCountEqual(self.json_db.get_rows_with_filter(GameName.TEXAS_HOLDEM, _filter=None), expectedKeys)

        # should apply GREATER, EQUAL and LESS on number and strings
        filters = VisualizeFilters({
            DefaultFieldNames.NET_EARN: [FilterCondition(FilterOperator.GREATER, 8)]
        })
        expectedKeys = [self.texasHoldemHex, uuid1]
        self.assertCountEqual(self.json_db.get_rows_with_filter(GameName.TEXAS_HOLDEM, _filter=filters), expectedKeys)

        filters = VisualizeFilters({
            DefaultFieldNames.LENGTH: [FilterCondition(FilterOperator.LESS, 1.5)]
        })
        expectedKeys = [uuid2, uuid3, uuid4]
        self.assertCountEqual(self.json_db.get_rows_with_filter(GameName.TEXAS_HOLDEM, _filter=filters), expectedKeys)

        filters = VisualizeFilters({
            DefaultFieldNames.NOTE: [FilterCondition(FilterOperator.GREATER, 'note1')]
        })
        expectedKeys = [uuid2, uuid3]
        self.assertCountEqual(self.json_db.get_rows_with_filter(GameName.TEXAS_HOLDEM, _filter=filters), expectedKeys)

        # should apply CONTAINS and list and strings
        filters = VisualizeFilters({
            DefaultFieldNames.NOTE: [FilterCondition(FilterOperator.CONTAINS, 'note')]
        })
        expectedKeys = [uuid1, uuid2, uuid3, uuid4]
        self.assertCountEqual(self.json_db.get_rows_with_filter(GameName.TEXAS_HOLDEM, _filter=filters), expectedKeys)

        filters = VisualizeFilters({
            DefaultFieldNames.TAGS: [FilterCondition(FilterOperator.CONTAINS, 'tag1')]
        })
        expectedKeys = [uuid1, uuid4]
        self.assertCountEqual(self.json_db.get_rows_with_filter(GameName.TEXAS_HOLDEM, _filter=filters), expectedKeys)

        # should apply negate
        filters = VisualizeFilters({
            DefaultFieldNames.NET_EARN: [FilterCondition(FilterOperator.GREATER, 8, negate=True)]
        })
        expectedKeys = [uuid2, uuid3, uuid4]
        self.assertCountEqual(self.json_db.get_rows_with_filter(GameName.TEXAS_HOLDEM, _filter=filters), expectedKeys)

        filters = VisualizeFilters({
            DefaultFieldNames.TAGS: [FilterCondition(FilterOperator.CONTAINS, 'tag1', negate=True)]
        })
        expectedKeys = [self.texasHoldemHex, uuid2, uuid3]
        self.assertCountEqual(self.json_db.get_rows_with_filter(GameName.TEXAS_HOLDEM, _filter=filters), expectedKeys)

        # should apply multiple filters
        filters = VisualizeFilters({
            DefaultFieldNames.NET_EARN: [FilterCondition(FilterOperator.GREATER, 7)],
            DefaultFieldNames.TAGS: [FilterCondition(FilterOperator.CONTAINS, 'tag2')]
        })
        expectedKeys = [uuid1, uuid2]
        self.assertCountEqual(self.json_db.get_rows_with_filter(GameName.TEXAS_HOLDEM, _filter=filters), expectedKeys)

        filters = VisualizeFilters({
            DefaultFieldNames.NET_EARN: [
                FilterCondition(FilterOperator.LESS, 10),
                FilterCondition(FilterOperator.GREATER, 7)
            ]
        })
        expectedKeys = [uuid1, uuid2]
        self.assertCountEqual(self.json_db.get_rows_with_filter(GameName.TEXAS_HOLDEM, _filter=filters), expectedKeys)

if __name__ == '__main__':
    unittest.main()
