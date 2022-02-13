# Class definitions
# Define objects used by both Backend and Client

# Note: DO NOT directly modify any attributes of any objects
# If no getter/setter is provided, consider the attribute as Private

import datetime
import uuid
from typing import List, Dict, Any
from .constants import FieldType, DefaultFieldNames, DatabaseKeys, \
    DISALLOWED_NUMBER_INPUTS


"""
    FieldDefinition defines a field as an attribute of a Game
    User defines the fields while creating a new Game
         and enters values for the fields while recording a Session
    DO NOT directly modify any attributes after init

    Attributes:
    - fieldName: str : Display name
    - fieldType: str : The type of input accepted. Allowed types are listed in CommonNameToAcceptedTypes
    - required: bool : Whether field is required for every Session
"""
class FieldDefinition:

    CommonNameToAcceptedTypes = {
        FieldType.NUMBER: [int, float],
        FieldType.DATE: [str],
        FieldType.TEXT: [str],
        FieldType.LIST: [list]
    }

    def __init__(self, fieldName: str, fieldType: str, required: bool=False):
        if fieldType not in FieldDefinition.CommonNameToAcceptedTypes:
            raise TypeError(f'{fieldType} is not an accepted type.')
        self.fieldName : str = fieldName
        self.fieldType : str = fieldType
        self.required : bool= required

    def get_field_name(self):
        return self.fieldName

    def is_required(self):
        return self.required

    def as_dict(self):
        return {
            self.fieldName: {
                DatabaseKeys.SCHEMA_TYPE_KEY: self.fieldType,
                DatabaseKeys.SCHEMA_REQUIRED_KEY: self.required,
            }
        }

    def raise_incompatible_type_error(self, value):
        raise TypeError(f'{value} is incompatible with type f{self.fieldType}')

    # Check if value is an appropriate entry
    def parse_entry(self, value: Any):

        # handle None value, regardless of type
        if value is None:
            if self.required:
                raise TypeError(f'{self.fieldName} is required but None is provided')
            return None

        # handle TEXT type
        if self.fieldType == FieldType.TEXT:
            if not isinstance(value, str):
                self.raise_incompatible_type_error(value)
            return value

        # handle NUMBER type
        if self.fieldType == FieldType.NUMBER:
            if is_disallowed_number_str(value):
                self.raise_incompatible_type_error(value)
            try:
                return float(value)
            except:
                self.raise_incompatible_type_error(value)

        # handle DATE type
        if self.fieldType == FieldType.DATE:
            if isinstance(value, datetime.date):
                str_value = str(value)
            else:
                str_value = value
                try:
                    datetime.datetime.strptime(value, '%Y/%m/%d')
                except:
                    self.raise_incompatible_type_error(value)
            return str_value.split(' ')[0]

        # handle LIST type
        if self.fieldType == FieldType.LIST:
            if isinstance(value, list) or isinstance(value, tuple):
                return value
            if isinstance(value, str):
                return value.split(',')
            self.raise_incompatible_type_error(value)

        raise TypeError('unknown FieldDefinition type, please do not modify objects directly')


"""
    Game represents a game user records sessions for. Examples: Texas Hold'em, PLO
    DO NOT directly modify any attributes after init

    Attributes:
    - name: str : Display name
    - fields: List[FieldDefinition] : The fields user may record under each Session for this Game
"""
class Game:

    DefaultFields = [
        FieldDefinition(DefaultFieldNames.NET_EARN, FieldType.NUMBER, required=True),
        FieldDefinition(DefaultFieldNames.DATE, FieldType.DATE),
        FieldDefinition(DefaultFieldNames.LENGTH, FieldType.NUMBER),
        FieldDefinition(DefaultFieldNames.TAGS, FieldType.LIST),
        FieldDefinition(DefaultFieldNames.NOTE, FieldType.TEXT)
    ]

    def __init__(self, name: str, fields: List[FieldDefinition]=None):
        self.name = name
        self.fields = list(Game.DefaultFields)
        for field in fields or []:
            if not isinstance(field, FieldDefinition):
                raise TypeError("parameter was not wrapped in FieldDefinition type")
        
            # If field already exists, remove the field
            index, existingField = self.find_field_definition_by_name(field.get_field_name())
            if existingField:
                self.fields.pop(index)
            
            self.fields.append(field)

    def get_name(self):
        return self.name

    def all_fields_as_dict(self):
        res = {}
        for field in self.fields:
            res.update(field.as_dict())
        return res

    # Finds FieldDefinition by fieldName
    # Input: fieldName: str, name of field to lookup
    # Output: (index, FieldDefinition object), or (None, None) if not found
    # TODO: Optimize performance by rewriting self.fields as Dict
    def find_field_definition_by_name(self, fieldName: FieldDefinition):
        for index, existingField in enumerate(self.fields):
            if existingField.get_field_name() == fieldName:
                return index, existingField
        return (None, None)

    # Gets name of all required fields
    # Output: name of all required fields in a Python set
    def get_required_fieldNames(self):
        fieldNames = set()
        for index, existingField in enumerate(self.fields):
            if existingField.is_required():
                fieldNames.add(existingField.get_field_name())
        return fieldNames

    # Validates whether values passed are legal values for the FieldDefinitions
    # Parses str format entries into expected format
    # Throws TypeError if validation fails
    def parse_field_values(self, fieldValues: Dict[str, Any]):
        fieldNamesPassed = set(fieldValues.keys())
        requiredFieldsNotPassed = self.get_required_fieldNames() - fieldNamesPassed
        if requiredFieldsNotPassed:
            raise TypeError(f'required fields not provided: {list(requiredFieldsNotPassed)}')

        for fieldName, fieldValue in fieldValues.items():
            _, existingField = self.find_field_definition_by_name(fieldName)
            if existingField:
                fieldValues[fieldName] = existingField.parse_entry(fieldValue)
        return fieldValues


"""
    Session represents the values user enters into a Session record
    Performs type check on user values entered
    DO NOT directly modify any attributes after init

    Attributes:
    - game: Game : The Game user records Session for
    - values: Dict[str, <expectedType>] : The field values user enters
"""
class Session:

    def __init__(self, game: Game, values: Dict[str, Any]):
        self.game = game
        self.fieldValues = game.parse_field_values(values)

    def get_game(self):
        return self.game

    def get_values(self):
        return self.fieldValues

    def equals(self, otherSession: 'Session'):
        if isinstance(otherSession, Session):
            return self.game.get_name() == otherSession.game.get_name() and \
                self.fieldValues == otherSession.fieldValues
        return False


def is_disallowed_number_str(value):
    return isinstance(value, str) and value.lower() in DISALLOWED_NUMBER_INPUTS
