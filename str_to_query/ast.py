
# build AST
from copy import deepcopy
from .Token import *
from .Node import *

def build_ast(instanced_tokens):
    contexts_stack = [{'head': None, 'last_node': None, 'last_logical': None}]
    current_expression_tokens = []

    # instanced_tokens.append(None)  # End
    for tok in instanced_tokens:
        
        if isinstance(tok, ContextToken):
            if tok.secondary_type == 'open':
                contexts_stack.append({'head': None, 'last_node': None, 'last_logical': None})
            elif tok.secondary_type == 'close':
                if not contexts_stack:
                    raise Exception('Attempted to close unexistent context!')

                if current_expression_tokens:
                    try:
                        expression_node = ExpressionNode(*current_expression_tokens)
                        current_expression_tokens = []
                    except Exception as e:
                        raise Exception(f'Couldn\'t parse expression node! -> {e}')

                    node_to_add = deepcopy(expression_node)
                    if contexts_stack[-1]['head'] == None:
                        contexts_stack[-1]['head'] = node_to_add
                    elif isinstance(contexts_stack[-1]['last_node'], LogicalNode):
                        contexts_stack[-1]['last_node'].right_child = node_to_add
                    else:
                        raise Exception('Found an unexpected expression??')
                    
                    expression_node = None
                    contexts_stack[-1]['last_node'] = node_to_add

    #             else:
    #             import ipdb; ipdb.set_trace()
                context_to_merge = contexts_stack.pop()
                if contexts_stack[-1]['head'] == None:
                    contexts_stack[-1]['head'] = context_to_merge['head']
                elif isinstance(contexts_stack[-1]['last_node'], LogicalNode):
                    contexts_stack[-1]['last_node'].right_child = context_to_merge['head']
                contexts_stack[-1]['last_node'] = context_to_merge['head']
        
        elif isinstance(tok, LogicalToken):
    #         if contexts_stack[-1]['last_logical'].precedence <
    #         import ipdb;ipdb.set_trace()
    #         print('test')
            logical_node = LogicalNode(tok)
            try:
                logical_node.left_child = contexts_stack[-1]['last_node']
            except:
                raise Exception('No previous node for logical operator!')
            if contexts_stack[-1]['last_node'] == contexts_stack[-1]['head']:
                contexts_stack[-1]['head'] = logical_node
            else:
                contexts_stack[-1]['last_logical'].right_child = logical_node
        
            contexts_stack[-1]['last_node'] = logical_node
            contexts_stack[-1]['last_logical'] = logical_node

        elif isinstance(tok, ExpressionToken):
            current_expression_tokens.append(tok)            
                


    if not len(contexts_stack) == 1:
        raise Exception('Unexpected end of string')
    
    return contexts_stack[0]['head']