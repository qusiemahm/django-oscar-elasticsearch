import os
from django.core.management.base import BaseCommand
from server.apps.vendor.models import Vendor
from oscar.core.loading import get_class
from elasticsearch import Elasticsearch
from django.conf import settings

# Load Oscar Elasticsearch Indexing utilities
VendorElasticsearchIndex = get_class("search.api.vendor", "VendorElasticsearchIndex")  # Load ES index class
chunked = get_class("search.utils", "chunked")

# Fetch Elasticsearch Credentials from Environment Variables
ELASTICSEARCH_URL = getattr(settings, "ELASTICSEARCH_URL", "")
ELASTICSEARCH_USER = getattr(settings, "ELASTICSEARCH_USER", "elastic")
ELASTIC_PASSWORD = getattr(settings, "ELASTIC_PASSWORD", "")
print()
# Create Elasticsearch Client with Authentication
es = Elasticsearch(
    hosts=[ELASTICSEARCH_URL],
    http_auth=(ELASTICSEARCH_USER, ELASTIC_PASSWORD),
    verify_certs=True,  # Set to True if using a valid SSL cert
    timeout=60,  # Increase timeout to 60 seconds
    max_retries=5,  # Retry up to 5 times
    retry_on_timeout=True
)

class Command(BaseCommand):
    help = "Index vendors in Elasticsearch"
    print("credit: ", ELASTICSEARCH_URL, ELASTICSEARCH_USER, ELASTIC_PASSWORD)

    def add_arguments(self, parser):
        parser.add_argument(
            "vendor_ids", nargs="*", type=int, help="Vendor ID(s) to index"
        )

    def handle(self, *args, **options):
        vendor_ids = options["vendor_ids"]

        if not vendor_ids:
            self.stdout.write(self.style.WARNING("No vendor IDs provided. Indexing all vendors."))
            vendors = Vendor.objects.all()  # Index all vendors if none are specified
        else:
            vendors = Vendor.objects.filter(id__in=vendor_ids)

        if not vendors.exists():
            self.stdout.write(self.style.WARNING("No matching vendors found."))
            return

        # Ensure Elasticsearch connection is valid
        if not es.ping():
            self.stdout.write(self.style.ERROR("Elasticsearch connection failed. Check credentials and server status."))
            return

        try:
            for chunk in chunked(vendors.values_list("id", flat=True), 100):  # Process in chunks of 100
                vendor_objects = Vendor.objects.filter(id__in=chunk)
                VendorElasticsearchIndex().update_or_create(vendor_objects)

            self.stdout.write(self.style.SUCCESS(f"Indexed {vendors.count()} vendors successfully."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error indexing vendors: {e}"))
