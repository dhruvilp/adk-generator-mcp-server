import logging
import os
import warnings
from pathlib import Path
from opensearchpy import OpenSearch, helpers
from sentence_transformers import SentenceTransformer
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

INDEX_NAME = "adk-docs-index"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OS_HOST = os.environ["OPENSEARCH_HOST"]

def create_opensearch_client():
    """Creates and returns an OpenSearch client instance."""
    logging.info(f"Connecting to OpenSearch at {OS_HOST}")
    client = OpenSearch(
        hosts=[OS_HOST],
        http_auth=(os.environ["OPENSEARCH_USER"], os.environ["OPENSEARCH_PASSWORD"]),
        use_ssl=True,
        verify_certs=False,  # In production, set to True with a valid cert
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )
    if not client.ping():
        raise ConnectionError("Could not connect to OpenSearch")
    logging.info("Successfully connected to OpenSearch.")
    return client

def create_index(client: OpenSearch, model: SentenceTransformer):
    """Creates the OpenSearch index with the correct mapping for k-NN search."""
    if client.indices.exists(index=INDEX_NAME):
        logging.warning(f"Index '{INDEX_NAME}' already exists. Deleting and recreating.")
        client.indices.delete(index=INDEX_NAME)

    embedding_dim = model.get_sentence_embedding_dimension()
    index_body = {
        "settings": {"index": {"knn": True, "knn.algo_param.ef_search": 100}},
        "mappings": {
            "properties": {
                "content": {"type": "text"},
                "content_vector": {
                    "type": "knn_vector",
                    "dimension": embedding_dim,
                    "method": {"name": "hnsw", "space_type": "l2", "engine": "lucene"}, # or faiss
                },
            }
        },
    }
    client.indices.create(index=INDEX_NAME, body=index_body)
    logging.info(f"Index '{INDEX_NAME}' created successfully with embedding dimension {embedding_dim}.")

def load_and_chunk_docs():
    """Loads documents from the /docs directory and chunks them."""
    docs_path = Path(__file__).resolve().parents[1] / "docs"
    chunks = []
    for doc_file in docs_path.glob("*.md"):
        logging.info(f"Processing document: {doc_file.name}")
        content = doc_file.read_text()
        # Simple chunking by splitting on a separator
        chunks.extend(p.strip() for p in content.split("---") if p.strip())
    logging.info(f"Loaded {len(chunks)} chunks from documents.")
    return chunks

def generate_actions(chunks: list[str], model: SentenceTransformer):
    """Yields bulk-indexing actions for each chunk."""
    for chunk in chunks:
        embedding = model.encode(chunk)
        yield {
            "_index": INDEX_NAME,
            "_source": {
                "content": chunk,
                "content_vector": embedding,
            },
        }

def main():
    """Main function to run the seeding process."""
    logging.info("Starting OpenSearch data seeding process...")
    try:
        # Suppress the insecure request warning for local dev
        warnings.filterwarnings("ignore", "Unverified HTTPS request is being made")

        client = create_opensearch_client()
        model = SentenceTransformer(EMBEDDING_MODEL)

        create_index(client, model)
        chunks = load_and_chunk_docs()

        logging.info("Generating embeddings and indexing documents...")
        success, failed = helpers.bulk(client, generate_actions(chunks, model))
        logging.info(f"Successfully indexed {success} documents.")
        if failed:
            logging.error(f"Failed to index {len(failed)} documents.")

    except Exception as e:
        logging.critical(f"An error occurred during the seeding process: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()