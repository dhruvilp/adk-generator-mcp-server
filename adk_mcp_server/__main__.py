import uvicorn

def run():
    """
    This function is the entry point for the uvicorn server.
    It's called by the script defined in `pyproject.toml`.
    """
    uvicorn.run(
        "adk_mcp_server.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True # Set to False in production for better performance
    )

if __name__ == "__main__":
    # This allows running the module directly using `python -m adk_mcp_server`
    run()