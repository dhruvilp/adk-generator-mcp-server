# ADK Agent Code Generator MCP

## Run OpenSearch Locally

```bash
docker run -it -p 9200:9200 -p 9600:9600 -e OPENSEARCH_INITIAL_ADMIN_PASSWORD=STRONG_PASSWORD -e "discovery.type=single-node"  --name opensearch-node opensearchproject/opensearch:latest
```


## Run the MCP Server

```bash

uv sync

uv pip install -e .

python scripts/seed_opensearch.py

start-server

#or

python -m adk_mcp_server

```

## Extra Deps

```bash

source /Users/dhruvilpatel/Documents/adk-generator-mcp-server/.venv/bin/activate && pip install --force-reinstall numpy==1.26.4

```

## Addding MCP Server

```json

"adkmcpserver": {
    "command": "python",
    "args": [
        "-m",
        "/../Documents/adk-generator-mcp-server"
    ]
}


```