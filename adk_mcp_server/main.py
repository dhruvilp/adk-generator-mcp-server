# adk_generator_mcp_server/main.py

import logging
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

from adk_mcp_server.settings import settings
from adk_mcp_server.tools import adk_generator # Import the tool module

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- App Initialization ---
logger.info("Initializing ADK Generator MCP Server...")

# Initialize the MCP server instance
mcp = FastMCP(
    settings.server_title,
    version=settings.server_version,
    # description=settings.server_description,
)

# Initialize the FastAPI app
app = FastAPI(
    title=settings.server_title,
    version=settings.server_version,
    # description=settings.server_description,
)

# --- Tool Registration ---
# This is where we attach our tools to the MCP instance.
# By calling the register_tool function from our module, we keep this file clean.
adk_generator.register_tool(mcp)
logger.info(f"Registered tool: '{adk_generator.TOOL_NAME}'")

# Mount the MCP application on the FastAPI app at the /mcp path
app.mount("/mcp", mcp)

@app.get("/", include_in_schema=False)
def root():
    """Root endpoint for basic health check and information."""
    return {
        "message": "ADK Generator MCP Server is running.",
        "mcp_tool_list_url": "/mcp/tools/list",
        "openapi_docs_url": "/docs"
    }