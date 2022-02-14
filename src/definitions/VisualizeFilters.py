from typing import Any, Dict, List

import enum


class FilterOperator(enum.Enum):
    GREATER = '1'
    LESS = '2'
    EQUAL = '3'
    CONTAINS = '4'


class FilterCondition:

    def __init__(self, operator: FilterOperator, operand: Any, negate: bool=False):

        self.verify_operand_type(operator, operand)
        self.operator = operator
        self.operand = operand
        self.negate = negate
    
    # throws TypeError if type is incompatible
    def verify_operand_type(self, operator: FilterOperator, operand: Any):
        
        # can perform all operations on str
        if isinstance(operand, str):
            return

        if isinstance(operand, int) or isinstance(operand, float):
            if operator in (FilterOperator.GREATER, FilterOperator.LESS, FilterOperator.EQUAL):
                return
        
        if isinstance(operand, list):
            if operator is FilterOperator.CONTAINS:
                return

        raise TypeError(f'operator {operator.value} is incompatible with operand {operand}')


class VisualizeFilters:

    def __init__(self, filters: Dict[str, List[FilterCondition]]):
        self.filters = filters
