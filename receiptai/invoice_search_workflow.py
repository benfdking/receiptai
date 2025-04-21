import os
import logging

from langgraph.graph import StateGraph
from typing import TypedDict, Literal, Union, List, Dict
from gmail_service import GmailService
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

creds_file_path = os.environ.get('CREDS_FILE_PATH')
token_path = os.environ.get('TOKEN_JSON_PATH')

# Validate environment variables
if not creds_file_path:
    logger.error('CREDS_FILE_PATH environment variable is not set')
    raise ValueError('CREDS_FILE_PATH environment variable is required')

if not token_path:
    logger.error('TOKEN_JSON_PATH environment variable is not set')
    raise ValueError('TOKEN_JSON_PATH environment variable is required')

gmail_service = GmailService(creds_file_path, token_path)

class InvoiceInquiryItem(TypedDict):
    timestamp: str
    merchant_name: str
    id: str #invoice id
    amount: str
    currency: str

class SearchQueryItem(TypedDict):
    id: str
    query: str

class QueryResultItem(TypedDict):
    id: str
    result: Union[str, List[Dict[str, str]]]

class InvoiceSearchState(TypedDict, total=False):
    search_items: list[InvoiceInquiryItem]
    defined_queries: Union[None, list[SearchQueryItem]]
    query_results: Union[None, list[QueryResultItem]]


def _build_gmail_search_string(item: InvoiceInquiryItem) -> Union[str, SearchQueryItem]:
    """
    Builds a Gmail search string to find emails containing specific invoice details.

    Args:
        invoice: InvoiceInquiryItem containing invoice information

    Returns:
        String containing a Gmail search query

    Example:
        >>> invoice = InvoiceInquiryItem(
                timestamp="1995-06-24",
                merchant_name="some_merchant",
                id="00000000",
                amount="1000.00",
                currency="GBP"
            )
        >>> build_gmail_search_string(invoice)
    """

    if all(param is None or "" for param in [item["timestamp"], item["merchant_name"], item["id"], item["amount"], item["currency"]]):
        return ""

    search_terms = []

        # Add each value as a search term that could appear in either body or subject
    for key, value in item.items():
        if value:  # Only include non-empty values
            # Look for the exact value in either body or subject
            search_terms.append(f'(body:"{value}" OR subject:"{value}")')

    # Join all terms with OR operators (any of these values appearing is a match)
    search_string = " OR ".join(search_terms)


    return SearchQueryItem(id=item["id"], query=search_string)


def build_search_queries(state: InvoiceSearchState) -> InvoiceSearchState:
    new_state = state.copy()
    items = new_state.get("search_items", [])

    search_query_items = [_build_gmail_search_string(item) for item in items]
    queries = [item for item in search_query_items if not isinstance(item, str)]

    new_state["defined_queries"] = queries if queries else None

    return new_state

async def process_queries(state: InvoiceSearchState) -> InvoiceSearchState:
    new_state = state.copy()
    queries = new_state.get("defined_queries", [])


    if not queries:
        new_state["query_results"] = None
        return new_state

    query_results = [await _process_query(query) for query in queries if queries and  query is not None]
    results = [item for item in query_results if not isinstance(item, str)]

    new_state["query_results"] = results

    return new_state

async def _process_query(query: SearchQueryItem) -> Union[str, QueryResultItem]:
    # Simulate processing the query and return a result
    result = await gmail_service.search_emails(query['query'])
    if isinstance(result, str):
        return result

    return QueryResultItem(id=query["id"], result=result)


def display_result(state: InvoiceSearchState) -> InvoiceSearchState:
    new_state = state.copy()

    print(new_state)
    return new_state

# Define the routing logic for conditional paths
def router(state: InvoiceSearchState) -> Literal["process_queries", "short_circuit"]:
    """Decide the next node based on user input"""
    defined_queries = state.get("defined_queries", None)
    if defined_queries:
        return "process_queries"
    else:
        print("No queries defined")
        return "short_circuit"

# Create the workflow graph with state schema
workflow = StateGraph(state_schema=InvoiceSearchState)

# Add nodes to the graph
workflow.add_node("build_search_queries", build_search_queries)
workflow.add_node("process_queries", process_queries)
workflow.add_node("display_result", display_result)
#

# Connect nodes with edges
# workflow.add_edge("build_search_queries", "process_queries")

# Set the entry point of the graph
workflow.set_entry_point("build_search_queries")

workflow.add_conditional_edges(
    "build_search_queries",
    router,
    {
        "process_queries": "process_queries",
        "short_circuit": "display_result"
    }
)

workflow.add_edge("process_queries", "display_result")




# Compile the graph
app = workflow.compile()

# Initialize state and run the graph
initial_state: InvoiceSearchState = {
    "search_items": [
        {
            "timestamp": "2023-05-20",
            "merchant_name": "Widget Industries",
            "id": "WI-9982-B",
            "amount": "499.50",
            "currency": "EUR"
        },
        {
            "timestamp": "2023-06-07",
            "merchant_name": "TechGadgets Inc",
            "id": "TG-2023-1187",
            "amount": "899.95",
            "currency": "USD"
        }
    ]
}

import asyncio
result = asyncio.run(app.ainvoke(initial_state))


# TODO(jimmy): Continue here
# - add model assert email body and download if needed
# - include model calling step
# - add cmd client
