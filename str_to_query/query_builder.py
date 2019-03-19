from .ast import build_ast
from .tokenizer import Tokenizer
from .builders import django_builder, dynamodb_builder, sql_alchemy

VALID_EXPORT_ORMS = {'django', 'dynamodb', 'sql_alchemy'}


class QueryBuilder:
    EXPORT_ORM_BUILDERS = {
        'django': django_builder,
        'dynamodb': dynamodb_builder,
        'sql_alchemy': sql_alchemy
    }

    def __init__(self, export_orm: str):
        if export_orm not in VALID_EXPORT_ORMS:
            raise Exception(f'P{export_orm} is not a valid export orm. Here\'s a list of the available ones -> {VALID_EXPORT_ORMS}')
        
        self.export_orm = export_orm
        self.builder = QueryBuilder.EXPORT_ORM_BUILDERS[export_orm]
        self.tokenizer = Tokenizer()

    def __call__(self, string: str):
        tokens = self.tokenizer(string)
        ast_head = build_ast(tokens)
        query = self.builder(ast_head)

        return query
