import logging
import os
import warnings
from opensearchpy import OpenSearch
from sentence_transformers import SentenceTransformer
from adk_mcp_server.settings import settings

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        try:
            OS_HOST = os.environ["OPENSEARCH_HOST"]
            
            logger.info("Initializing RAG Service...")
            # Suppress the insecure request warning for local dev
            warnings.filterwarnings("ignore", "Unverified HTTPS request is being made")
            
            self.client = OpenSearch(
                hosts=[OS_HOST],
                http_auth=(os.environ["OPENSEARCH_USER"], os.environ["OPENSEARCH_PASSWORD"]),
                use_ssl=True,
                verify_certs=False,
                ssl_assert_hostname=False,
                ssl_show_warn=False,
            )
            if not self.client.ping():
                raise ConnectionError("Could not connect to OpenSearch from RAGService")

            self.model = SentenceTransformer(settings.opensearch.embedding_model_name)
            self.index_name = settings.opensearch.index_name
            logger.info("RAG Service initialized successfully.")
        except Exception as e:
            logger.critical(f"Failed to initialize RAG Service: {e}", exc_info=True)
            # In a real app, you might want a more robust way to handle this failure
            self.client = None
            self.model = None

    def search(self, query: str, top_k: int = 3) -> list[str]:
        """Searches for relevant documents in OpenSearch using vector similarity."""
        if not self.client or not self.model:
            logger.error("RAG Service is not available. Skipping search.")
            return []

        try:
            logger.info(f"Performing RAG search for query: '{query}'")
            query_embedding = self.model.encode(query)
            
            search_query = {
                "size": top_k,
                "query": {
                    "knn": {
                        "content_vector": {
                            "vector": query_embedding,
                            "k": top_k,
                        }
                    }
                },
            }
            response = self.client.search(index=self.index_name, body=search_query)
            
            # Extract the content from the search hits
            retrieved_chunks = [hit["_source"]["content"] for hit in response["hits"]["hits"]]
            logger.info(f"Retrieved {len(retrieved_chunks)} chunks from OpenSearch.")
            return retrieved_chunks
            
        except Exception as e:
            logger.error(f"An error occurred during OpenSearch search: {e}", exc_info=True)
            return []

# Create a singleton instance to be imported by other modules
rag_service = RAGService()