import unittest
import datetime

from definitions import FieldDefinition, FieldType, DefaultFieldNames, \
                    Game, GameName, Session


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
        Game(GameName.TEXAS_HOLDEM)
        Game(GameName.TEXAS_HOLDEM, fieldDefs)

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


class TestSession(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.defaultGame = Game(GameName.TEXAS_HOLDEM)
        cls.gameWithAllFieldsRequired = Game(GameName.TEXAS_HOLDEM, [
            FieldDefinition(DefaultFieldNames.NET_EARN, FieldType.NUMBER, required=True),
            FieldDefinition(DefaultFieldNames.DATE, FieldType.DATE, required=True),
            FieldDefinition(DefaultFieldNames.LENGTH, FieldType.NUMBER, required=True),
            FieldDefinition(DefaultFieldNames.TAGS, FieldType.LIST, required=True),
            FieldDefinition(DefaultFieldNames.NOTE, FieldType.TEXT, required=True),
        ])
        cls.gameWithNoFieldsRequired = Game(GameName.TEXAS_HOLDEM, [
            FieldDefinition(DefaultFieldNames.NET_EARN, FieldType.NUMBER),
        ])

    # Test Case: Session.__init__ should accept input in expected type, str type or None/missing if not required
    def test_init_type_tolerance(self):

        # should accept expected type values
        expectedTypeValues = {
            DefaultFieldNames.NET_EARN: 10,
            DefaultFieldNames.DATE: datetime.date.today(),
            DefaultFieldNames.LENGTH: 10,
            DefaultFieldNames.TAGS: ['TAG1'],
            DefaultFieldNames.NOTE: 'NOTE',
        }
        Session(self.defaultGame, expectedTypeValues)

        # should accept values provided in string
        strTypeValues = {
            DefaultFieldNames.NET_EARN: '10',
            DefaultFieldNames.DATE: '2012/08/01', # Only YYYY/MM/DD tested
            DefaultFieldNames.LENGTH: '10.2',
            DefaultFieldNames.TAGS: "TAG1, TAG2", # Only CSV tested
            DefaultFieldNames.NOTE: 'NOTE',
        }
        Session(self.defaultGame, strTypeValues)

        # should accept missing and None for non-required fields
        noneTypeValues = {
            DefaultFieldNames.DATE: None,
            DefaultFieldNames.LENGTH: None,
        }
        Session(self.gameWithNoFieldsRequired, noneTypeValues)

    # Test Case: Session.__init__ should typecheck inputs, including those in str type
    def test_init_typecheck(self):

        # should reject inputs with unexpected type
        unexpectedTypeValues = { DefaultFieldNames.NET_EARN: datetime.date.today() }
        self.assertRaises(TypeError, Session,
            self.defaultGame, unexpectedTypeValues)

        # should reject inputs without all required types
        missingRequiredValues = {
            DefaultFieldNames.NET_EARN: 10,
            DefaultFieldNames.DATE: '2021/12/22',
        }
        self.assertRaises(TypeError, Session,
            self.gameWithAllFieldsRequired, missingRequiredValues)

        # should reject str inputs which do not parse into expected type
        self.assertRaises(TypeError, Session,
            self.gameWithNoFieldsRequired, { DefaultFieldNames.NET_EARN: 'six dollars' })
        self.assertRaises(TypeError, Session,
            self.gameWithNoFieldsRequired, { DefaultFieldNames.DATE: 'tomorrow' })

    # Test Case: Session.__init__ should convert inputs in str type to correct type
    def test_init_type_conversion(self):
        strTypeValues = {
            DefaultFieldNames.NET_EARN: '10',
            DefaultFieldNames.DATE: '2012/08/01', # Only YYYY/MM/DD tested
            DefaultFieldNames.LENGTH: '10.2',
            DefaultFieldNames.TAGS: "TAG1, TAG2", # Only CSV tested
            DefaultFieldNames.NOTE: 'NOTE',
        }
        session = Session(self.defaultGame, strTypeValues)
        self.assertEqual(session.fieldValues[DefaultFieldNames.NET_EARN], 10)
        self.assertEqual(session.fieldValues[DefaultFieldNames.DATE], datetime.datetime(2012, 8, 1))
        self.assertEqual(session.fieldValues[DefaultFieldNames.LENGTH], 10.2)

    # Test Case: Session.__init__ should reject special illegal values
    def test_init_illegal_values(self):
        illegalNumberValues = { DefaultFieldNames.NET_EARN: 'NaN' }
        self.assertRaises(TypeError, Session,
            self.defaultGame, illegalNumberValues)
