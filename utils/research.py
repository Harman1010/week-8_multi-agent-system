from langchain_community.utilities import WikipediaAPIWrapper, DuckDuckGoSearchAPIWrapper

import arxiv

def search_wikipedia(query:str) -> str:

    try:
        wikipedia = WikipediaAPIWrapper()
        return wikipedia.run(query)

    except Exception as e:
        print(f"Wikipedia search failed: {e}")
        return "No Wikipedia information available."

import arxiv


def search_arxiv(query: str) -> str:

    try:
        client = arxiv.Client()

        search = arxiv.Search(
            query=query,
            max_results=3,
            sort_by=arxiv.SortCriterion.Relevance
        )

        results = client.results(search)

        papers = []

        for paper in results:

            papers.append(
                f"Title: {paper.title}\n"
                f"Summary: {paper.summary}"
            )

        if not papers:
            return "No relevant ArXiv information available."

        return "\n\n".join(papers)

    except Exception as e:
        print(f"ArXiv search failed: {e}")
        return "No ArXiv information available."

def search_duckduckgo(query:str) -> str:

    try:
        duckduckgo = DuckDuckGoSearchAPIWrapper()
        return duckduckgo.run(query)

    except Exception as e:
        print(f"Duckduckgo search failed: {e}")
        return "No Duckduckgo information available."