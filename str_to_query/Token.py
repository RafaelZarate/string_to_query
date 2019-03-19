import operator
from decimal import Decimal
from datetime import datetime, date

__all__ = ('ContextToken', 'LogicalToken', 'ExpressionToken', 'LimitToken')


class Token:
    REGISTERED_TOKEN_TYPES = {
        'context': {'open', 'close'},
        'logical': {'and', 'or'},
        'expression': {'field', 'value_type', 'value'},
        'limit': {'start', 'end'}
    }

    def __init__(self, literal, primary_type, secondary_type):
        if (
            primary_type not in Token.REGISTERED_TOKEN_TYPES
            or secondary_type not in Token.REGISTERED_TOKEN_TYPES[primary_type]
        ):
            raise Exception(
                'Attempted to tokenize an unregistered primary/secondary type. Literal value: '
                f'{literal}, primary_type: {primary_type}, secondary_type: {secondary_type}.'
            )
        
        self.literal = literal
        self.primary_type = primary_type
        self.secondary_type = secondary_type
        self.string_notation = f'{primary_type}:{secondary_type}'
    
    def __str__(self):
        return self.string_notation


class ContextToken(Token):
    def __init__(self, literal, secondary_type):
        super().__init__(literal, 'context', secondary_type)


class LimitToken(Token):
    def __init__(self, literal, secondary_type):
        super().__init__(literal, 'limit', secondary_type)


class LogicalToken(Token):
    TOKEN_OPERATOR = {'and': operator.and_, 'or': operator.or_}
    TOKEN_PRECEDENCE = {'and': 2, 'or': 1}

    def __init__(self, literal, secondary_type):
        super().__init__(literal, 'logical', secondary_type)
        self.precedence = LogicalToken.TOKEN_PRECEDENCE[self.secondary_type]
        self.operator = LogicalToken.TOKEN_OPERATOR[self.secondary_type]


class ExpressionToken(Token):
    VALID_VALUE_TYPES = {
        'int': int,
        'str': str,
        'float': float,
        'decimal': Decimal,
        # Not yet implemented
        # 'date': date,
        # 'datetime': datetime
    }

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
            return ExpressionToken.VALID_VALUE_TYPES[self.literal]
        except KeyError:
            raise Exception('Invalid value type!')
