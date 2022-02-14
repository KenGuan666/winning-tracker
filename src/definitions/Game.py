# Note: DO NOT directly modify any attributes of any objects
# If no getter/setter is provided, consider the attribute as Private

from typing import List, Dict, Any
from .constants import FieldType, DefaultFieldNames
from .FieldDefinition import FieldDefinition

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

