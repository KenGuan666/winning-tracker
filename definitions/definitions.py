import datetime
from typing import ClassVar, List

class FieldDefinition:

    common_name_to_accepted_types : ClassVar[List[str]] = {
        'number': [int, float],
        'date': [datetime.date],
        'text': [str],
        'list': [list]
    }

    def __init__(self, fieldName: str, fieldType: str, required: bool=False):
        if fieldType not in FieldDefinition.common_name_to_accepted_types:
            raise TypeError(f'{fieldType} is not an accepted type.')
        self.fieldName = fieldName
        self.fieldType = fieldType
        self.required = required
