QUERY_TRANSFORMATION_PROMPT = """

You are an expert in query rewriting.

You need to transform the given query using the following instructions:-

1. Preserve original meaning.
2. Provide a clearer perspective
3. Keep the query concise
4. Do not invent new information
5. Do not answer the question
6. Return only the transformed query.

Query:
{query}

"""