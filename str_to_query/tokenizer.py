import re

from .Token import *


class Tokenizer:
    def __init__(self):
        self.separators = ['\(', '\)', ':']
        self.substrings_to_ignore = {':', ''}
        self.general_token_types = {
            # These tokens are easily identifiable with the literal value
            '(': ('context', 'open'),
            ')': ('context', 'close'),
            'AND': ('logical', 'and'),
            'OR': ('logical', 'or')
        }
        self.expression_token_types = {
            # Expression token types are identified using the previous and next tokens
            # the previous token is used as key and the next token is used as the lambda param
            'limit:start': lambda _: 'field',
            'context:open': lambda _: 'field',
            'expression:field': lambda next_substring: 'value' if next_substring in [None, ')'] else 'value_type',
            'expression:value_type': lambda _: 'value'
        }
        self.primary_type_to_token = {
            'context': ContextToken,
            'logical': LogicalToken,
            'expression': ExpressionToken,
            'limit': LimitToken
        }
        self.expected_tokens = {
            # Possible next tokens based on previous token
            'limit:start': {'context:open', 'expression:field'},
            'context:open': {'context:open', 'expression:field'},
            'context:close': {'context:close', 'logical:and', 'logical:or'},
            'logical:and': {'context:open'},
            'logical:or': {'context:open'},
            'expression:field': {'expression:value_type', 'expression:value'},
            'expression:value_type': {'expression:value'},
            'expression:value': {'context:close'}
        } 

    def create_substrings(self, string: str) -> list:
        """
        Splits string into list of substrings that will then
        be tokenized
        :param string: string to be tokenized
        :type string: str
        :return: list of substrings
        :rtype: list
        """
        joined_separators = '|'.join(self.separators)
        compiled_re = re.compile(f'({joined_separators})')
        substrings = re.split(compiled_re, string)
        return substrings

    def preprocess_substrings(self, substrings: list) -> list:
        """
        General cleanup of the created subustrings. Two important
        processes are implemented:
        1) strip all tokens - remove whitespaces before and after
        2) remove all substrings that are empty or useless
        :param substrings: list of substring to preprocess
        :type substrings: list
        :return: cleaned list
        :rtype: list
        """
        stripped_substrings = [substr.strip() for substr in substrings]
        cleaned_substrings = filter(
            lambda substring: substring not in self.substrings_to_ignore,
            stripped_substrings
        )
        return list(cleaned_substrings)

    def get_token(self, current_substring: str, previous_token_repr: str, next_substring: str) -> 'Token':
        """
        Uses the necessary context (current literal, past token and next literal) to determine
        token type of the given current_substring.
        :param current_substring: substring whose token type is going to be determined
        :type current_substring: str
        :param previous_token_repr: string representation of previous token
        :type previous_token_repr: str
        :param next_substring: next substring
        :type next_substring: str
        :return: Token instance for the given current_substring
        :rtype: Token
        """
        try:
            primary_type, secondary_type = self.general_token_types[current_substring]
        except KeyError:
            try:
                primary_type = 'expression'
                secondary_type_lambda = self.expression_token_types[previous_token_repr]
                secondary_type = secondary_type_lambda(next_substring)
            except KeyError:
                raise Exception(
                    f'Couldn\'t determine token type!\nCurrent -> {current_substring}\n'
                    f'Previous -> {previous_token_repr}\nNext -> {next_substring}'
                )
        
        return self.primary_type_to_token[primary_type](current_substring, secondary_type)

    def __call__(self, string: str) -> list:
        """
        Tokenizes the received string
        :param string: string that will be tokenized
        :param string: str
        :return: list of tokens
        :rtype: list
        """
        raw_substrings = self.create_substrings(string)
        substrings = self.preprocess_substrings(raw_substrings)
        
        token_list = []
        previous_token_repr = str(LimitToken(None, 'start'))
        for index, current_substring in enumerate(substrings):
            try:
                next_substring = substrings[index+1]
            except IndexError:
                next_substring = None  # End of substrings -> None is the string expression of limit:end

            token = self.get_token(current_substring, previous_token_repr, next_substring)
            token_repr = str(token)
            
            expected_tokens = self.expected_tokens[previous_token_repr]
            if token_repr not in expected_tokens:
                raise Exception(
                    f'Unexpected token encountered -> {token_repr}.'
                    f'one of the following was expected -> {expected_tokens}'
                )
            
            token_list.append(token)
            previous_token_repr = token_repr

        return token_list
