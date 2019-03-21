# String to Query

string_to_query is a plug and play string to query converter for multiple ORMs. It's an easy to use, fast and robust solution for building queries out of strings for your preferred ORM.


# Usage

from query_to_string.query_builder import QueryBuilder

query_builder = QueryBuilder('django')

string = "((field_a__lt:int:100)OR(field_b__contains:test))AND(field_c:bool:0)"

query = query_builder(string)

YourModel.objects.filter(query)



# Use cases

* It isn't easy to build queries through get requests since you're limited to query strings. Using string_to_query you'll be able to make complex queries in your backend from a client seamlessly.
* Any other situation where you want to build complex queries from a client where you're limited to use strings as your communication method.

