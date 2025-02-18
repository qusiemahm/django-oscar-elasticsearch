from elasticsearch import Elasticsearch
from oscar_elasticsearch.search.settings import ELASTICSEARCH_SERVER_URLS
import os

# Fetch credentials from environment variables or settings
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "")
ELASTICSEARCH_USER = os.getenv("ELASTICSEARCH_USER", "")  # Replace with actual username
ELASTICSEARCH_PASSWORD = os.getenv("ELASTIC_PASSWORD", "")  # Replace with actual password

# Create Elasticsearch client with authentication
es = Elasticsearch(
    hosts=[ELASTICSEARCH_URL],
    http_auth=(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD),
    verify_certs=False,  # Change to True if using a valid SSL cert
    timeout=60,  # Increase timeout to 60 seconds
    max_retries=5,  # Retry up to 5 times
    retry_on_timeout=True
)
