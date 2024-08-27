import os
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.document_loaders import FireCrawlLoader

from dotenv import load_dotenv

load_dotenv()

class SerperClient:
    """
    A client for performing Google searches using the Serper API.

    This client provides synchronous and asynchronous methods for performing Google searches
    and retrieving the search results.

    Attributes:
        None

    Methods:
        search(query, num_results): Perform a Google search for the given query and return the search results.
        search_async(query, num_results): Asynchronously perform a Google search for the given query and return the search results.
    """

    def __init__(self, serper_api_key: str = os.environ.get("SERPER_API_KEY")) -> None:
        self.serper_api_key = serper_api_key

    def search(
        self,
        query,
        num_results: int = 5,
    ):
        """
        Perform a Google search for the given query and return the search results.

        Args:
            query (str): The search query.
            num_results (int, optional): The number of search results to retrieve. Defaults to GOOGLE_SEARCH_DEFAULT_RESULT_COUNT.

        Returns:
            dict: The search results as a dictionary.

        """
        response = GoogleSerperAPIWrapper(k=num_results).results(query=query)
        # this is to make the response compatible with the response from the google search client
        items = response.pop("organic", [])
        response["items"] = items
        return response


class FireCrawlClient:

    def __init__(
        self, firecrawl_api_key: str = os.environ.get("FIRECRAWL_API_KEY")
    ) -> None:
        self.firecrawl_api_key = firecrawl_api_key

    def scrape(self, url):
        docs = FireCrawlLoader(
            api_key=self.firecrawl_api_key, url=url, mode="scrape"
        ).lazy_load()

        page_content = ""
        for doc in docs:
            page_content += doc.page_content

        # limit to 10,000 characters
        return page_content[:10000]
