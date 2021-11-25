import unittest
from definitions import FieldDefinition

class TestFieldDefinition(unittest.TestCase):

    def test_init(self):
        fieldName = 'fieldName'
        FieldDefinition(fieldName, 'number')
        FieldDefinition(fieldName, 'date')
        FieldDefinition(fieldName, 'text')
        FieldDefinition(fieldName, 'list')
        self.assertRaises(TypeError, FieldDefinition, fieldName, 'int')
