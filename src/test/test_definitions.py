import unittest

from definitions import FieldDefinition, FieldType, DefaultFieldNames, \
                    Game, GameName


class TestFieldDefinition(unittest.TestCase):

    # Test Case: FieldDefinition.__init__ should only allow selected FieldType
    def test_init(self):
        fieldName = 'fieldName'
        FieldDefinition(fieldName, FieldType.NUMBER)
        FieldDefinition(fieldName, FieldType.DATE)
        FieldDefinition(fieldName, FieldType.TEXT)
        FieldDefinition(fieldName, FieldType.LIST)
        self.assertRaises(TypeError, FieldDefinition, fieldName, 'int')


class TestGameDefinition(unittest.TestCase):

    # Test Case: Game.__init__ should check type of fields
    # because one may pass List[str] by mistake
    def test_init_typecheck(self):
        fieldDefs = [FieldDefinition('field', FieldType.NUMBER)]
        game = Game(GameName.TEXAS_HOLDEM, fieldDefs)

        self.assertRaises(TypeError, Game, GameName.TEXAS_HOLDEM, ['field'])

    # Test Case: Game.__init__ should auto-populate default fields
    def test_init_populate_default_fields(self):

        # Game.__init__
        fieldDefs = [FieldDefinition('field', FieldType.NUMBER)]
        game = Game(GameName.TEXAS_HOLDEM, fieldDefs)

        # Set up expected state
        expectedFields = fieldDefs[0].as_dict()
        for f in Game.DefaultFields:
            expectedFields.update(f.as_dict())

        # Check Game object against expected state
        self.assertDictEqual(game.all_fields_as_dict(), expectedFields)

    # Test Case: Game.__init__ should not repeat default fields if provided
    def test_init_no_duplicate_fields(self):

        # Game.__init__
        customFields = [
            FieldDefinition(DefaultFieldNames.TAGS, FieldType.TEXT),
            FieldDefinition('People', FieldType.LIST)
        ]
        game = Game(GameName.TEXAS_HOLDEM, customFields)

        # Set up expected state
        # The newly defined custom field overwrites default definition of 'Tags'
        expectedFields = {}
        for f in [
            FieldDefinition(DefaultFieldNames.NET_EARN, FieldType.NUMBER, required=True),
            FieldDefinition(DefaultFieldNames.DATE, FieldType.DATE),
            FieldDefinition(DefaultFieldNames.LENGTH, FieldType.NUMBER),
            FieldDefinition(DefaultFieldNames.TAGS, FieldType.TEXT),
            FieldDefinition(DefaultFieldNames.NOTE, FieldType.TEXT),
            FieldDefinition('People', FieldType.LIST)]:
            expectedFields.update(f.as_dict())

        # Check Game object against expected state
        self.assertDictEqual(game.all_fields_as_dict(), expectedFields)


class TestGameSessionFieldsDefinition(unittest.TestCase):

    # Test Case: GameSessionFields.__init__ should accept input in both correct and str type
    def test_init_type_tolerance(self):
        pass

    # Test Case: GameSessionFields.__init__ should typecheck inputs, including those in str type
    def test_init_str_typecheck(self):
        pass

    # Test Case: GameSessionFields.__init__ should convert inputs in str type to correct type
    def test_init_type_conversion(self):
        pass


class TestSessionDefinition(unittest.TestCase):

    # Test Case: Session.__init__ should create uuid
    def test_init(self):
        pass
