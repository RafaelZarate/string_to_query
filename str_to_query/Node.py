from .Token import ExpressionToken


__all__ = ('ExpressionNode', 'LogicalNode')

class Node:
    uid = 0
    def __init__(self, left_child=None, right_child=None):
        self.left_child = left_child
        self.right_child = right_child
        Node.uid +=1
        self._uid = Node.uid

class ExpressionNode(Node):
    def __init__(self, *args):
        
        if len(args) not in [2, 3]:
            raise Exception(f'Couldn\'t build ExpressionNode! Tokens -> {args}')
        
        field_token = args[0]
        value_token = args[-1]
        value_type_token = args[1] if len(args) == 3 else None
            
        if any(not isinstance(tok, ExpressionToken) for tok in [field_token, value_token]):
            raise Exception('Cannot build expression node out of non ExpressionTokens!')
        
        field, lookup_expression = field_token.get_field_and_lookup_expression()
        self.field = field
        self.lookup_expression = lookup_expression
        
#         import ipdb; ipdb.set_trace
        value_type = None if not value_type_token else value_type_token.get_value_type_casting_method()
        self.value = value_type(value_token.literal) if value_type else value_token.literal
        super().__init__()
        
class LogicalNode(Node):
    def __init__(self, logical_token):
        self.operator = logical_token.operator
        super().__init__()
