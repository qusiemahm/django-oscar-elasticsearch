from oscar.core.loading import get_model, get_class

from oscar_elasticsearch.search import settings
from server.apps.vendor.models import Vendor

chunked = get_class("search.utils", "chunked")
Product = get_model("catalogue", "Product")
Category = get_model("catalogue", "Category")

ProductElasticsearchIndex = get_class("search.api.product", "ProductElasticsearchIndex")
CategoryElasticsearchIndex = get_class(
    "search.api.category", "CategoryElasticsearchIndex"
)
VendorElasticsearchIndex = get_class("search.api.vendor", "VendorElasticsearchIndex")  # <-- your custom class


def update_index_vendor(vendor_id):
    """
    Update or create the specified vendor in the Elasticsearch index.
    """
    if isinstance(vendor_id, list):
        return update_index_vendors(vendor_id)  # Already a list, pass it directly
    return update_index_vendors([vendor_id])

def update_index_vendors(vendor_ids):
    """
    Bulk update or create the given vendor IDs.
    """
    for chunk in chunked(vendor_ids, settings.INDEXING_CHUNK_SIZE):
        vendors = Vendor.objects.filter(id__in=chunk)
        VendorElasticsearchIndex().update_or_create(vendors)

def update_index_category(category_id, update_products=True):
    update_index_categories([category_id])

    if update_products:
        product_ids = set(
            Product.objects.filter(categories__id=category_id).values_list(
                "pk", flat=True
            )
        )
        update_index_products(list(product_ids))


def update_index_categories(category_ids, update_products=True):
    for chunk in chunked(category_ids, settings.INDEXING_CHUNK_SIZE):
        categories = Category.objects.filter(id__in=chunk)
        CategoryElasticsearchIndex().update_or_create(categories)

    if update_products:
        product_ids = set(
            Product.objects.filter(categories__id__in=category_ids).values_list(
                "pk", flat=True
            )
        )
        update_index_products(list(product_ids))


def update_index_product(product_id):
    update_index_products([product_id])


def update_index_products(product_ids):
    for chunk in chunked(product_ids, settings.INDEXING_CHUNK_SIZE):
        products = Product.objects.filter(id__in=chunk)
        ProductElasticsearchIndex().update_or_create(products)
