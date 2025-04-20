from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from app.api.routes import router as api_router
from app.config import Config

app = FastAPI(
    title="News Guy API",
    description="API for querying Fireship YouTube videos",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")


mcp = FastApiMCP(
    app,
    name="News Guy MCP Server",  # Name for your MCP server
    description="MCP server for News Guy API",  # Description
    base_url="http://localhost:8000",  # Where your API is running
    describe_all_responses=True,  # Include all possible response schemas
    describe_full_response_schema=True,  # Include full JSON schema in descriptions
)

# Mount the MCP server to your FastAPI app
mcp.mount()
