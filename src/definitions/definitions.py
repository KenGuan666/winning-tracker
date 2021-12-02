import datetime
from typing import List
from .constants import FieldType, DefaultFieldNames


class FieldDefinition:

    CommonNameToAcceptedTypes = {
        FieldType.NUMBER: [int, float],
        FieldType.DATE: [datetime.date],
        FieldType.TEXT: [str],
        FieldType.LIST: [list]
    }

    def __init__(self, fieldName: str, fieldType: str, required: bool=False):
        if fieldType not in FieldDefinition.CommonNameToAcceptedTypes:
            raise TypeError(f'{fieldType} is not an accepted type.')
        self.fieldName = fieldName
        self.fieldType = fieldType
        self.required = required

    def as_dict(self):
        return {
            'fieldName': self.fieldName,
            'fieldType': self.fieldType,
            'required': self.required
        }


class Game:

    DefaultFields = [
        FieldDefinition(DefaultFieldNames.NET_EARN, FieldType.NUMBER, required=True),
        FieldDefinition(DefaultFieldNames.DATE, FieldType.DATE),
        FieldDefinition(DefaultFieldNames.LENGTH, FieldType.NUMBER),
        FieldDefinition(DefaultFieldNames.TAGS, FieldType.LIST),
        FieldDefinition(DefaultFieldNames.NOTE, FieldType.TEXT)
    ]

    def __init__(self, name: str, fields: List[FieldDefinition]):
        self.name = name
        self.fields = list(Game.DefaultFields)
        for field in fields:
            if not isinstance(field, FieldDefinition):
                raise TypeError("parameter was not wrapped in FieldDefinition type")
            
            # If field already exists, remove the field
            for index, existingField in enumerate(self.fields):
                if existingField.fieldName == field.fieldName:
                    self.fields.pop(index)
                    break
            
            self.fields.append(field)
