import operator
from decimal import Decimal
from datetime import datetime, date

__all__ = ('ContextToken', 'LogicalToken', 'ExpressionToken', 'LimitToken')


registered_token_types = {
    'context': {'open', 'close'},
    'logical': {'and', 'or'},
    'expression': {'field', 'value_type', 'value'},
    'limit': {'start', 'end'}
}

class Token:
    def __init__(self, literal, primary_type, secondary_type):
        if primary_type not in registered_token_types or secondary_type not in registered_token_types[primary_type]:
            import ipdb; ipdb.set_trace()
            raise Exception('Attempted to tokenize an unregistered primary/secondary type')
        
        self.literal = literal
        self.primary_type = primary_type
        self.secondary_type = secondary_type
        self.string_notation = f'{primary_type}:{secondary_type}'
    
    def set_string_notation(self):
        self.string_notation = f'{self.primary_type}:{self.secondary_type}'
    
    def update_secondary_type(self, new_secondary_type):
        self.secondary_type = new_secondary_type
        self.set_string_notation()
    
    def __str__(self):
        return self.string_notation


class ContextToken(Token):
    def __init__(self, literal, secondary_type):
        super().__init__(literal, 'context', secondary_type)

class LimitToken(Token):
    def __init__(self, literal, secondary_type):
        super().__init__(literal, 'limit', secondary_type)


token_operator = {'and': operator.and_, 'or': operator.or_}
token_precedence = {'and': 2, 'or': 1}

class LogicalToken(Token):
    def __init__(self, literal, secondary_type):
        super().__init__(literal, 'logical', secondary_type)
        self.precedence = token_precedence[self.secondary_type]
        self.operator = token_operator[self.secondary_type]

value_types = {
    'int': int,
    'str': str,
    'float': float,
    'decimal': Decimal,
    'date': date,
    'datetime': datetime
}
    
class ExpressionToken(Token):
    def __init__(self, literal, secondary_type):
        super().__init__(literal, 'expression', secondary_type)

    def get_field_and_lookup_expression(self):
        if not self.secondary_type == 'field':
            return None
        
        splitted_field = self.literal.split('__')
        splitted_count = len(splitted_field)
        if splitted_count == 1:
            lookup_expression = 'eq'
        elif splitted_count in [2, 3]:
            lookup_expression = splitted_field[-1]
        else:
            raise Exception('Invalid lookup expression!')
        
        return splitted_field[0], lookup_expression
    
    def get_value_type_casting_method(self):
        if not self.secondary_type == 'value_type':
            return None
        
        try:
            return value_types[self.literal]
        except KeyError:
            raise Exception('Invalid value type!')
        
