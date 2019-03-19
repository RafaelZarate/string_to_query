from .tokenizer import Tokenizer
from .ast import build_ast
from .builders import django_builder, dynamodb_builder, sql_alchemy

VALID_EXPORT_ORMS = {'django', 'dynamodb', 'sql_alchemy'}

class QueryBuilder:
    def __init__(self, export_orm: str):
        if export_orm not in VALID_EXPORT_ORMS:
            raise Exception(f'P{export_orm} is not a valid export orm. Here\'s a list of the available ones -> {VALID_EXPORT_ORMS}')
        
        export_orm_to_builder = {
            'django': django_builder,
            'dynamodb': dynamodb_builder,
            'sql_alchemy': sql_alchemy
        }
        self.export_orm = export_orm
        self.builder = export_orm_to_builder[export_orm]
        self.tokenizer = Tokenizer()

    
    def __call__(self, string: str):
        tokens = self.tokenizer(string)
        ast_head = build_ast(tokens)
        query = self.builder(ast_head)

        return query