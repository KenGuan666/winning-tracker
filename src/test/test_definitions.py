import unittest
from definitions import FieldDefinition, FieldType, DefaultFieldNames, \
                    Game, GameName


class TestFieldDefinition(unittest.TestCase):

    def test_init(self):
        fieldName = 'fieldName'
        FieldDefinition(fieldName, FieldType.NUMBER)
        FieldDefinition(fieldName, FieldType.DATE)
        FieldDefinition(fieldName, FieldType.TEXT)
        FieldDefinition(fieldName, FieldType.LIST)
        self.assertRaises(TypeError, FieldDefinition, fieldName, 'int')


class TestGameDefinition(unittest.TestCase):

    def test_init(self):
        fieldDefs = [FieldDefinition('field', FieldType.NUMBER)]
        game = Game(GameName.TEXAS_HOLDEM, fieldDefs)

        # Type-check Game's init params because one may pass List[str] by mistake
        self.assertRaises(TypeError, Game, GameName.TEXAS_HOLDEM, ['field'])

    def test_populate_default_fields(self):
        fieldDefs = [FieldDefinition('field', FieldType.NUMBER)]
        game = Game(GameName.TEXAS_HOLDEM, fieldDefs)

        expectedFields = [f.as_dict() for f in fieldDefs]
        expectedFields.extend([f.as_dict() for f in Game.DefaultFields])
        self.assertCountEqual([f.as_dict() for f in game.fields], expectedFields)

    def test_no_duplicate_fields(self):
        customFields = [
            FieldDefinition(DefaultFieldNames.TAGS, FieldType.TEXT),
            FieldDefinition('People', FieldType.LIST)
        ]
        game = Game(GameName.TEXAS_HOLDEM, customFields)

        # The newly defined custom field overwrites default definition of 'Tags'
        expectedFields = [f.as_dict() for f in [
            FieldDefinition(DefaultFieldNames.NET_EARN, FieldType.NUMBER, required=True),
            FieldDefinition(DefaultFieldNames.DATE, FieldType.DATE),
            FieldDefinition(DefaultFieldNames.LENGTH, FieldType.NUMBER),
            FieldDefinition(DefaultFieldNames.TAGS, FieldType.TEXT),
            FieldDefinition(DefaultFieldNames.NOTE, FieldType.TEXT),
            FieldDefinition('People', FieldType.LIST)
        ]]
        self.assertCountEqual([f.as_dict() for f in game.fields], expectedFields)
