
# build AST
from copy import copy, deepcopy

from .Token import *
from .Node import *


class ASTBuilder:
    def __init__(self):
        self.empty_stack = {'head': None, 'last_node': None, 'last_logical': None}
        self.context_stack = []

    def _merge_contexts(self, node=None) -> None:
        """
        Merge current context with parent context. If node is passed, it adds the node
        to the current context
        :param node: If passed, it will be merged into current context
        :type node: Node
        :return: None
        :rtype: None
        """
        node = node or self.context_stack.pop()['head']
        current_context = self.context_stack[-1]
        if current_context['head'] == None:
            current_context['head'] = node
        elif isinstance(current_context['last_node'], LogicalNode):
            current_context['last_node'].right_child = node
        else:
            raise Exception('Unexpected token was found!')
        current_context['last_node'] = node

    def __call__(self, token_list) -> 'Node':
        """
        Builds AST out of list of tokens
        :param token_list: list of tokens
        :type token_list: list
        :return: head of AST
        :rtype: Node
        """
        self.context_stack = [copy(self.empty_stack)]  # set parent context (children should be merged)
        current_expression_tokens = []

        # token_list.append(None)  # End
        for token in token_list:
            if isinstance(token, ExpressionToken):
                current_expression_tokens.append(token)

            elif isinstance(token, ContextToken) and token.secondary_type == 'open':
                self.context_stack.append(copy(self.empty_stack))

            elif isinstance(token, ContextToken) and token.secondary_type == 'close':
                if not self.context_stack:
                    raise Exception('Attempted to close an unexistent context!')

                if current_expression_tokens:
                # Build ExpressionToken and merge it into current context
                    try:
                        expression_node = ExpressionNode(*current_expression_tokens)
                        current_expression_tokens = []
                    except Exception as e:
                        raise Exception(f'Couldn\'t parse expression node! -> {e}')

                    node_to_add = deepcopy(expression_node)
                    self._merge_contexts(node_to_add)

                # Merge head of current context with parent context
                self._merge_contexts()

            elif isinstance(token, LogicalToken):
                # if current_context['last_logical'].precedence < token.precendence
                #     do swap!
                current_context = self.context_stack[-1]
                logical_node = LogicalNode(token)
                try:
                    logical_node.left_child = current_context['last_node']
                except:
                    raise Exception('No previous node for logical operator!')
                if current_context['last_node'] == current_context['head']:
                    current_context['head'] = logical_node
                else:
                    current_context['last_logical'].right_child = logical_node

                current_context['last_node'] = logical_node
                current_context['last_logical'] = logical_node

        # Only original parent context should be left
        if not len(self.context_stack) == 1:
            raise Exception('Unexpected end of string!')

        return self.context_stack[0]['head']
