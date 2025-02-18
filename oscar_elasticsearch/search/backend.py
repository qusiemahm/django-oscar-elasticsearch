from elasticsearch import Elasticsearch
from oscar_elasticsearch.search.settings import ELASTICSEARCH_SERVER_URLS
import os
from django.conf import settings

# Fetch credentials from environment variables or settings
ELASTICSEARCH_URL = getattr(settings, "ELASTICSEARCH_URL", "")
ELASTICSEARCH_USER = getattr(settings, "ELASTICSEARCH_USER", "elastic")
ELASTIC_PASSWORD = getattr(settings, "ELASTIC_PASSWORD", "")

# Create Elasticsearch client with authentication
es = Elasticsearch(
    hosts=[ELASTICSEARCH_URL],
    http_auth=(ELASTICSEARCH_USER, ELASTIC_PASSWORD),
    verify_certs=True,  # Change to True if using a valid SSL cert
    timeout=60,  # Increase timeout to 60 seconds
    max_retries=5,  # Retry up to 5 times
    retry_on_timeout=True
)
