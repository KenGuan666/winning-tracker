# Note: DO NOT directly modify any attributes of any objects
# If no getter/setter is provided, consider the attribute as Private

import datetime
from typing import Any
from .constants import FieldType, DatabaseKeys, DISALLOWED_NUMBER_INPUTS


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
                    try:
                        datetime.datetime.strptime(value, '%Y-%m-%d')
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


def is_disallowed_number_str(value):
    return isinstance(value, str) and value.lower() in DISALLOWED_NUMBER_INPUTS
