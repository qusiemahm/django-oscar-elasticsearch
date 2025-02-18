# server/apps/vendor/management/commands/update_vendor_index.py
from django.core.management.base import BaseCommand
from server.apps.vendor.models import Vendor
from oscar.core.loading import get_class

VendorElasticsearchIndex = get_class("search.api.vendor", "VendorElasticsearchIndex")  # Load ES index class
chunked = get_class("search.utils", "chunked")

class Command(BaseCommand):
    help = "Index vendors in Elasticsearch"

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

        for chunk in chunked(vendors.values_list("id", flat=True), 100):  # Chunked processing
            vendor_objects = Vendor.objects.filter(id__in=chunk)
            VendorElasticsearchIndex().update_or_create(vendor_objects)

        self.stdout.write(self.style.SUCCESS(f"Indexed {vendors.count()} vendors."))
