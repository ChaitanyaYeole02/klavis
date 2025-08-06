# Walmart MCP Server

A Model Context Protocol (MCP) server for Walmart product search, store search, and category search functionality.

## Features

- **Product Search**: Search for Walmart products with filters for price, availability, and sorting
- **Store Search**: Find Walmart stores near a specific location
- **Category Search**: Browse Walmart product categories and subcategories

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file in the `mcp_servers/walmart/` directory:
   ```
   WALMART_API_KEY=your_walmart_api_key_here
   WALMART_MCP_SERVER_PORT=5000
   ```

3. **Get Walmart API Key**:
   - Sign up for Walmart API access at [Walmart Developer Portal](https://developer.walmart.com/)
   - Generate an API key for the Walmart Marketplace API

## Usage

### Running the Server

```bash
python server.py --port 5000 --log-level INFO
```

### Available Tools

#### 1. walmart_product_search
Search for Walmart products with various filters.

**Parameters**:
- `query` (required): The product search query
- `limit` (optional): Number of results (max 50, default 10)
- `offset` (optional): Pagination offset
- `sort` (optional): Sort order - 'relevance', 'price_low', 'price_high', 'rating', 'newest'
- `min_price` (optional): Minimum price filter
- `max_price` (optional): Maximum price filter
- `in_stock` (optional): Filter for in-stock items only
- `category_id` (optional): Filter by specific category ID

#### 2. walmart_store_search
Search for Walmart stores near a location.

**Parameters**:
- `location` (required): Location to search (zip code, city, or coordinates)
- `radius` (optional): Search radius in miles (default 25)
- `limit` (optional): Number of stores to return (max 20, default 10)

#### 3. walmart_category_search
Search for Walmart product categories.

**Parameters**:
- `query` (optional): Category name to search for
- `parent_id` (optional): Parent category ID to get subcategories
- `limit` (optional): Number of categories to return (max 50, default 20)

## API Endpoints

- **SSE**: `http://localhost:5000/sse`
- **StreamableHTTP**: `http://localhost:5000/mcp`
- **Health Check**: `http://localhost:5000/`

## Docker

Build and run with Docker:

```bash
docker build -t walmart-mcp-server .
docker run -p 5000:5000 --env-file .env walmart-mcp-server
```

## Error Handling

The server includes comprehensive error handling for:
- Missing API keys
- Network connectivity issues
- Invalid API responses
- Rate limiting

All errors are logged and returned in a structured format to the client. 