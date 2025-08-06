import logging

from typing import Any, Dict, Optional

import requests

from .base import get_walmart_client

# Configure logging
logger = logging.getLogger(__name__)

async def walmart_product_search(
    query: str,
    limit: int = 10,
    offset: int = 0,
    sort: str = "relevance",
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    category_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for Walmart products.

    Args:
        query (str): [Required] The product search query.
        limit (int): Number of results to return (max 50, default 10).
        offset (int): Zero-based offset for pagination.
        sort (str): Sort order - 'relevance', 'price_low', 'price_high', 'rating', 'newest'.
        min_price (float): Minimum price filter.
        max_price (float): Maximum price filter.
        in_stock (bool): Filter for in-stock items only.
        category_id (str): Filter by specific category ID.
    Returns:
        dict: JSON response with product search results.
    """
    token = get_walmart_client()
    if not token:
        logger.error("Could not get Walmart API token")
        return {"error": "Missing Walmart API token"}

    url = "https://api.walmart.com/v3/items/search"
    headers = {
        "Accept": "application/json",
        "WM_SEC.ACCESS_TOKEN": token,
        "WM_QOS.CORRELATION_ID": "walmart-mcp-server"
    }

    # Build query parameters
    params = {
        "query": query,
        "limit": min(limit, 50),
        "offset": offset
    }

    # Add optional parameters
    if sort and sort != "relevance":
        params["sort"] = sort
    if min_price is not None:
        params["minPrice"] = min_price
    if max_price is not None:
        params["maxPrice"] = max_price
    if in_stock is not None:
        params["inStock"] = in_stock
    if category_id:
        params["categoryId"] = category_id

    logger.info(f"Sending Walmart product search request: {query}")
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        logger.info("Received Walmart product search response")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Walmart product search failed: {e}")
        return {"error": f"Could not complete Walmart product search for query: {query}"}
    except Exception as e:
        logger.error(f"Unexpected error in Walmart product search: {e}")
        return {"error": f"Unexpected error in Walmart product search: {str(e)}"}

async def walmart_store_search(
    location: str,
    radius: int = 25,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Search for Walmart stores near a location.

    Args:
        location (str): [Required] Location to search (zip code, city, or coordinates).
        radius (int): Search radius in miles (default 25).
        limit (int): Number of stores to return (max 20, default 10).
    Returns:
        dict: JSON response with store search results.
    """
    token = get_walmart_client()
    if not token:
        logger.error("Could not get Walmart API token")
        return {"error": "Missing Walmart API token"}

    url = "https://api.walmart.com/v3/stores"
    headers = {
        "Accept": "application/json",
        "WM_SEC.ACCESS_TOKEN": token,
        "WM_QOS.CORRELATION_ID": "walmart-mcp-server"
    }

    # Build query parameters
    params = {
        "location": location,
        "radius": radius,
        "limit": min(limit, 20)
    }

    logger.info(f"Sending Walmart store search request for location: {location}")
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        logger.info("Received Walmart store search response")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Walmart store search failed: {e}")
        return {"error": f"Could not complete Walmart store search for location: {location}"}
    except Exception as e:
        logger.error(f"Unexpected error in Walmart store search: {e}")
        return {"error": f"Unexpected error in Walmart store search: {str(e)}"}

async def walmart_category_search(
    query: Optional[str] = None,
    parent_id: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Search for Walmart product categories.

    Args:
        query (str): Optional. Category name to search for.
        parent_id (str): Optional. Parent category ID to get subcategories.
        limit (int): Number of categories to return (max 50, default 20).
    Returns:
        dict: JSON response with category search results.
    """
    token = get_walmart_client()
    if not token:
        logger.error("Could not get Walmart API token")
        return {"error": "Missing Walmart API token"}

    # Determine the appropriate endpoint based on parameters
    if parent_id:
        url = f"https://api.walmart.com/v3/items/categories/{parent_id}"
    else:
        url = "https://api.walmart.com/v3/items/categories"

    headers = {
        "Accept": "application/json",
        "WM_SEC.ACCESS_TOKEN": token,
        "WM_QOS.CORRELATION_ID": "walmart-mcp-server"
    }

    # Build query parameters
    params = {
        "limit": min(limit, 50)
    }

    if query:
        params["query"] = query

    logger.info(f"Sending Walmart category search request")
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        logger.info("Received Walmart category search response")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Walmart category search failed: {e}")
        return {"error": f"Could not complete Walmart category search"}
    except Exception as e:
        logger.error(f"Unexpected error in Walmart category search: {e}")
        return {"error": f"Unexpected error in Walmart category search: {str(e)}"} 